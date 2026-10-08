"""Measured audio → scenes.json, narration.wav, captions.srt, script.md, storyboard.md.

Caption timing is a PROPORTIONAL ESTIMATE inside each measured scene. It is not
forced word alignment and no full human listen is claimed.
"""
import json
import math
import pathlib
import re
import sys
import wave

R = pathlib.Path(__file__).parent
CFG = json.loads((R / 'config.json').read_text())
S = json.loads((R / 'scenes-draft.json').read_text())
GAP = CFG['scene_gap_seconds']
PROOF = '--proof' in sys.argv

from drawlib import caption_lines  # noqa: E402  (needs assets/font present)

start = 0.0
captions = []
chunks = []
params = None
for i, s in enumerate(S):
    path = R / f'audio/scene-{i + 1:02d}.wav'
    if PROOF:
        dur = 8.0
    else:
        if not path.exists():
            raise SystemExit(
                f'missing {path}. Synthesise speech first (see references/tts.md), or run '
                f'bash make_demo_audio.sh for placeholder audio.')
        with wave.open(str(path)) as w:
            par = (w.getnchannels(), w.getsampwidth(), w.getframerate())
            pcm = w.readframes(w.getnframes())
            dur = w.getnframes() / w.getframerate()
        if params is None:
            params = par
        assert par == params, f'scene {i + 1} audio format differs from scene 1'
        chunks.append(pcm)
    s.update(start=start, duration=dur + GAP, speech_duration=dur,
             audio=f'audio/scene-{i + 1:02d}.wav')

    sentences = [x.strip() for x in re.findall(r'[^.!?]+[.!?]?', s['narration']) if x.strip()]
    bounded = []
    for sentence in sentences:
        cur = ''
        for word in sentence.split():
            trial = (cur + ' ' + word).strip()
            if len(caption_lines(trial)) > 2 and cur:
                bounded.append(cur)
                cur = word
            else:
                cur = trial
        if cur:
            bounded.append(cur)
    sentences = bounded
    total = sum(map(len, sentences)) or 1
    pos = start
    scene_captions = []
    for txt in sentences:
        length = dur * len(txt) / total
        c = dict(start=pos, end=pos + length, text=txt, scene=i + 1)
        captions.append(c)
        scene_captions.append(c)
        pos += length

    def match(key):
        hits = [c for c in scene_captions if key in c['text']]
        assert hits, (s['id'], 'transition keyword not found in narration:', key)
        return hits[0]['start'] - start

    s['transition_at'] = match(s['transition_keyword'])
    s['cues'] = [dict(at=match(c['keyword']), text=c['text'], focus=None, source_keyword=c['keyword'])
                 for c in s['cue_definitions']]
    s['cues'].sort(key=lambda c: c['at'])
    for o in s['diagram']['objects']:
        if o['type'] == 'checks':
            o['times'] = [start + match(k) for k in o['keywords']]
        if o['type'] in ('wbox', 'wlink'):
            o['draw_at'] = match(o['keyword'])
    start += s['duration']

frames = math.ceil(start * CFG['fps'])
duration = frames / CFG['fps']
DATA = dict(width=CFG['width'], height=CFG['height'], fps=CFG['fps'], duration=duration, frames=frames,
            scenes=S, subtitles=captions,
            caption_alignment='Sentence-length proportional estimates within measured TTS; not forced word alignment',
            provisional_proof=PROOF)
(R / 'scenes.json').write_text(json.dumps(DATA, ensure_ascii=False, indent=2))

if not PROOF:
    with wave.open(str(R / 'narration.wav'), 'wb') as out:
        out.setnchannels(params[0])
        out.setsampwidth(params[1])
        out.setframerate(params[2])
        gap = bytes(round(GAP * params[2]) * params[0] * params[1])
        for pcm in chunks:
            out.writeframes(pcm)
            out.writeframes(gap)
        out.writeframes(bytes(max(0, round((duration - start) * params[2])) * params[0] * params[1]))

    def stamp(t):
        n = round(t * 1000)
        h, n = divmod(n, 3600000)
        m, n = divmod(n, 60000)
        sec, ms = divmod(n, 1000)
        return f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'

    (R / 'captions.srt').write_text('\n\n'.join(
        f'{i + 1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i, c in enumerate(captions)) + '\n')
    (R / 'script.md').write_text(
        '# narration script\n\nIndependent explanation, not verbatim narration of the source.\n'
        'Captions are proportional estimates inside measured scenes.\n\n'
        + '\n\n'.join(f'## {s["id"]}. {s["title"]} · {s["section"]}\n\n{s["narration"]}' for s in S))
    (R / 'storyboard.md').write_text(
        '# storyboard\n\n'
        + '\n\n'.join(
            f'## {s["id"]}. {s["title"]} ({s["start"]:.3f}–{s["start"] + s["duration"]:.3f}s)\n'
            f'claim: {s["claim"]}\nbefore/after: {s["visual"]}\nexception kept: {s["exceptions"]}\n'
            f'transition anchor: {s["transition_keyword"]} (proportional estimate)\n'
            f'on-screen note: ' + ' / '.join(c['text'] for c in s['cues']) for s in S))

print(f'prepared {len(S)} scenes {duration:.3f}s {frames} frames'
      + (' PROOF ONLY' if PROOF else ' from measured WAV lengths; no tempo adjustment'))
