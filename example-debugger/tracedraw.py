"""Full-width source panel, a watch bar of recorded values, and a hunk cursor.

Long real-world lines do not fit beside a value column, so the code spans the frame and
the debugger values sit underneath. Text is never shrunk, clipped or reflowed: anything
that does not fit fails an assertion.
"""
import io
import keyword
import pathlib
import tokenize
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont
from drawlib import BG, EDGE, FG, MUTED, PURPLE, RED, TEAL, YELLOW, text

MONO = pathlib.Path(__file__).parent / 'assets' / 'NotoSansMonoCJKkr-Regular.otf'
CODE_RECT = (40, 190, 1240, 466)
WATCH_RECT = (40, 474, 1240, 592)
ROW0, ROW_STEP, CODE_SIZE = 230, 28, 20
HIGHLIGHT = '#214638'


@lru_cache(maxsize=16)
def mono(size):
    return ImageFont.truetype(str(MONO), size)


@lru_cache(maxsize=2000)
def mono_tile(label, size, color):
    """Same ascent-anchored box for every label, so a coloured token lands exactly on its row."""
    font = mono(size)
    ascent, descent = font.getmetrics()
    im = Image.new('RGBA', (int(font.getlength(label)) + 4, ascent + descent), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2, 0), label, font=font, fill=color)
    return im


def checked(im, rect, point, label, size, color=FG):
    tile = mono_tile(label, size, color)
    x, y = point
    assert rect[0] + 8 <= x and x + tile.width <= rect[2] - 8, ('horizontal overflow', label)
    assert rect[1] + 8 <= y and y + tile.height <= rect[3] - 8, ('vertical overflow', label)
    im.paste(tile, (round(x), round(y)), tile)
    return {'kind': 'text', 'text': label, 'box': [x, y, x + tile.width, y + tile.height]}


def frame(im, rect, title, color=TEAL):
    ImageDraw.Draw(im).rounded_rectangle(rect, radius=10, fill=BG, outline=EDGE, width=2)
    text(im, (rect[0] + 16, rect[1] + 8), title, 17, color)


@lru_cache(maxsize=4)
def file_tokens(source):
    out = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.start[0] != token.end[0]:
            continue
        color = (YELLOW if token.type == tokenize.STRING else PURPLE if token.type == tokenize.NUMBER
                 else TEAL if keyword.iskeyword(token.string) else None)
        if color:
            out.append((token.start[0], token.start[1], token.string, color))
    return tuple(out)


def code_panel(im, source_lines, first, last, active_line, title):
    assert 1 <= first <= last <= len(source_lines)
    assert last - first + 1 <= 8, 'a panel holds at most 8 source rows; split the scene'
    assert active_line is None or first <= active_line <= last
    frame(im, CODE_RECT, title)
    rows = source_lines[first - 1:last]
    rects = []
    for offset, row in enumerate(rows):
        number, y = first + offset, ROW0 + offset * ROW_STEP
        if number == active_line:
            ImageDraw.Draw(im).rounded_rectangle((48, y - 3, 1232, y + 25), radius=4, fill=HIGHLIGHT)
        rects.append(checked(im, CODE_RECT, (56, y + 2), f'{number:>3}', 17, TEAL if number == active_line else MUTED))
        rects.append(checked(im, CODE_RECT, (112, y), row, CODE_SIZE))
    # Colour tokens over the exact row text. Tokenize the whole file: a slice that starts
    # inside an indented block is not valid Python on its own.
    for row_number, column, label, color in file_tokens('\n'.join(source_lines) + '\n'):
        if first <= row_number <= last:
            row = source_lines[row_number - 1]
            x = 112 + mono(CODE_SIZE).getlength(row[:column])
            checked(im, CODE_RECT, (x, ROW0 + (row_number - first) * ROW_STEP), label, CODE_SIZE, color)
    return rects


def watch_bar(im, title, items, hunk_lines, hunk_index, labels):
    """items: list of (name, shown value). hunk_index: the diff line the loop holds, or None."""
    frame(im, WATCH_RECT, title, YELLOW)
    rects, x = [], 56
    if not items:
        rects.append(checked(im, WATCH_RECT, (x, 510), labels['empty'], 18, MUTED))
    for name, shown in items:
        label = f'{name} = {shown}'
        rects.append(checked(im, WATCH_RECT, (x, 510), label, 18, FG))
        x += mono_tile(label, 18, FG).width + 34
    text(im, (56, 551), labels['hunk'], 15, MUTED)
    x = 136
    d = ImageDraw.Draw(im)
    for index, line in enumerate(hunk_lines):
        shown = ('·' + line[1:]) if line.startswith(' ') else line
        color = TEAL if line.startswith('+') else RED if line.startswith('-') else MUTED
        tile = mono_tile(shown, 15, FG if index == hunk_index else color)
        box = (x, 544, x + tile.width + 16, 574)
        assert box[2] <= WATCH_RECT[2] - 8, ('hunk strip overflow', line)
        d.rounded_rectangle(box, radius=6, fill=HIGHLIGHT if index == hunk_index else BG,
                            outline=TEAL if index == hunk_index else EDGE, width=2)
        im.paste(tile, (x + 8, 549), tile)
        rects.append({'kind': 'text', 'text': shown, 'box': [x + 8, 549, x + 8 + tile.width, 549 + tile.height]})
        x = box[2] + 10
    return rects
