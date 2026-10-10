"""Build one language variant of an explainer with the shared pipeline.

Used by example-concept/ and example-architecture/. Each caller supplies a scene plan,
a source record and a fidelity inventory; this module stages the shared scripts into
<example>/build/<lang>/, synthesises or reuses per-scene speech, then runs
prepare -> render (samples, determinism, master) -> qa -> package, and exports the
verified master and its derivatives into <example>/preview/.
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

import gemini_tts

SHARED = pathlib.Path(__file__).resolve().parent
LANG_TAG = {'ko': 'kor', 'en': 'eng'}


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def run(build, *args):
    done = subprocess.run(list(map(str, args)), cwd=build, capture_output=True)
    if done.returncode:
        sys.stderr.write(done.stdout.decode()[-3000:] + done.stderr.decode()[-3000:])
        raise SystemExit(f'failed: {" ".join(map(str, args))}')
    return done.stdout.decode()


def scene_records(plan, lang):
    """Plan rows hold {'ko': ..., 'en': ...} for every spoken or displayed string."""
    def pick(v):
        return v[lang] if isinstance(v, dict) and set(v) == {'ko', 'en'} else v

    def walk(v):
        v = pick(v)
        if isinstance(v, dict):
            return {k: walk(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [walk(x) for x in v]
        return v

    scenes = []
    for index, row in enumerate(plan, 1):
        s = walk(row)
        scenes.append(dict(
            id=index, title=s['title'], section=s['section'], claim=s['claim'],
            narration=s['narration'], transition_keyword=s['transition'],
            cue_definitions=[dict(keyword=k, text=t) for k, t in s['cues']],
            diagram=dict(objects=s['objects']), visual=s['visual'], exceptions=s['exceptions'],
            source_location=s['source'],
            metaphor='Positions, sizes and counts in the diagram are illustrative, not measured data.'))
    return scenes


def stage(root, lang, scenes, config, source_record):
    build = root / 'build' / lang
    for sub in ('assets', 'audio', 'qa'):
        (build / sub).mkdir(parents=True, exist_ok=True)
    for name in ('prepare.py', 'render.py', 'qa.py', 'package.py', 'drawlib.py', 'asr_check.py'):
        shutil.copy2(SHARED / name, build / name)
    shutil.copy2(SHARED.parent / 'LICENSE', build / 'LICENSE')
    shutil.copy2(root / 'README.md', build / 'README.md')
    shutil.copy2(SHARED / 'assets/font-license.txt', build / 'assets/font-license.txt')
    font = SHARED / 'assets/NotoSansCJKkr-Regular.otf'
    if not font.is_file():
        raise SystemExit('Fetch the shared OFL font first: bash example/assets/fetch-font.sh')
    shutil.copy2(font, build / 'assets/NotoSansCJKkr-Regular.otf')
    (build / 'scenes-draft.json').write_text(json.dumps(scenes, ensure_ascii=False, indent=2))
    (build / 'source-verification.json').write_text(json.dumps(source_record, ensure_ascii=False, indent=2))
    base = json.loads((SHARED / 'config.json').read_text())
    base.update(config, language=LANG_TAG[lang],
                package_extra_files=['source-verification.json', 'asr_check.py'])
    (build / 'config.json').write_text(json.dumps(base, ensure_ascii=False, indent=2))
    return build


def speech(root, build, lang, scenes, voice, style):
    """Audio lives in <example>/audio-cache/<lang>/ so a clean build never pays twice."""
    cache = root / 'audio-cache' / lang
    counts = {'reused': 0, 'synthesized': 0}
    for s in scenes:
        wav = cache / f'scene-{s["id"]:02d}.wav'
        counts[gemini_tts.synthesize(wav, s['narration'], voice, style)] += 1
        for f in (wav, wav.with_name(wav.stem + '-metadata.json')):
            shutil.copy2(f, build / 'audio' / f.name)
    return counts


def fidelity(build, scenes, review):
    covered = {s['id'] for s in scenes}
    for unit in review['inventory']:
        assert set(unit['scenes']) <= covered, unit
    assert all(s['exceptions'] and s['source_location'] for s in scenes)
    review = dict(review, scene_map=[dict(scene=s['id'], source=s['source_location'], claim=s['claim'],
                                          qualification=s['exceptions'], visual=s['visual']) for s in scenes],
                  private_source_text_packaged=False, independent_review=False,
                  full_human_listening=False, asr_pronunciation_check=False,
                  asr_similarity_check='qa/asr.json when WHISPER_MODEL was set; a transcript similarity, not a pronunciation grade',
                  forced_alignment=False)
    (build / 'source-fidelity-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2))


def export(root, build, lang, gif_scene, gif_seconds=9.0):
    qa = json.loads((build / 'qa/qa.json').read_text())
    master = build / 'master.mp4'
    assert digest(master) == qa['master_sha256'], 'master changed since QA'
    data = json.loads((build / 'scenes.json').read_text())
    scene = data['scenes'][gif_scene - 1]
    start = max(scene['start'], scene['start'] + scene['transition_at'] - 2.0)
    preview = root / 'preview'
    preview.mkdir(exist_ok=True)
    shutil.copy2(master, preview / f'{lang}.mp4')
    shutil.copy2(build / 'captions.srt', preview / f'{lang}.srt')
    shot = scene['start'] + min(scene['duration'] - .1, scene['transition_at'] + 3.0)
    run(build, 'ffmpeg', '-v', 'error', '-y', '-ss', shot, '-i', master, '-frames:v', '1', preview / f'{lang}.png')
    filters = ('[0:v]fps=10,scale=800:-1:flags=lanczos,split[a][b];'
               '[a]palettegen=max_colors=128:stats_mode=diff[p];'
               '[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle')
    gif = preview / f'{lang}.gif'
    run(build, 'ffmpeg', '-v', 'error', '-y', '-ss', start, '-t', gif_seconds, '-i', master,
        '-filter_complex', filters, '-loop', '0', gif)
    probe = json.loads(run(build, 'ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-of', 'json', gif))
    assert int(probe['streams'][0]['nb_read_frames']) > 1
    assert not subprocess.run(['ffmpeg', '-v', 'error', '-i', str(gif), '-f', 'null', '-'],
                              capture_output=True).stderr
    entry = dict(language=lang, duration_seconds=qa['duration'], frames=qa['frames'],
                 video=dict(path=f'{lang}.mp4', bytes=(preview / f'{lang}.mp4').stat().st_size,
                            sha256=digest(preview / f'{lang}.mp4')),
                 captions=dict(path=f'{lang}.srt', sha256=digest(preview / f'{lang}.srt'),
                               timing='proportional estimate inside measured scenes; not forced alignment'),
                 screenshot=dict(path=f'{lang}.png', at_seconds=shot),
                 gif=dict(path=f'{lang}.gif', bytes=gif.stat().st_size, start_seconds=start,
                          seconds=gif_seconds, fps=10, width=800, audio=False),
                 full_decode_clean=qa['decode_errors_empty'],
                 asr=asr_summary(build),
                 tts=json.loads((build / 'tts-provenance.json').read_text())['note'])
    path = preview / 'verification.json'
    report = json.loads(path.read_text()) if path.exists() else {}
    report[lang] = entry
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return entry


def asr_summary(build):
    path = build / 'qa' / 'asr.json'
    if not path.exists():
        return 'not run'
    report = json.loads(path.read_text())
    return dict(tool=report['tool'], model=report['model'], min_similarity=report['min_similarity'],
                per_scene=[r['similarity'] for r in report['scenes']], scope=report['scope'])


def build_variant(root, lang, plan, config, source_record, review, voice, style, gif_scene):
    root = pathlib.Path(root)
    scenes = scene_records(plan, lang)
    build = stage(root, lang, scenes, config[lang], source_record)
    counts = speech(root, build, lang, scenes, voice, style[lang])
    print(lang, 'speech', counts, flush=True)
    fidelity(build, scenes, review)
    py = sys.executable
    steps = [('prepare.py',), ('render.py', '--samples'), ('render.py', '--determinism'),
             ('render.py',), ('qa.py',)]
    # Optional ASR runs before packaging so qa/asr.json travels in the archive.
    if os.environ.get('WHISPER_MODEL') and shutil.which('whisper-cli'):
        steps.append(('asr_check.py', '.', lang))
    steps.append(('package.py',))
    for step in steps:
        out = run(build, py, *step)
        print(lang, ' '.join(step), '->', out.strip().splitlines()[-1] if out.strip() else 'ok', flush=True)
    entry = export(root, build, lang, gif_scene)
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return entry
