"""Debugger-specific QA, run inside build/<lang>/ after qa.py and before package.py.

Separate from the encoded-file QA: it proves that what the panel shows is the pinned
source and the recorded run, not that the explanation is right.
"""
import hashlib
import json
import math
import pathlib
import subprocess

R = pathlib.Path(__file__).parent
SNAPSHOT = R / 'source-snapshot.py'


def git_blob(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def displayed(value):
    if isinstance(value, dict) and '__class__' in value:
        inner = ', '.join(f'{k}={displayed(v)}' for k, v in value.items() if k != '__class__')
        return f'{value["__class__"]}({inner})'
    if isinstance(value, str) and not value.startswith(('LineType.', 'list[')):
        return repr(value)
    return str(value)


def items_for(event, names):
    out = []
    for name in names:
        if name == 'return':
            assert event['event'] == 'return'
            out.append(['return', displayed(event['result'])])
        elif name.startswith('tracker.'):
            out.append([name, displayed(event['values']['tracker'][name.split('.', 1)[1]])])
        else:
            out.append([name, displayed(event['values'][name])])
    return out


def main():
    DATA = json.loads((R / 'scenes.json').read_text())
    TRACE = json.loads((R / 'trace.json').read_text())
    VERIFY = json.loads((R / 'source-verification.json').read_text())
    pinned = next(f for f in VERIFY['files'] if f['path'] == VERIFY['displayed_source'])
    raw = SNAPSHOT.read_bytes()
    assert git_blob(raw) == pinned['git_blob'], 'displayed source differs from the pinned blob'
    rows = raw.decode().splitlines()
    events = TRACE['events']
    count = 0
    for scene in DATA['scenes']:
        first, last = scene['code_range']
        previous_start = -1.0
        for h in scene['highlights']:
            event = events[h['event_index']]
            assert (event['function'], event['line'], event['event']) == (h['function'], h['line'], h['event'])
            assert event['function'] == scene['function'], ('highlight outside the scene function', h)
            assert first <= h['line'] <= last, ('highlight outside the code range', h)
            assert 0 <= h['start'] < h['end'] <= scene['duration'] + 1e-9, ('cue outside its panel', h)
            assert h['start'] > previous_start, ('cues out of order', h)
            assert h['items'] == items_for(event, h['show']), ('display differs from the recorded event', h)
            previous_start = h['start']
            count += 1
        assert rows[first - 1:last] == SNAPSHOT.read_text().splitlines()[first - 1:last]
    import render
    fps = DATA['fps']
    frames = set(range(0, DATA['frames'], 5))
    for scene in DATA['scenes']:
        for h in scene['highlights']:
            for t in (h['start'], h['end']):
                k = math.ceil((scene['start'] + t) * fps - 1e-8)
                frames.update(x for x in (k - 1, k, k + 1) if 0 <= x < DATA['frames'])
    for k in sorted(frames):
        render.renderAt(k / fps, True)
    samples = []
    (R / 'qa').mkdir(exist_ok=True)
    for scene in DATA['scenes']:
        for i, h in enumerate(scene['highlights']):
            at = scene['start'] + h['start'] + 0.1
            path = R / 'qa' / f'debugger-{scene["id"]:02d}-{i + 1:02d}.png'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(at), '-i', str(R / 'master.mp4'),
                            '-frames:v', '1', '-vf', 'scale=640:-1', str(path)], check=True)
            samples.append({'scene': scene['id'], 'line': h['line'], 'event_index': h['event_index'],
                            'at': at, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    report = {'passed': True, 'source_blob': pinned['git_blob'], 'highlights': count,
              'geometry_frames': len(frames), 'geometry_scope': 'every 5th frame plus each cue boundary ±1 frame',
              'event_semantics': TRACE['event_semantics'], 'scenario': TRACE['scenario'],
              'encoded_cue_samples': samples,
              'not_traced': VERIFY.get('not_traced', [])}
    (R / 'qa' / 'debugger-trace.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print('debugger trace checks', count, 'highlights,', len(frames), 'frames')


if __name__ == '__main__':
    main()
