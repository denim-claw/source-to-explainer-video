"""Encoded-master audit. Owns EVERY derivative in qa/ — never hand-run ffmpeg for these.

Checks: probe + counted frames, full decode, audio peak/RMS/clipping, semantic
before/after change, text and label-vs-card collisions, cut-point samples,
phone-size frames, forward/reverse seek determinism, per-scene audio provenance.
"""
import concurrent.futures
import hashlib
import itertools
import json
import pathlib
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from drawlib import caption_lines, font_path, tile
from render import S, value, xy, USE_SVG as use_svg

R = pathlib.Path(__file__).parent
Q = R / 'qa'
Q.mkdir(exist_ok=True)
D = json.loads((R / 'scenes.json').read_text())
V = R / 'master.mp4'
assert V.exists(), 'run render.py first'


def run(cmd):
    return subprocess.run(cmd, capture_output=True, check=True)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def frame(t, p, w=1280):
    run(['ffmpeg', '-v', 'error', '-threads', '1', '-y', '-ss', str(t), '-i', str(V),
         '-frames:v', '1', '-vf', f'scale={w}:-1', str(p)])


assert not D['provisional_proof'], 'proof render must never be reported as final'
probe = json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(V)]).stdout)
(Q / 'ffprobe.json').write_text(json.dumps(probe, indent=2))
v = next(x for x in probe['streams'] if x['codec_type'] == 'video')
aud = next(x for x in probe['streams'] if x['codec_type'] == 'audio')
assert int(v['nb_read_frames']) == D['frames'], (v['nb_read_frames'], D['frames'])
assert (v['width'], v['height'], v['r_frame_rate'], v['codec_name'], v['pix_fmt']) == (D['width'], D['height'], '30/1', 'h264', 'yuv420p')
assert aud['codec_name'] == 'aac' and aud['channels'] == 1
decode = run(['ffmpeg', '-v', 'error', '-i', str(V), '-f', 'null', '-'])
assert not decode.stderr, decode.stderr.decode()
(Q / 'decode-errors.txt').write_bytes(decode.stderr)

items = []
for s in S:
    if s['diagram']['objects'][0]['type'] == 'checks':
        before, after = s['start'] + .02, s['start'] + s['duration'] * .96
    else:
        before = s['start'] + max(.02, s['transition_at'] - .6)
        after = s['start'] + min(s['duration'] - .08, s['transition_at'] + 3.2)
    for tag, t in (('early', before), ('late', after)):
        items.append((t, Q / f'scene-{s["id"]:02d}-{tag}.png', 1280))
    items.append((after, Q / f'phone-{s["id"]:02d}.png', 640))
    if s['id'] > 1:
        for k, off in enumerate([0, .08, .17, .4]):
            items.append((s['start'] + off, Q / f'cut-{s["id"]:02d}-{k}.png', 640))
    for k, c in enumerate(s['cues']):
        items.append((s['start'] + c['at'] + .25, Q / f'cue-{s["id"]:02d}-{k + 1:02d}.png', 640))
list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(lambda x: frame(*x), items))
print('extracted', len(items), 'frames from the encoded master', flush=True)

font = ImageFont.truetype(str(font_path()), 18)
for batch in range(0, len(S), 4):
    seq = S[batch:batch + 4]
    sheet = Image.new('RGB', (1280, len(seq) * 390), '#101923')
    dr = ImageDraw.Draw(sheet)
    for row, s in enumerate(seq):
        for col, tag in enumerate(['early', 'late']):
            sheet.paste(Image.open(Q / f'scene-{s["id"]:02d}-{tag}.png').resize((640, 360)), (col * 640, row * 390 + 30))
        dr.text((10, row * 390 + 5), f'{s["id"]:02d} {s["title"]} · encoded master before / after', font=font, fill='#edf3f5')
    sheet.save(Q / f'encoded-sheet-{batch // 4 + 1}.jpg', quality=94)

