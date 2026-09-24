# AlarmSong — the public site

The pages behind [alarmsong.com](https://alarmsong.com): home, support,
privacy, terms and account deletion. Served by GitHub Pages from `main`,
straight out of the repository root. The domain lives in `CNAME`; HTTPS is
issued and enforced.

Plain HTML and one stylesheet. No build step, no framework, nothing to install
before editing a page.

| What | Where |
|---|---|
| Look of every page | `style.css` |
| The mark everything is drawn from | `brand/mark.svg` |
| Baker for favicons and the link preview | `python brand/bake.py` |

## Look at it locally

```
python -m http.server 8787 --directory .
```

Open `http://localhost:8787/index.html`. The short addresses (`/support` and
friends) are GitHub Pages' doing and do not work locally — open the `.html`
file instead.

## Redraw the images

Only when the mark itself changes. Needs Chrome (or Edge) and Pillow:

```
python brand/bake.py
```

`brand/mark.svg` becomes `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`,
`icon-192.png`, `icon-512.png` and `og.png`. None of those are drawn by hand —
two copies of a mark drift apart within a week.

## Before calling a change done

Check at 320, 375 and desktop width, in both light and dark, and make sure
nothing is clipped and nothing scrolls sideways.
