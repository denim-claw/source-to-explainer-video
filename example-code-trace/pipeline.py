"""Stage a code-trace adapter and reuse example/{prepare,render,qa,package}.py.

No paid TTS or live services. Run from any directory; build/ is local and ignored.
"""
import argparse
import hashlib
import json
import math
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SHARED = ROOT.parent / 'example'
BUILD = ROOT / 'build'


def run(*args, cwd=None):
    return subprocess.run(list(map(str, args)), cwd=BUILD if cwd is None else cwd, check=True, capture_output=True)


def write(name, value):
    (BUILD / name).write_text(json.dumps(value, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage(mode):
    BUILD.mkdir(exist_ok=True)
    (BUILD / 'assets').mkdir(exist_ok=True)
    (BUILD / 'audio').mkdir(exist_ok=True)
    (BUILD / 'qa').mkdir(exist_ok=True)
    for name in ('prepare.py', 'qa.py', 'package.py', 'drawlib.py'):
        shutil.copy2(SHARED / name, BUILD / name)
    shutil.copy2(SHARED / 'render.py', BUILD / 'base_render.py')
    for name in ('render.py', 'codedraw.py', 'panels.py'):
        shutil.copy2(ROOT / name, BUILD / name)
    shutil.copy2(ROOT.parent / 'LICENSE', BUILD / 'LICENSE')
    shutil.copy2(ROOT / 'README.md', BUILD / 'README.md')
    shutil.copy2(SHARED / 'assets/font-license.txt', BUILD / 'assets/font-license.txt')
    font = SHARED / 'assets/NotoSansCJKkr-Regular.otf'
    if not font.is_file():
        raise SystemExit('Fetch the shared OFL font first: see README.md')
    shutil.copy2(font, BUILD / 'assets/NotoSansCJKkr-Regular.otf')
    source = ROOT / 'inventory.py'
    blob = run('git', 'hash-object', '-w', source, cwd=ROOT).stdout.decode().strip()
    original = run('git', 'cat-file', 'blob', blob, cwd=ROOT).stdout
    assert original == source.read_bytes()
    (BUILD / 'source-snapshot.py').write_bytes(original)
    write('source-verification.json', {'source': 'fictional inventory.py',
          'source_git_blob': blob, 'source_sha256': digest(source),
          'scope': 'new public fixture pinned by Git blob, not private application code',
          'line_count': len(original.decode().splitlines())})
    from harness import record
    trace = record()
    write('trace.json', trace)
    scenarios = [
        ('Validate the request', [4, 8],
         'Validate the request before changing stock. Read the available stock after authentication.',
         [('Validate', 6), ('Read', 8)]),
        ('Compute the remaining stock', [8, 12],
         'Subtract two units from five units. The remaining stock becomes three. Fix the clock for a repeatable run.',
         [('Subtract', 11), ('The remaining', 12), ('Fix', 12)]),
        ('Save with a fixed timestamp', [11, 14],
         'Save three remaining units with the fixed timestamp. Return the result after the fake storage call.',
         [('Save', 13), ('Return', 14)]),
    ]
    scenes = []
    for index, (title, code_range, narration, cues) in enumerate(scenarios, 1):
        scenes.append({'id': index, 'title': title, 'section': f'Fictional inventory · {mode} trace',
            'claim': title, 'visual': 'highlight the current source line and replace values',
            'exceptions': 'Success path only; real authentication/DB/time are not verified.',
            'narration': narration, 'transition_keyword': cues[0][0],
            'cue_definitions': [{'keyword': word, 'text': ''} for word, _ in cues],
            'diagram': {'objects': [{'type': 'label', 'text': '', 'pos': [500, 550]}]},
            'code_range': code_range,
            'highlight_definitions': [{'keyword': word, 'line': line} for word, line in cues]})
    write('scenes-draft.json', scenes)
    config = json.loads((SHARED / 'config.json').read_text())
    config.update(header='CODE TRACE · FICTIONAL INVENTORY',
                  footer='Injected fakes / temporary speech / estimated caption timing / success path only',
                  scene_gap_seconds=0.3,
                  package_extra_files=['base_render.py', 'codedraw.py', 'panels.py',
                                       'source-snapshot.py', 'source-verification.json',
                                       'trace.json', 'qa/code-trace.json'])
    (BUILD / 'config.json').write_text(json.dumps(config, indent=2))
    return scenes, trace


def audio(scenes):
    for scene in scenes:
        wav = BUILD / f'audio/scene-{scene["id"]:02d}.wav'
        metadata = wav.with_name(wav.stem + '-metadata.json')
        text = scene['narration']
        if wav.exists() and metadata.exists() and json.loads(metadata.read_text()).get('text') == text:
            continue
        raw = wav.with_suffix('.aiff' if shutil.which('say') else '.raw.wav')
        if shutil.which('say'):
            run('say', '-v', 'Samantha', '-r', '175', '-o', raw, text)
            engine = 'macOS say · temporary demo speech'
        elif shutil.which('espeak'):
            run('espeak', '-w', raw, text)
            engine = 'espeak · temporary demo speech'
        else:
            raise SystemExit('Install espeak or use macOS say; no paid TTS fallback is performed.')
        run('ffmpeg', '-v', 'error', '-y', '-i', raw, '-ac', '1', '-ar', '24000', '-c:a', 'pcm_s16le', wav)
        raw.unlink()
        metadata.write_text(json.dumps({'text': text, 'model': engine, 'voice': 'local demo',
                                       'temporary': True, 'paid_calls': 0}, indent=2))


def prepare(trace, mode):
    run(sys.executable, 'prepare.py')
    data = json.loads((BUILD / 'scenes.json').read_text())
    for scene in data['scenes']:
        highlights = []
        for definition, cue in zip(scene['highlight_definitions'], scene['cues']):
            assert definition['keyword'] == cue['source_keyword']
            event_index = next(i for i, e in enumerate(trace['events'])
                               if e['event'] == 'line' and e['line'] == definition['line'])
            event = trace['events'][event_index]
            highlights.append({'start': cue['at'], 'line': definition['line'],
                'values': event['values'] if mode == 'debugger' else {'units': 2},
                'keyword': definition['keyword'], 'trace_event_index': event_index})
        for i, highlight in enumerate(highlights):
            highlight['end'] = highlights[i + 1]['start'] if i + 1 < len(highlights) else scene['duration']
        scene['highlights'] = highlights
    write('scenes.json', data)
    return data


def check_trace(data):
    # Check every displayed row against the pinned Git original, not a manually retyped snippet.
    verification = json.loads((BUILD / 'source-verification.json').read_text())
    blob = run('git', 'cat-file', 'blob', verification['source_git_blob'], cwd=ROOT).stdout.decode().splitlines()
    snapshot = (BUILD / 'source-snapshot.py').read_text().splitlines()
    assert snapshot == blob
    assert digest(BUILD / 'source-snapshot.py') == verification['source_sha256']
    trace = json.loads((BUILD / 'trace.json').read_text())
    row_count, highlights = 0, 0
    for scene in data['scenes']:
        first, last = scene['code_range']
        assert snapshot[first - 1:last] == blob[first - 1:last]
        row_count += last - first + 1
        for h in scene['highlights']:
            assert 0 <= h['start'] < h['end'] <= scene['duration'], ('cue outside its panel', h)
            assert first <= h['line'] <= last
            event = trace['events'][h['trace_event_index']]
            assert event['line'] == h['line'] and event['event'] == 'line'
            if 'debugger trace' in scene['section']:
                assert h['values'] == event['values'], 'display values differ from trace'
            highlights += 1
    sys.path.insert(0, str(BUILD))
    import render
    # Every frame audits real-font width/height and checks source/value panel separation.
    for frame in range(data['frames']):
        render.renderAt(frame / data['fps'], True)
    report = {'passed': True, 'git_source_rows_compared': row_count,
              'highlights_within_own_panel': highlights, 'geometry_frames': data['frames'],
              'source_git_blob': verification['source_git_blob'],
              'scope': 'fictional success path, line events are before execution; no live integration',
              'temporary_audio': True, 'paid_tts_calls': 0}
    write('qa/code-trace.json', report)
    write('source-fidelity-review.json', {
        'source': verification, 'coverage': [s['claim'] for s in data['scenes']],
        'scenario_verified': 'units=2, stock=5, remaining=3, fixed timestamp and save arguments',
        'not_verified': ['invalid authentication', 'insufficient stock', 'real services', 'independent content review']})



def check_encoded_trace(data):
    # All trace derivatives are regenerated by this pipeline, from the encoded master.
    from PIL import Image, ImageDraw
    samples = []
    for scene in data['scenes']:
        for index, highlight in enumerate(scene['highlights']):
            anchor = scene['start'] + highlight['start']
            for tag, offset in [('before', -1 / data['fps']), ('at', 0), ('after', 1 / data['fps'])]:
                # At selects the first encoded frame on/after the cue, not a preceding frame.
                frame_index = max(0, min(data['frames'] - 1,
                    math.ceil(anchor * data['fps'] - 1e-8) + round(offset * data['fps'])))
                path = BUILD / f'qa/trace-{scene["id"]}-{index}-{tag}.png'
                run('ffmpeg', '-v', 'error', '-y', '-ss', frame_index / data['fps'],
                    '-i', 'master.mp4', '-frames:v', '1', '-vf', 'scale=640:-1', path)
                samples.append({'scene': scene['id'], 'line': highlight['line'],
                                'tag': tag, 'frame': frame_index, 'sha256': digest(path)})
    selected = sorted((BUILD / 'qa').glob('trace-*-after.png'))
    sheet = Image.new('RGB', (1280, math.ceil(len(selected) / 2) * 360), '#101923')
    for index, path in enumerate(selected):
        sheet.paste(Image.open(path), (index % 2 * 640, index // 2 * 360))
    sheet.save(BUILD / 'qa/encoded-sheet-trace.jpg', quality=94)
    report = json.loads((BUILD / 'qa/code-trace.json').read_text())
    report['encoded_cue_samples'] = samples
    write('qa/code-trace.json', report)


def split_parts(data, max_bytes, max_scenes):
    assert max_bytes > 0 and max_scenes > 0
    parts = []
    def encode(scenes):
        number = len(parts) + 1
        name = f'part-{number:02d}.mp4'
        path = BUILD / name
        # Match renderAt's scene selection on the frame grid: first frame at/after cut.
        start_frame = math.ceil(scenes[0]['start'] * data['fps'] - 1e-8)
        end_frame = (data['frames'] if scenes[-1] == data['scenes'][-1] else
                     math.ceil((scenes[-1]['start'] + scenes[-1]['duration']) * data['fps'] - 1e-8))
        start, end = start_frame / data['fps'], end_frame / data['fps']
        frames = end_frame - start_frame
        run('ffmpeg', '-v', 'error', '-y', '-ss', start, '-i', 'master.mp4',
            '-t', frames / data['fps'], '-map', '0:v:0', '-map', '0:a:0',
            '-c:v', 'libx264', '-crf', '21', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-ar', '48000', '-ac', '1', '-movflags', '+faststart', path)
        if path.stat().st_size > max_bytes:
            if len(scenes) == 1:
                path.unlink()
                raise ValueError('One scene exceeds the byte limit; shorten the scene or reduce encoding size.')
            midpoint = len(scenes) // 2
            encode(scenes[:midpoint])
            encode(scenes[midpoint:])
            return
        probe = json.loads(run('ffprobe', '-v', 'error', '-count_frames', '-show_streams',
                               '-show_format', '-of', 'json', path).stdout)
        stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        assert int(stream['nb_read_frames']) == frames
        assert (stream['codec_name'], stream['pix_fmt'], stream['r_frame_rate']) == ('h264', 'yuv420p', '30/1')
        decode = run('ffmpeg', '-v', 'error', '-i', path, '-f', 'null', '-')
        assert not decode.stderr
        parts.append({'path': name, 'scenes': [s['id'] for s in scenes],
                      'bytes': path.stat().st_size, 'sha256': digest(path), 'frames': frames,
                      'seconds': frames / data['fps'], 'start': start, 'end': end,
                      'full_decode_clean': True})
    for offset in range(0, len(data['scenes']), max_scenes):
        encode(data['scenes'][offset:offset + max_scenes])
    assert sum(part['frames'] for part in parts) == data['frames'], 'parts must cover the full timeline once'
    write('parts.json', {'max_bytes': max_bytes, 'parts': parts})
    # Remove derivatives from a previous grouping only after the new parts pass QA.
    expected_names = {part['path'] for part in parts}
    for old_part in BUILD.glob('part-*.mp4'):
        if old_part.name not in expected_names:
            old_part.unlink()
    html = (ROOT / 'player.html').read_text().replace('__PARTS_JSON__', json.dumps(parts))
    (BUILD / 'player.html').write_text(html)
    return parts



def export_preview():
    """Export the verified fictional demo; no new synthesis or rendering is needed."""
    qa = json.loads((BUILD / 'qa/qa.json').read_text())
    verification = json.loads((BUILD / 'source-verification.json').read_text())
    master = BUILD / 'master.mp4'
    assert digest(master) == qa['master_sha256'], 'master changed since QA'
    assert verification['source_sha256'] == digest(ROOT / 'inventory.py'), 'fixture source changed'
    scene = json.loads((BUILD / 'scenes.json').read_text())['scenes'][1]
    timestamp = scene['start'] + scene['highlights'][1]['start'] + 0.1
    preview = ROOT / 'preview'
    preview.mkdir(exist_ok=True)
    shutil.copy2(master, preview / 'demo.mp4')
    run('ffmpeg', '-v', 'error', '-y', '-ss', timestamp, '-i', master,
        '-frames:v', '1', preview / 'demo.png')
    gif = preview / 'demo.gif'
    filters = ('[0:v]fps=10,scale=800:-1:flags=lanczos,split[a][b];'
               '[a]palettegen=max_colors=128:stats_mode=diff[p];'
               '[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle')
    run('ffmpeg', '-v', 'error', '-y', '-i', master, '-filter_complex', filters,
        '-loop', '0', gif)
    probe = json.loads(run('ffprobe', '-v', 'error', '-count_frames', '-show_streams',
                           '-show_format', '-of', 'json', gif).stdout)
    stream = probe['streams'][0]
    assert (stream['width'], stream['height']) == (800, 450)
    assert abs(float(probe['format']['duration']) - qa['duration']) <= 0.1
    assert int(stream['nb_read_frames']) > 1
    decoded = run('ffmpeg', '-v', 'error', '-i', gif, '-f', 'null', '-')
    assert not decoded.stderr
    report = {'source': 'independently authored fictional inventory fixture',
              'source_git_blob': verification['source_git_blob'],
              'temporary_local_speech': True, 'paid_tts_calls': 0,
              'duration_seconds': qa['duration'], 'frames': qa['frames'],
              'video': {'path': 'demo.mp4', 'bytes': (preview / 'demo.mp4').stat().st_size,
                        'sha256': digest(preview / 'demo.mp4')},
              'screenshot': {'path': 'demo.png', 'at_seconds': timestamp,
                             'sha256': digest(preview / 'demo.png')},
              'gif': {'path': 'demo.gif', 'bytes': gif.stat().st_size, 'sha256': digest(gif),
                      'width': 800, 'height': 450, 'fps': 10,
                      'frames': int(stream['nb_read_frames']),
                      'duration_seconds': float(probe['format']['duration']),
                      'full_decode_clean': True, 'audio': False},
              'full_decode_clean': qa['decode_errors_empty'],
              'caption_timing': 'proportional estimate; not forced alignment'}
    (preview / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--export-preview', action='store_true',
                        help='export the verified fictional MP4, GIF and captured frame into preview/')
    parser.add_argument('--mode', choices=['debugger', 'lines'], default='debugger')
    parser.add_argument('--max-bytes', type=int, default=15_000_000)
    parser.add_argument('--max-scenes-per-part', type=int, default=2)
    args = parser.parse_args()
    if args.export_preview:
        export_preview()
        return
    scenes, trace = stage(args.mode)
    audio(scenes)
    data = prepare(trace, args.mode)
    check_trace(data)
    for arguments in [('render.py', '--samples'), ('render.py', '--determinism'),
                      ('render.py',), ('qa.py',)]:
        completed = run(sys.executable, *arguments)
        print(completed.stdout.decode()[-1200:], flush=True)
    check_encoded_trace(data)
    completed = run(sys.executable, 'package.py')
    print(completed.stdout.decode()[-1200:], flush=True)
    parts = split_parts(data, args.max_bytes, args.max_scenes_per_part)
    print(json.dumps({'build': str(BUILD), 'parts': parts, 'temporary_audio': True}, indent=2))


if __name__ == '__main__':
    main()
