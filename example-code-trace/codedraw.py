"""Draw an exact source slice with original line numbers and time-bounded highlights."""
import io
import keyword
import tokenize

from PIL import ImageDraw
from drawlib import FG, MUTED, PURPLE, TEAL, YELLOW, f
from panels import CODE_RECT, checked_text, panel


def code_panel(im, source_lines, first, last, active_line):
    assert 1 <= first <= last <= len(source_lines)
    assert active_line is None or first <= active_line <= last
    panel(im, CODE_RECT, f'inventory.py:{first}–{last}')
    rows = source_lines[first - 1:last]
    # Preserve indentation/text; only colour tokens. Never reflow or elide source lines.
    rectangles = []
    for offset, row in enumerate(rows):
        number, y = first + offset, 242 + offset * 30
        if number == active_line:
            ImageDraw.Draw(im).rounded_rectangle((48, y - 4, 832, y + 26), radius=4, fill='#214638')
        rectangles.append(checked_text(im, CODE_RECT, (56, y), str(number), 18, MUTED))
        rectangles.append(checked_text(im, CODE_RECT, (100, y), row, 20))
    # Token positions come from the displayed slice, including original whitespace.
    for token in tokenize.generate_tokens(io.StringIO('\n'.join(rows) + '\n').readline):
        if token.start[0] != token.end[0] or token.start[0] > len(rows):
            continue
        color = None
        if token.type == tokenize.STRING:
            color = YELLOW
        elif token.type == tokenize.NUMBER:
            color = PURPLE
        elif keyword.iskeyword(token.string):
            color = TEAL
        if color:
            row = rows[token.start[0] - 1]
            point = (100 + f(20).getlength(row[:token.start[1]]), 242 + (token.start[0] - 1) * 30)
            checked_text(im, CODE_RECT, point, token.string, 20, color)
    return rectangles