cutfiles = sorted(Q.glob('cut-*.png'))
for batch in range(0, len(cutfiles), 20):
    fs = cutfiles[batch:batch + 20]
    sheet = Image.new('RGB', (1280, 200 * -(-len(fs) // 4)), '#101923')
    dr = ImageDraw.Draw(sheet)
    for k, p in enumerate(fs):
        x, y = k % 4 * 320, k // 4 * 200
        dr.text((x + 4, y + 2), p.stem, font=font, fill='#edf3f5')
        sheet.paste(Image.open(p).resize((320, 180)), (x, y + 20))
    sheet.save(Q / f'cuts-sheet-{batch // 20 + 1}.jpg', quality=94)

motion = []
for s in S:
    aa = np.asarray(Image.open(Q / f'scene-{s["id"]:02d}-early.png')).astype(float)[190:545, 40:1240]
    bb = np.asarray(Image.open(Q / f'scene-{s["id"]:02d}-late.png')).astype(float)[190:545, 40:1240]
    mad = float(np.abs(aa - bb).mean())
    assert mad > .1, (s['id'], 'diagram did not change between before and after')
    motion.append(dict(scene=s['id'], diagram_rgb_MAD=mad, changed=True, semantic_change=s['visual']))

raw = run(['ffmpeg', '-v', 'error', '-i', str(V), '-map', '0:a:0', '-ar', '16000', '-ac', '1', '-f', 'f32le', '-']).stdout
audio = np.frombuffer(raw, dtype='<f4')
peak, rms = float(np.max(np.abs(audio))), float(np.sqrt(np.mean(audio * audio)))
clipped = int(np.count_nonzero(np.abs(audio) >= 1))
assert peak < 1 and rms > .001 and clipped == 0, (peak, rms, clipped)

layouts = json.loads((Q / 'layout-author.json').read_text())


def card_rects(scene, q):
    """Every filled/outlined card and checklist cell actually drawn at this phase, plus
    its label text box. Text-vs-text checks miss these: a card painted later, or a
    checklist cell placed over a card, clips a label while no two texts overlap."""
    out = []
    for o in scene['diagram']['objects']:
        kind = o['type']
        if kind in ('box', 'wbox'):
            x, y = xy(o['pos'], q)
            w = value(o.get('w', 330), q)
            h = value(o.get('h', 58), q)
            lab = value(o.get('label', ''), q)
            out.append(dict(kind=kind, label=lab, rect=[x - w / 2, y - h / 2, x + w / 2, y + h / 2]))
        elif kind == 'checks':
            cols = o.get('cols', 3)
            cw = (1280 - 160) / cols
            for k, lab in enumerate(o['labels']):
                x = 80 + cw * (k % cols) + cw / 2
                y = o.get('y0', 300) + o.get('dy', 120) * (k // cols)
                out.append(dict(kind='checks', label=lab,
                                rect=[x - cw * .44, y - 34, x + cw * .44, y + 34]))
    return out


def overlap(a, b):
    return min(a[2], b[2]) - max(a[0], b[0]) > 2 and min(a[3], b[3]) - max(a[1], b[1]) > 2


collisions, node_card, card_overlaps, label_card_hits = [], [], [], []
for entry in layouts:
    assert not entry['out_of_frame'], entry
    for t1, t2 in itertools.combinations(entry['text_rectangles'], 2):
        if overlap(t1['box'], t2['box']):
            collisions.append(dict(scene=entry['scene'], time=entry['time'], texts=[t1['text'], t2['text']]))
    s = S[entry['scene'] - 1]
    q = entry['phase']
    for n in [o for o in s['diagram']['objects'] if o['type'] == 'node']:
        if (n.get('show') == 'before' and q >= .5) or (n.get('show') == 'after' and q < .5):
            continue
        lab = value(n.get('label', ''), q)
        if not lab:
            continue
        x, y = xy(n['pos'], q)
        r = value(n.get('r', 25), q)
        t0 = tile(str(lab), n.get('size', 22), value(n.get('color', '#51dccb'), q))
        nb = [x - t0.width / 2, y + r + 12, x + t0.width / 2, y + r + 12 + t0.height]
        for o in [o for o in s['diagram']['objects'] if o['type'] in ('box', 'wbox')]:
            xx, yy = xy(o['pos'], q)
            w = value(o.get('w', 330), q)
            h = value(o.get('h', 58), q)
            cb = [xx - w / 2, yy - h / 2, xx + w / 2, yy + h / 2]
            if overlap(nb, cb):
                node_card.append(dict(scene=s['id'], time=entry['time'], label=lab, card=value(o.get('label', ''), q)))
    cards = card_rects(s, q)
    for c1, c2 in itertools.combinations(cards, 2):
        if c1['rect'] == c2['rect']:
            continue
        if overlap(c1['rect'], c2['rect']):
            card_overlaps.append(dict(scene=s['id'], time=entry['time'], a=c1['label'], b=c2['label'], kinds=[c1['kind'], c2['kind']]))
    labels = [r for r in entry['text_rectangles']]
    for lb in labels:
        for c in cards:
            if c['label'] == lb['text']:
                continue
            if overlap(lb['box'], c['rect']):
                label_card_hits.append(dict(scene=s['id'], time=entry['time'], text=lb['text'], card=c['label'], kind=c['kind']))

assert not collisions, collisions
assert not node_card, node_card
assert not card_overlaps, card_overlaps
assert not label_card_hits, label_card_hits[:5]
assert all(len(caption_lines(c['text'])) <= 2 for c in D['subtitles'])
assert all(tile(s['title'], 40, '#edf3f5').width <= 1164 for s in S)

ts = [s['start'] + min(4, s['duration'] * .1) for s in S]
forward = {}
for i, t in enumerate(ts):
    p = Q / f'seek-{i:02d}.png'
    frame(t, p, 640)
    forward[str(t)] = sha(p)
backward = {}
for i, t in reversed(list(enumerate(ts))):
    p = Q / f'seek-{i:02d}-reverse.png'
    frame(t, p, 640)
    backward[str(t)] = sha(p)
assert forward == backward
(Q / 'encoded-seek-determinism.json').write_text(json.dumps(dict(
    passed=True, samples=len(ts), hashes=forward,
    scope='Same-machine FFmpeg forward/reverse timestamp extraction; not cross-platform bit identity'), indent=2))

scene_audio = []
for s in S:
    p = R / s['audio']
    if not p.exists():
        scene_audio.append(dict(scene=s['id'], audio=str(p), present=False))
        continue
    meta = p.with_name(p.stem + '-metadata.json')
    entry = dict(scene=s['id'], seconds=s['speech_duration'], sha256=sha(p), present=True)
    if meta.exists():
        m = json.loads(meta.read_text())
        assert m.get('text') == s['narration'], f'scene {s["id"]} audio metadata text differs from narration'
        entry.update(model=m.get('model'), voice=m.get('voice'), interaction_id=m.get('id'))
    scene_audio.append(entry)

report = dict(
    master=str(V), master_sha256=sha(V), bytes=V.stat().st_size, duration=float(probe['format']['duration']),
    frames=int(v['nb_read_frames']), expected_frames=D['frames'], width=D['width'], height=D['height'],
    fps=v['r_frame_rate'], video_codec=v['codec_name'], pixel_format=v['pix_fmt'],
    audio_codec=aud['codec_name'], audio_sample_rate=aud['sample_rate'], audio_channels=aud['channels'],
    full_decode_exit=decode.returncode, decode_errors_empty=True, scene_count=len(S),
    cue_count=sum(len(s['cues']) for s in S), caption_count=len(D['subtitles']),
    caption_alignment=D['caption_alignment'],
    full_human_listen=False, asr_pronunciation_check=False, independent_content_reviewer=False,
    cut_samples=len(cutfiles), phone_samples=len(S), motion=motion,
    audio_peak=peak, audio_rms=rms, clipped_samples=clipped, audio_analysis_rate=16000,
    audio_scene_provenance=scene_audio,
    author_layout_samples=len(layouts), author_text_collisions=collisions,
    author_node_label_card_collisions=node_card,
    author_card_overlaps=card_overlaps, author_label_card_hits=label_card_hits,
    author_text_out_of_frame=0,
    determinism=json.loads((Q / 'determinism.json').read_text())['passed'], encoded_seek_determinism=True,
    renderer='Pillow + ' + ('CairoSVG annotation layer + ' if use_svg else '') + 'FFmpeg',
    encoder_tag=probe['format'].get('tags', {}).get('encoder'),
    published=False)
(Q / 'qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({k: val for k, val in report.items() if k not in ('motion', 'audio_scene_provenance')}, ensure_ascii=False, indent=2))
