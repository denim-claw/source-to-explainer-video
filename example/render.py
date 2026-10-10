"""Pure-function frame renderer → master MP4. Pillow + FFmpeg, deterministic in t.

    python render.py --samples        authoring bbox audit
    python render.py --determinism    forward/reverse RGB equality
    python render.py                  encode master.mp4
"""
import bisect
import hashlib
import io
import itertools
import json
import math
import pathlib
import subprocess
import sys
import time
from functools import lru_cache

from PIL import Image, ImageDraw

from drawlib import (BG, BLUE, EDGE, FG, GRID, MUTED, PURPLE, RED, TEAL, YELLOW,
                     arrow, box, clamp, curve_flow, dot, ease, flow, line, mix, mix_color,
                     morph_points, node, text, tile)

R = pathlib.Path(__file__).parent
CFG = json.loads((R / 'config.json').read_text())
DATA = json.loads((R / 'scenes.json').read_text())
S = DATA['scenes']
START = [s['start'] for s in S]
CAPSTART = [c['start'] for c in DATA['subtitles']]
W, H, FPS = DATA['width'], DATA['height'], DATA['fps']
OUT = R / 'master.mp4'
USE_SVG = False  # optional CairoSVG annotation layer; off by default

try:  # optional: a thin SVG annotation layer, cached per (scene, cue)
    import cairosvg  # type: ignore
    USE_SVG = True
except Exception:
    cairosvg = None


def value(v, q):
    """Interpolate a scalar/list field between the before (q<.5) and after (q>=.5) state."""
    if isinstance(v, list) and len(v) == 2:
        return mix(v[0], v[1], q) if all(isinstance(x, (int, float)) for x in v) else (v[0] if q < .5 else v[1])
    return v


def xy(v, q):
    if isinstance(v, list) and len(v) == 4:
        return (mix(v[0], v[2], q), mix(v[1], v[3], q))
    return tuple(v)


def base(s):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    for x in range(40, W - 40, 60):
        line(d, (x, 190), (x, 544), GRID, 1)
    for y in range(190, 545, 50):
        line(d, (40, y), (W - 40, y), GRID, 1)
    text(im, (58, 26), CFG['header'], 18, MUTED)
    text(im, (58, 69), s['title'], 40, FG)
    text(im, (58, 133), s['section'], 21, TEAL)
    text(im, (W - 100, 33), f'{s["id"]:02d} / {len(S)}', 20, MUTED, True)
    d.rounded_rectangle((40, 605, W - 40, 691), radius=12, fill='#182532')
    text(im, (48, 698), CFG['footer'], 12, MUTED)
    return im


BASE = [base(s) for s in S]


@lru_cache(maxsize=80)
def svg_overlay(scene_idx, cue_idx):
    """One semantic annotation per cue, rasterised once and cropped to its bbox."""
    cue = S[scene_idx]['cues'][cue_idx]
    content = ''
    focus = cue.get('focus')
    if focus:
        x, y, w, h = focus
        content += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" '
                    f'stroke="{TEAL}" stroke-width="2" stroke-dasharray="10 6" opacity="0.75"/>')
    content += f'<path d="M 68 553 L 80 553 L 80 578" fill="none" stroke="{TEAL}" stroke-width="3" stroke-linecap="round"/>'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{content}</svg>'
    a = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
    bb = a.getbbox()
    return a.crop(bb), bb[:2]


