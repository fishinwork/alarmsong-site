# -*- coding: utf-8 -*-
"""Печём картинки сайта из одного знака.

Источник один: brand/mark.svg. Отсюда получаются фавиконки, иконка для
телефона и картинка для ссылок. Рисовать что-то из этого руками нельзя —
две копии знака разойдутся за неделю, ровно как разошлись бы две копии
страниц. Тот же приём, что и с небом приложения (tools/bake_sky.py).

Запускать на компьютере, где есть Chrome:

    python brand/bake.py

Готовые файлы лежат в репозитории, поэтому обычно запускать не нужно —
только когда меняется сам знак.
"""
import io
import os
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BROWSERS = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    '/usr/bin/chromium', '/usr/bin/google-chrome',
]

# Что печём: имя файла → сторона квадрата.
SQUARES = {
    'apple-touch-icon.png': 180,   # плитка на домашнем экране айфона
    'icon-192.png': 192,           # манифест, Android
    'icon-512.png': 512,           # манифест, витрины
}
ICO_SIZES = [16, 32, 48]           # что кладём внутрь favicon.ico



def write_ico(path, blobs):
    """Собираем .ico из готовых PNG — по кадру на размер.

    Внутри .ico со времён Windows Vista можно хранить PNG как есть, и все
    живые браузеры это понимают. Так каждый размер остаётся таким, каким его
    нарисовал браузер, а не ужатым из большого.
    """
    count = len(blobs)
    head = struct.pack('<HHH', 0, 1, count)
    offset = 6 + 16 * count
    entries, body = [], []
    for size, data in blobs:
        entries.append(struct.pack('<BBBBHHII',
                                   size if size < 256 else 0,
                                   size if size < 256 else 0,
                                   0, 0, 1, 32, len(data), offset))
        body.append(data)
        offset += len(data)
    io.open(path, 'wb').write(head + b''.join(entries) + b''.join(body))


def browser():
    for path in BROWSERS:
        if os.path.exists(path):
            return path
    sys.exit('Не нашёл ни Chrome, ни Edge — печь нечем.')


def shoot(html_path, width, height, out_png, chrome):
    """Снимок страницы ровно в заданном размере."""
    tmp = tempfile.mkdtemp(prefix='alarmsong-bake-')
    try:
        subprocess.run([
            chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars',
            '--force-device-scale-factor=1', f'--user-data-dir={tmp}',
            f'--window-size={width},{height}',
            f'--screenshot={out_png}',
            pathlib.Path(html_path).resolve().as_uri(),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def page_for_mark(size):
    """Обёртка вокруг знака: ни полей, ни полос прокрутки."""
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<style>html,body{margin:0;padding:0;background:transparent;overflow:hidden}'
        'img{display:block}</style></head><body>'
        f'<img src="mark.svg" width="{size}" height="{size}"></body></html>'
    )


def main():
    chrome = browser()
    wrapper = os.path.join(HERE, '_wrap.html')
    made = []

    # 1. Квадратные иконки — каждая рисуется в своём размере, а не ужимается
    #    из большой: у мелких так остаются чёткими полосы волны.
    for name, size in SQUARES.items():
        open(wrapper, 'w', encoding='utf-8').write(page_for_mark(size))
        out = os.path.join(ROOT, name)
        shoot(wrapper, size, size, out, chrome)
        Image.open(out).convert('RGB').save(out)   # без альфы: Apple не любит прозрачность
        made.append(name)

    # 2. favicon.ico — три размера внутри одного файла, для старых браузеров.
    #    Каждый снят в своём размере: Pillow при сохранении ICO ужимает всё из
    #    одной картинки и кладёт внутрь только её, поэтому склеиваем сами.
    blobs = []
    for size in ICO_SIZES:
        open(wrapper, 'w', encoding='utf-8').write(page_for_mark(size))
        png = os.path.join(HERE, f'_ico_{size}.png')
        shoot(wrapper, size, size, png, chrome)
        blobs.append((size, io.open(png, 'rb').read()))
    ico = os.path.join(ROOT, 'favicon.ico')
    write_ico(ico, blobs)
    made.append('favicon.ico')

    # 3. Картинка для ссылок — отдельная страница, знак плюс подпись.
    #    Держим её легче двухсот килобайт: мессенджеры тяжёлую просто не
    #    показывают, и ссылка приходит мёртвой. 256 цветов с размытием —
    #    на глаз то же самое, весит вдвое меньше.
    og = os.path.join(ROOT, 'og.png')
    shoot(os.path.join(HERE, 'og.html'), 1200, 630, og, chrome)
    picture = Image.open(og).convert('RGB').quantize(
        colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
    picture.save(og, 'PNG', optimize=True)
    if os.path.getsize(og) > 200 * 1024:
        print('ВНИМАНИЕ: og.png тяжелее 200 КБ, ссылка может прийти без картинки')
    made.append('og.png')

    for junk in [wrapper] + [os.path.join(HERE, f'_ico_{s}.png') for s in ICO_SIZES]:
        if os.path.exists(junk):
            os.remove(junk)

    # 4. Знак как есть — для браузеров, которые умеют SVG на вкладке.
    shutil.copyfile(os.path.join(HERE, 'mark.svg'), os.path.join(ROOT, 'favicon.svg'))
    made.append('favicon.svg')

    for name in made:
        path = os.path.join(ROOT, name)
        print(f'{name:<22} {os.path.getsize(path):>8} байт')


if __name__ == '__main__':
    main()
