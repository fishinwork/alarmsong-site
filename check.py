# -*- coding: utf-8 -*-
"""Проверка сайта перед выкладкой. Запускать из корня репозитория:

    python check.py

Смотрит не на одну страницу, а на одинаковое на всех. Так ловится ровно то,
что глазами не видно: 25.09 правка шапки скриптом убрала кнопку «Get the app»
с одной страницы из десяти, и обе проверки глазами её пропустили — смотрели на
ту же страницу, где и сломали.

Ничего не чинит и никуда не ходит по сети: читает файлы и считает.
Возвращает 1, если что-то не сошлось, — можно ставить в хук перед push.
"""
import json
import os
import re
import sys

PAGES = sorted(f for f in os.listdir('.') if f.endswith('.html'))
BEACON = 'static.cloudflareinsights.com'
bad = []


def read(name):
    with open(name, encoding='utf-8') as f:
        return f.read()


def one_per_page(what, count):
    """Одно и то же должно быть на каждой странице ровно один раз."""
    for page in PAGES:
        n = count(read(page))
        if n != 1:
            bad.append('%s: %s — %d, а надо 1' % (page, what, n))


def in_nav(html):
    m = re.search(r'<nav aria-label="Site">.*?</nav>', html, re.S)
    return m.group(0) if m else ''


# ── одинаковое на всех страницах ─────────────────────────────────────────
one_per_page('кнопка «Get the app» в меню', lambda h: in_nav(h).count('btn btn-main'))
one_per_page('переключатель темы', lambda h: h.count('class="themes"'))
one_per_page('theme.js', lambda h: h.count('/theme.js'))
one_per_page('слой неба', lambda h: h.count('class="sky"'))
one_per_page('дальний слой', lambda h: h.count('class="far"'))
one_per_page('ближний слой', lambda h: h.count('class="near"'))
one_per_page('счётчик', lambda h: h.count(BEACON))
one_per_page('общий стиль', lambda h: h.count('href="/style.css"'))
one_per_page('атрибуция DB-IP', lambda h: h.count('db-ip.com'))

# ── адреса страниц ───────────────────────────────────────────────────────
for page in PAGES:
    html = read(page)
    canon = re.findall(r'<link rel="canonical" href="([^"]+)"', html)
    if page == '404.html':
        if canon:
            bad.append('404.html: canonical не нужен, страница закрыта от поиска')
        if 'name="robots" content="noindex"' not in html:
            bad.append('404.html: нет noindex')
    elif len(canon) != 1:
        bad.append('%s: canonical — %d, а надо 1' % (page, len(canon)))

    title = re.search(r'<title>(.*?)</title>', html, re.S)
    desc = re.search(r'<meta name="description" content="(.*?)">', html, re.S)
    if not title or len(title.group(1).strip()) > 60:
        bad.append('%s: заголовок длиннее 60 знаков или его нет' % page)
    if not desc or len(desc.group(1).strip()) > 155:
        bad.append('%s: описание длиннее 155 знаков или его нет' % page)

# ── ничего русского в том, что отдаётся посетителю ──────────────────────
served = PAGES + ['style.css', 'theme.js', 'favicon.svg', 'robots.txt',
                  'sitemap.xml', 'site.webmanifest']
for name in served:
    if os.path.exists(name):
        n = len(re.findall(r'[А-Яа-яЁё]', read(name)))
        if n:
            bad.append('%s: %d русских букв — репозиторий публичный' % (name, n))

# ── все местные ссылки и картинки существуют ────────────────────────────
for page in PAGES:
    html = read(page)
    for url in set(re.findall(r'(?:href|src)="(/[^"#?]*)"', html)):
        path = url.lstrip('/')
        if not path:
            path = 'index.html'
        elif '.' not in os.path.basename(path):
            path += '.html'          # короткие адреса отдаёт GitHub Pages
        if not os.path.exists(path):
            bad.append('%s: ссылка %s ведёт в никуда' % (page, url))

# ── карта сайта совпадает со страницами ─────────────────────────────────
if os.path.exists('sitemap.xml'):
    listed = set(re.findall(r'<loc>https://alarmsong\.com/([^<]*)</loc>', read('sitemap.xml')))
    should = {p[:-5] for p in PAGES if p not in ('404.html', 'index.html')} | {''}
    for miss in sorted(should - listed):
        bad.append('карта сайта: нет %s' % (miss or '/'))
    for extra in sorted(listed - should):
        bad.append('карта сайта: лишний %s' % extra)

# ── вопросы в разметке совпадают с видимыми ─────────────────────────────
home = read('index.html')
block = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', home, re.S)
if block:
    try:
        data = json.loads(block.group(1))
        faq = [x for x in data.get('@graph', []) if x.get('@type') == 'FAQPage']
        if faq:
            marked = [q['name'].strip() for q in faq[0]['mainEntity']]
            visible = [re.sub(r'<[^>]+>', '', v).strip()
                       for v in re.findall(r'<summary>(.*?)</summary>', home, re.S)]
            if marked != visible:
                bad.append('вопросы в разметке разошлись с видимыми на странице')
    except json.JSONDecodeError as e:
        bad.append('разметка на главной не разбирается как JSON: %s' % e)

# ── итог ────────────────────────────────────────────────────────────────
if bad:
    print('Не сошлось:')
    for line in bad:
        print('  -', line)
    sys.exit(1)

print('Всё сошлось: страниц %d, одинаковое на всех на месте.' % len(PAGES))