def renderAt(t, audit=False):
    i = max(0, min(len(S) - 1, bisect.bisect_right(START, t + 1e-8) - 1))
    s = S[i]
    local = max(0, t - s['start'])
    p = clamp(local / s['duration'])
    q = ease((local - s['transition_at']) / 2.4)

    im = BASE[i].copy()
    d = ImageDraw.Draw(im)
    d.rectangle((58, 173, 58 + int(1164 * ease(local / .6)), 176), fill=TEAL)

    objects = s['diagram']['objects']
    nodes = {o['id']: o for o in objects if o.get('id')}
    rects = []

    def pos(v):
        return xy(nodes[v]['pos'], q) if isinstance(v, str) else xy(v, q)

    def tracked_text(pt, txt, size, col, center=True):
        a = tile(str(txt), size, col)
        left = pt[0] - a.width / 2 if center else pt[0]
        top = pt[1]
        d.rounded_rectangle((left - 4, top - 2, left + a.width + 4, top + a.height + 2), radius=3, fill=BG)
        text(im, pt, txt, size, col, center)
        rects.append(dict(kind='text', text=str(txt), box=[left, top, left + a.width, top + a.height]))

    order = sorted(objects, key=lambda o: 0 if o['type'] in ('flow', 'line', 'arrow', 'curve', 'wlink', 'morph', 'mesh', 'timeline') else 1)
    for o in order:
        show = o.get('show', 'always')
        if (show == 'before' and q >= .5) or (show == 'after' and q < .5):
            continue
        kind = o['type']
        u = 1.0  # progressive-drawing phase; 1.0 means fully drawn
        if kind in ('wbox', 'wlink'):
            u = clamp((local - o['draw_at']) / 1.15)
            if u <= 0:
                continue
        col = value(o.get('color', TEAL), q)

        if kind in ('flow', 'line', 'arrow', 'wlink'):
            a, b = pos(o['from']), pos(o['to'])
            if kind == 'wlink':
                b = (mix(a[0], b[0], u), mix(a[1], b[1], u))
            if kind in ('flow', 'wlink'):
                flow(d, a, b, t, col, offset=o.get('offset', 0), count=o.get('count', 3), rate=o.get('rate', .16))
            elif kind == 'arrow':
                arrow(d, a, b, col, o.get('width', 3))
            else:
                line(d, a, b, col, o.get('width', 3))

        elif kind == 'curve':
            curve_flow(d, [pos(v) for v in o['points']], t, col, count=o.get('count', 4))

        elif kind == 'morph':
            pts = morph_points(o['rect'], o['circle'], n=o.get('points', 128), t=q)
            d.polygon(pts, fill='#18352f', outline=EDGE)
            d.line(pts + [pts[0]], fill=col, width=4, joint='curve')
            cx, cy = o['circle'][0], o['circle'][1]
            tracked_text((cx, cy - 14), value([o['label_before'], o['label_after']], q), 24, col)

        elif kind == 'node':
            pt = pos(o['pos'])
            r = value(o.get('r', 25), q)
            lab = value(o.get('label', ''), q)
            size = o.get('size', 22)
            node(im, d, pt, lab, col, r=r, size=size)
            if lab:
                a = tile(str(lab), size, col)
                rects.append(dict(kind='text', text=str(lab),
                                  box=[pt[0] - a.width / 2, pt[1] + r + 12, pt[0] + a.width / 2, pt[1] + r + 12 + a.height]))

        elif kind == 'label':
            tracked_text(pos(o['pos']), value(o['text'], q), o.get('size', 24), col, o.get('center', True))

        elif kind in ('box', 'wbox'):
            x, y = pos(o['pos'])
            w = value(o.get('w', 330), q)
            h = value(o.get('h', 58), q)
            size = o.get('size', 23)
            lab = value(o.get('label', ''), q)
            r = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if kind == 'wbox':
                r = (r[0], r[1], r[0] + (r[2] - r[0]) * u, r[3])
            d.rounded_rectangle(r, radius=9, fill=BG, outline=col, width=2)
            if u > .55:
                text(im, (x, y - size / 2), lab, size, col, True)
            a = tile(str(lab), size, col)
            rects.append(dict(kind='text', text=str(lab), box=[x - a.width / 2, y - size / 2, x + a.width / 2, y - size / 2 + a.height]))
            assert a.width <= w - 12, (s['id'], lab, 'box label overflow')

        elif kind == 'gate':
            x, y = pos(o['pos'])
            h = value(o.get('h', [150, 25]), q)
            d.rounded_rectangle((x - 9, y - h / 2, x + 9, y + h / 2), radius=4, fill=col)

        elif kind == 'timeline':
            # Release-style ticks on one axis. Shared ticks slide to their new spacing;
            # added ticks appear one by one and removed ticks leave one by one.
            (x0, x1), y = o['x'], o['y']
            before, after = o['count']
            line(d, (x0, y), (x1, y), EDGE, 3)
            for k in range(max(before, after)):
                pb = mix(x0, x1, (k + .5) / before) if k < before else None
                pa = mix(x0, x1, (k + .5) / after) if k < after else None
                if pb is not None and pa is not None:
                    x = mix(pb, pa, q)
                elif pa is not None:
                    if k - before >= (after - before) * q:
                        continue
                    x = pa
                else:
                    if k >= before - (before - after) * q:
                        continue
                    x = pb
                d.rounded_rectangle((x - 4, y - 22, x + 4, y + 22), radius=3, fill=col)

        elif kind == 'mesh':
            # n peers on a ring. Before: every pair talks. After: each peer talks to one hub.
            cx, cy = o['center']
            rad, n = o.get('radius', 130), o.get('n', 8)
            pts = [(cx + rad * math.cos(math.tau * k / n - math.pi / 2),
                    cy + rad * math.sin(math.tau * k / n - math.pi / 2)) for k in range(n)]
            pair = mix_color(RED, BG, ease(q * 1.6))
            spoke = mix_color(BG, TEAL, ease(q * 1.6 - .6))
            for a, b in itertools.combinations(pts, 2):
                line(d, a, b, pair, 2)
            for a in pts:
                line(d, a, (cx, cy), spoke, 3)
            for a in pts:
                dot(d, a, 9, YELLOW)
            hub = mix_color(BG, TEAL, ease(q * 1.6 - .6))
            d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=BG, outline=hub, width=4)

        elif kind == 'chips':
            # A short list whose members change at the transition (queue, holders, tape rows).
            x, y = pos(o['pos'])
            items = o['items'][1] if q >= .5 and isinstance(o['items'][0], list) else (
                o['items'][0] if isinstance(o['items'][0], list) else o['items'])
            size = o.get('size', 21)
            widths = [tile(str(it), size, col).width + 26 for it in items]
            gap = 12
            left = x - (sum(widths) + gap * (len(widths) - 1)) / 2 if o.get('center', True) else x
            for it, wdt in zip(items, widths):
                c = o.get('colors', {}).get(str(it), col)
                d.rounded_rectangle((left, y - 20, left + wdt, y + 20), radius=20, fill=BG, outline=c, width=2)
                a = tile(str(it), size, c)
                text(im, (left + wdt / 2, y - a.height / 2 - 1), it, size, c, True)
                rects.append(dict(kind='text', text=str(it),
                                  box=[left + 13, y - 20, left + wdt - 13, y + 20]))
                left += wdt + gap

        elif kind == 'checks':
            cols = o.get('cols', 3)
            y0, dy = o.get('y0', 300), o.get('dy', 120)
            cw = (W - 160) / cols
            for k, lab in enumerate(o['labels']):
                x = 80 + cw * (k % cols) + cw / 2
                y = y0 + dy * (k // cols)
                active = t >= o['times'][k]
                color = o.get('colors', [TEAL] * len(o['labels']))[k] if active else MUTED
                box(im, d, (x - cw * .44, y - 34, x + cw * .44, y + 34), lab, color, 22)
                dot(d, (x - cw * .37, y), 4, color)
                a = tile(lab, 22, color)
                rects.append(dict(kind='text', text=lab, box=[x - a.width / 2, y - 11, x + a.width / 2, y - 11 + a.height]))
        else:
            raise ValueError('unhandled object type ' + kind)

    # one semantic sentence in the reserved slack strip; never overlaps captions
    cue_idx = max([k for k, c in enumerate(s['cues']) if local >= c['at'] - 1e-8], default=-1)
    if cue_idx >= 0:
        cue = s['cues'][cue_idx]
        if USE_SVG:
            overlay, at = svg_overlay(i, cue_idx)
            im.paste(overlay, at, overlay)
        tracked_text((W / 2, 552), cue['text'], 23, FG)

    ci = bisect.bisect_right(CAPSTART, t + 1e-7) - 1
    if ci >= 0:
        c = DATA['subtitles'][ci]
        if c['scene'] == s['id'] and t < c['end'] + 1e-7:
            from drawlib import caption_lines
            lines = caption_lines(c['text'])
            assert len(lines) <= 2, (s['id'], 'caption longer than two lines', lines)
            y = 614 + (2 - len(lines)) * 16
            for txt in lines:
                text(im, (W / 2, y), txt, 26, FG, True)
                y += 32

    d.rectangle((40, 600, 40 + int(1200 * clamp(t / DATA['duration'])), 602), fill=TEAL)
    if audit:
        return im, dict(scene=s['id'], time=t, phase=q, cue=cue_idx + 1, text_rectangles=rects,
                        out_of_frame=[r for r in rects if r['box'][0] < 40 or r['box'][2] > W - 40
                                      or r['box'][1] < 190 or r['box'][3] > 590])
    return im


def main():
    if '--samples' in sys.argv:
        (R / 'samples').mkdir(exist_ok=True)
        (R / 'qa').mkdir(exist_ok=True)
        audits = []
        for s in S:
            times = [('early', s['start'] + s['duration'] * .14), ('late', s['start'] + s['duration'] * .82)]
            times += [(f'phase-{k:02d}', s['start'] + min(s['duration'] - .01, s['transition_at'] + k * .4)) for k in range(7)]
            times += [(f'cue-{k + 1:02d}', s['start'] + c['at'] + .25) for k, c in enumerate(s['cues'])]
            for tag, t in times:
                im, a = renderAt(t, True)
                im.save(R / f'samples/{s["id"]:02d}-{tag}.png')
                audits.append(a)
        (R / 'qa/layout-author.json').write_text(json.dumps(audits, ensure_ascii=False, indent=2))
        bad = [a for a in audits if a['out_of_frame']]
        print('samples', len(audits), 'out_of_frame', len(bad))
        assert not bad, bad
        return

    if '--determinism' in sys.argv:
        ts = [s['start'] + s['duration'] * .14 for s in S] + [s['start'] + s['duration'] * .82 for s in S]
        a = {str(t): hashlib.sha256(renderAt(t).tobytes()).hexdigest() for t in ts}
        b = {str(t): hashlib.sha256(renderAt(t).tobytes()).hexdigest() for t in reversed(ts)}
        assert a == b
        (R / 'qa/determinism.json').write_text(json.dumps(dict(
            scope='Same-machine Pillow RGB equality in forward/reverse calls, not cross-platform',
            passed=True, samples=len(ts), hashes=a), indent=2))
        print('deterministic', len(ts))
        return

    voice = R / 'narration.flac'
    if not voice.exists():
        voice = R / 'narration.wav'
    cmd = ['ffmpeg', '-v', 'error', '-y',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0',
           '-i', str(voice), '-i', str(R / 'captions.srt'),
           '-map', '0:v:0', '-map', '1:a:0', '-map', '2:s:0',
           '-c:v', 'libx264', '-preset', 'fast', '-crf', str(CFG['crf']), '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', CFG['audio_bitrate'], '-ar', str(CFG['audio_sample_rate']), '-ac', '1',
           '-af', 'loudnorm=I=-16:TP=-3:LRA=11,alimiter=limit=0.75:level=false',
           '-c:s', 'mov_text',
           '-metadata:s:a:0', f'language={CFG.get("language", "kor")}',
           '-metadata:s:s:0', f'language={CFG.get("language", "kor")}',
           '-metadata', f'title={CFG["header"]}',
           '-t', str(DATA['duration']), '-movflags', '+faststart', str(OUT)]
    (R / 'render-command.json').write_text(json.dumps(cmd, ensure_ascii=False, indent=2))
    t0 = time.monotonic()
    with open(R / 'render-ffmpeg.log', 'wb') as log:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
        try:
            for frame in range(DATA['frames']):
                proc.stdin.write(renderAt(frame / FPS).tobytes())
                if frame % 600 == 0:
                    print('frame', frame, '/', DATA['frames'], 'seconds', round(time.monotonic() - t0, 1), flush=True)
            proc.stdin.close()
            assert proc.wait() == 0
        except BaseException:
            proc.kill()
            proc.wait()
            raise
    (R / 'render-result.json').write_text(json.dumps(dict(
        path=str(OUT), frames=DATA['frames'], seconds=time.monotonic() - t0,
        renderer='Pillow + FFmpeg'), indent=2))
    print('RENDER COMPLETE', DATA['frames'], flush=True)


if __name__ == '__main__':
    main()
