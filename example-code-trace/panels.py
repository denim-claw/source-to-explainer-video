"""Panel geometry: reject overflow rather than clipping values or shrinking fonts."""
import json

from PIL import ImageDraw
from drawlib import BG, EDGE, FG, MUTED, TEAL, f, text, tile

CODE_RECT = (40, 190, 840, 590)
VALUE_RECT = (865, 190, 1240, 590)


def panel(im, rect, title):
    ImageDraw.Draw(im).rounded_rectangle(rect, radius=10, fill=BG, outline=EDGE, width=2)
    text(im, (rect[0] + 16, rect[1] + 12), title, 19, TEAL)


def checked_text(im, rect, point, label, size, color=FG):
    width, height = tile(label, size, color).size
    x, y = point
    assert rect[0] + 8 <= x and x + width <= rect[2] - 8, ('horizontal overflow', label)
    assert rect[1] + 8 <= y and y + height <= rect[3] - 8, ('vertical overflow', label)
    text(im, point, label, size, color)
    return {'kind': 'text', 'text': label, 'box': [x, y, x + width, y + height]}


def wrap_value(label, width, size=19):
    # JSON strings/identifiers may contain no spaces: wrap by measured glyph width.
    rows, row = [], ''
    for char in label:
        if f(size).getlength(row + char) > width and row:
            rows.append(row)
            row = ''
        row += char
    if row:
        rows.append(row)
    return rows


def values(im, value_map, illustrative=False):
    panel(im, VALUE_RECT, 'VALUES · illustrative input' if illustrative else 'VALUES · before highlighted line')
    rectangles, y = [], 242
    for name, value in value_map.items():
        label = name + ' = ' + json.dumps(value, ensure_ascii=False)
        for row in wrap_value(label, VALUE_RECT[2] - VALUE_RECT[0] - 36):
            rectangles.append(checked_text(im, VALUE_RECT, (883, y), row, 19, FG))
            y += 28
        y += 10
    if not value_map:
        rectangles.append(checked_text(im, VALUE_RECT, (883, y), 'No locals yet', 19, MUTED))
    return rectangles
