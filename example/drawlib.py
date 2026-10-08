"""Minimal drawing primitives for the frame renderer.

Font resolution order:
  1. $EXPLAINER_FONT (absolute path)
  2. assets/NotoSansCJKkr-Regular.otf next to this file
  3. any .otf/.ttf in assets/

Never hard-code a font you cannot license; see assets/README.md.
"""
import os
import pathlib
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
BG = '#101923'
GRID = '#1a2835'
FG = '#edf3f5'
MUTED = '#9cabb8'
TEAL = '#51dccb'
YELLOW = '#f3ce62'
RED = '#f08080'
BLUE = '#7caff2'
EDGE = '#395466'
PURPLE = '#b19ce9'


def font_path():
    env = os.environ.get('EXPLAINER_FONT')
    if env and pathlib.Path(env).is_file():
        return pathlib.Path(env)
    named = ROOT / 'assets' / 'NotoSansCJKkr-Regular.otf'
    if named.is_file():
        return named
    found = sorted(p for p in (ROOT / 'assets').glob('*') if p.suffix.lower() in ('.otf', '.ttf')) if (ROOT / 'assets').is_dir() else []
    if found:
        return found[0]
    raise FileNotFoundError(
        'No font found. Put an OFL/CJK font at assets/NotoSansCJKkr-Regular.otf, '
        'or set EXPLAINER_FONT=/abs/path/font.otf')


FONT_PATH = font_path()


@lru_cache(maxsize=25)
def f(size):
    return ImageFont.truetype(str(FONT_PATH), size)


@lru_cache(maxsize=600)
def tile(s, size, col):
    box = f(size).getbbox(s)
    im = Image.new('RGBA', (int(box[2] - box[0] + 4), size * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2, -box[1]), s, font=f(size), fill=col)
    return im.crop((0, 0, im.width, box[3] - box[1] + 3))


def text(im, xy, s, size=24, col=FG, center=False):
    a = tile(str(s), size, col)
    x, y = xy
    if center:
        x -= a.width / 2
    im.paste(a, (round(x), round(y)), a)


def clamp(x):
    return min(1, max(0, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def mix(a, b, q):
    return a + (b - a) * q


def line(d, a, b, col=EDGE, width=3):
    d.line([a, b], fill=col, width=width)


def dot(d, xy, r=6, col=TEAL):
    x, y = xy
    d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def flow(d, a, b, t, col=TEAL, offset=0., count=3, rate=.23):
    line(d, a, b)
    for n in range(count):
        u = (t * rate + offset + n / count) % 1
        dot(d, (mix(a[0], b[0], u), mix(a[1], b[1], u)), 5, col)


def curve_flow(d, points, t, col=TEAL, count=4):
    d.line(points, fill=EDGE, width=3)
    for n in range(count):
        u = (t * .17 + n / count) % 1
        i = min(len(points) - 2, int(u * (len(points) - 1)))
        q = u * (len(points) - 1) - i
        dot(d, (mix(points[i][0], points[i + 1][0], q), mix(points[i][1], points[i + 1][1], q)), 5, col)


def node(im, d, xy, label='', col=TEAL, r=25, size=22):
    """Circle node with a knockout label below it."""
    x, y = xy
    d.ellipse((x - r - 5, y - r - 5, x + r + 5, y + r + 5), outline=EDGE, width=2)
    d.ellipse((x - r, y - r, x + r, y + r), fill=BG, outline=col, width=3)
    if label:
        a = tile(str(label), size, col)
        left = x - a.width / 2
        top = y + r + 12
        d.rounded_rectangle((left - 4, top - 2, left + a.width + 4, top + a.height + 2), radius=3, fill=BG)
        text(im, (x, top), label, size, col, True)


def arrow(d, a, b, col=TEAL, width=3):
    line(d, a, b, col, width)
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    n = 12
    d.polygon([b,
               (b[0] - n * math.cos(angle - .5), b[1] - n * math.sin(angle - .5)),
               (b[0] - n * math.cos(angle + .5), b[1] - n * math.sin(angle + .5))], fill=col)


def box(im, d, rect, label, col=TEAL, size=23):
    d.rounded_rectangle(rect, radius=9, fill=BG, outline=col, width=2)
    text(im, ((rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2 - size / 2), label, size, col, True)


def caption_lines(s, max_width=1150, size=26):
    """Wrap at real pixel width, caller must assert len(lines) <= 2."""
    lines = []
    cur = ''
    for word in str(s).split():
        trial = (cur + ' ' + word).strip()
        if f(size).getlength(trial) > max_width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def morph_points(start_rect, end_circle, n=128, t=0.0):
    """One shape moving between a rectangle and a circle with a fixed correspondence.

    Both states are sampled to the same vertex count so the viewer reads one object
    changing meaning rather than two shapes swapping.
    """
    x0, y0, x1, y1 = start_rect
    rect = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    seg = [math.dist(rect[i], rect[i + 1]) for i in range(4)]
    total = sum(seg)
    pts = []
    for k in range(n):
        target = total * k / n
        acc = 0.0
        for i in range(4):
            if acc + seg[i] >= target or i == 3:
                q = (target - acc) / seg[i] if seg[i] else 0.0
                pts.append((mix(rect[i][0], rect[i + 1][0], q), mix(rect[i][1], rect[i + 1][1], q)))
                break
            acc += seg[i]
    cx, cy, r = end_circle
    circle = [(cx + r * math.cos(math.tau * k / n), cy + r * math.sin(math.tau * k / n)) for k in range(n)]
    return [(mix(a[0], b[0], t), mix(a[1], b[1], t)) for a, b in zip(pts, circle)]
