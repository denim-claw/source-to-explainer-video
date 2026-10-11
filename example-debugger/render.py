"""Debugger renderer adapter. The shared renderer still owns layout bands, encoding and QA."""
import bisect
import json
import pathlib

import base_render as shared
from tracedraw import code_panel, watch_bar

R = pathlib.Path(__file__).parent
S, DATA, W, H, FPS = shared.S, shared.DATA, shared.W, shared.H, shared.FPS
value, xy, USE_SVG = shared.value, shared.xy, False
SOURCE = (R / 'source-snapshot.py').read_text().splitlines()
TRACE = json.loads((R / 'trace.json').read_text())
HUNK = TRACE['input']['content'].splitlines()
CFG = json.loads((R / 'config.json').read_text())
LABELS = CFG['trace_labels']


def renderAt(t, audit=False):
    index = max(0, min(len(S) - 1, bisect.bisect_right(shared.START, t + 1e-8) - 1))
    scene = S[index]
    local = max(0, t - scene['start'])
    im = shared_original(t)
    active = next((h for h in scene['highlights'] if h['start'] <= local < h['end']), None)
    first, last = scene['code_range']
    title = f'{CFG["source_path"]}:{first}–{last} · {scene["function"]}'
    rects = code_panel(im, SOURCE, first, last, active['line'] if active else None, title)
    if active:
        heading = (LABELS['returned'] if active['event'] == 'return' else LABELS['before']).format(
            line=active['line'], function=active['function'])
        rects += watch_bar(im, heading, active['items'], HUNK, active['hunk_index'], LABELS)
    else:
        rects += watch_bar(im, LABELS['waiting'], [], HUNK, None, LABELS)
    if audit:
        return im, {'scene': scene['id'], 'time': t, 'phase': 0, 'cue': 0,
                    'text_rectangles': rects, 'out_of_frame': []}
    return im


shared_original = shared.renderAt
shared.renderAt = renderAt
if __name__ == '__main__':
    shared.main()
