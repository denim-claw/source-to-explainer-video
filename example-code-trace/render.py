"""Trace renderer adapter. The shared renderer still owns encoding and determinism."""
import bisect
import pathlib

import base_render as shared
from codedraw import code_panel
from panels import values

# Export the shared QA/replay interface.
S, DATA, W, H, FPS = shared.S, shared.DATA, shared.W, shared.H, shared.FPS
value, xy, USE_SVG = shared.value, shared.xy, False
SOURCE = (pathlib.Path(__file__).parent / 'source-snapshot.py').read_text().splitlines()


def renderAt(t, audit=False):
    index = max(0, min(len(S) - 1, bisect.bisect_right(shared.START, t + 1e-8) - 1))
    scene = S[index]
    local = max(0, t - scene['start'])
    # Shared title/caption/cut layers; diagram is intentionally empty of other text.
    im = shared_original(t)
    highlights = scene['highlights']
    active = next((h for h in highlights if h['start'] <= local < h['end']), None)
    line = active['line'] if active else None
    vals = active['values'] if active else {}
    rects = code_panel(im, SOURCE, *scene['code_range'], line) + values(im, vals, illustrative='lines trace' in scene['section'])
    if audit:
        return im, {'scene': scene['id'], 'time': t, 'phase': 0, 'cue': 0,
                    'text_rectangles': rects, 'out_of_frame': []}
    return im


shared_original = shared.renderAt
shared.renderAt = renderAt
if __name__ == '__main__':
    shared.main()
