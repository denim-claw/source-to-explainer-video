"""Whitelist archive + toolchain provenance + a REAL extracted-archive replay.

The archive is built LAST and its own hash/size go into artifact-verification.json
OUTSIDE the archive (a document that embeds the hash of the archive containing it is
self-referential).
"""
import hashlib
import importlib.metadata as md
import json
import pathlib
import shutil
import subprocess
import sys
import wave
import zipfile

R = pathlib.Path(__file__).parent
Q = R / 'qa'
D = json.loads((R / 'scenes.json').read_text())
S = D['scenes']
qa = json.loads((Q / 'qa.json').read_text())


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, check=True, **kw)


assert qa['frames'] == D['frames'] and qa['determinism'] and qa['decode_errors_empty']
assert not qa['author_text_collisions'] and not qa['author_node_label_card_collisions']
V = pathlib.Path(qa['master'])
assert sha(V) == qa['master_sha256'], 'master changed since QA — re-run qa.py'

# --- provenance ------------------------------------------------------------
provenance = []
for i, s in enumerate(S):
    wav = R / f'audio/scene-{i + 1:02d}.wav'
    if not wav.exists():
        provenance.append(dict(scene=i + 1, present=False, note='placeholder/replace with real narration'))
        continue
    with wave.open(str(wav)) as w:
        seconds = w.getnframes() / w.getframerate()
    entry = dict(scene=i + 1, seconds=seconds, sha256=sha(wav))
    meta = wav.with_name(wav.stem + '-metadata.json')
    if meta.exists():
        entry.update(json.loads(meta.read_text()))
    provenance.append(entry)
real_tts = sum(1 for p in provenance if p.get('model'))
narration = R / 'narration.flac' if (R / 'narration.flac').exists() else R / 'narration.wav'
with wave.open(str(narration)) as w:
    narration_seconds = w.getnframes() / w.getframerate()
(R / 'tts-provenance.json').write_text(json.dumps(dict(
    scenes=provenance, scene_count=len(provenance), real_tts_scenes=real_tts,
    narration_seconds=narration_seconds,
    note='placeholder audio is room tone, not speech' if real_tts < len(provenance) else 'all scenes synthesised',
), ensure_ascii=False, indent=2))

names = ['pillow', 'numpy', 'fonttools']
versions = {}
for n in names:
    try:
        versions[n] = md.version(n)
    except md.PackageNotFoundError:
        versions[n] = None
(R / 'requirements.txt').write_text('\n'.join(f'{k}=={v}' for k, v in sorted(versions.items()) if v) + '\n')
ffmpeg = run(['ffmpeg', '-version']).stdout.decode()
ffprobe = run(['ffprobe', '-version']).stdout.decode()
native_cairo = None
try:
    import cairocffi
    native_cairo = cairocffi.cairo_version_string()
except Exception:
    pass
(R / 'toolchain.json').write_text(json.dumps(dict(
    python=sys.version, python_executable=sys.executable, packages=versions,
    native_Cairo_version=native_cairo,
    native_Cairo_note='a system Cairo shared library is required only for the optional SVG annotation layer',
    ffmpeg=ffmpeg, ffprobe=ffprobe,
    encoded_encoder_tag=qa.get('encoder_tag'), renderer=qa['renderer'],
    FFmpeg_binary_bundled=False,
), ensure_ascii=False, indent=2))

# --- poster + derivatives --------------------------------------------------
poster_time = S[min(1, len(S) - 1)]['start'] + S[min(1, len(S) - 1)]['duration'] * .82
run(['ffmpeg', '-v', 'error', '-y', '-ss', str(poster_time), '-i', str(V), '-frames:v', '1', '-q:v', '2', str(R / 'poster.jpg')])

ALLOWED = ['README.md', 'LICENSE', 'requirements.txt', 'toolchain.json', 'tts-provenance.json',
           'config.json', 'design.py', 'drawlib.py', 'prepare.py', 'render.py', 'qa.py',
           'fidelity.py', 'package.py', 'make_demo_audio.sh',
           'scenes-draft.json', 'scenes.json', 'script.md', 'storyboard.md', 'captions.srt',
           'narration.wav', 'narration.flac', 'poster.jpg',
           'render-command.json', 'render-result.json', 'render-ffmpeg.log', 'render.log',
           'source-fidelity-review.json', 'source-map.json',
           'assets/README.md', 'assets/fetch-font.sh', 'assets/font-license.txt',
           'assets/NotoSansCJKkr-Regular.otf']
# Renderer adapters can explicitly whitelist their local support files.
for extra in json.loads((R / 'config.json').read_text()).get('package_extra_files', []):
    member = pathlib.PurePosixPath(extra)
    assert not member.is_absolute() and '..' not in member.parts, extra
    assert (R / extra).is_file(), f'missing package support file: {extra}'
    ALLOWED.append(extra)
ALLOWED += [f'audio/scene-{i + 1:02d}.wav' for i in range(len(S))]
ALLOWED += [f'audio/scene-{i + 1:02d}-metadata.json' for i in range(len(S))
            if (R / f'audio/scene-{i + 1:02d}-metadata.json').exists()]
ALLOWED += [str(p.relative_to(R)) for p in Q.iterdir()
            if p.is_file() and (p.suffix in ('.json', '.txt')
                                or p.name.startswith(('encoded-sheet-', 'cuts-sheet-', 'phone-')))]
Z = R / 'source.zip'


def build():
    allow = sorted({p for p in ALLOWED if (R / p).is_file()})
    assert allow, 'nothing to archive'
    for p in allow:
        assert not p.endswith('.pdf') and 'private/' not in p and '.env' not in p
        assert '.venv' not in p and 'node_modules' not in p and not p.startswith('samples/')
    with zipfile.ZipFile(Z, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in allow:
            z.write(R / p, p)
    with zipfile.ZipFile(Z) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(allow)
        for member in z.namelist():
            assert not member.endswith('.pdf') and 'private/' not in member and '.env' not in member
    return len(allow)


count = build()

# --- real replay from the extracted archive --------------------------------
C = R / 'package-check'
if C.exists():
    shutil.rmtree(C)
C.mkdir()
with zipfile.ZipFile(Z) as z:
    z.extractall(C)
replay_code = """
import hashlib, json, pathlib, subprocess
import render
R = pathlib.Path.cwd()
S = render.S
times = [s['start'] + s['duration'] * .14 for s in S] + [s['start'] + s['duration'] * .82 for s in S]
hashes = {str(t): hashlib.sha256(render.renderAt(t).tobytes()).hexdigest() for t in times}
voice = R / 'narration.flac'
if not voice.exists():
    voice = R / 'narration.wav'
cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1280x720',
       '-r', '30', '-i', 'pipe:0', '-i', str(voice), '-c:v', 'libx264', '-preset', 'fast',
       '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '1',
       '-t', '2', '-movflags', '+faststart', str(R / 'package-replay.mp4')]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for frame in range(60):
    p.stdin.write(render.renderAt(frame / 30).tobytes())
p.stdin.close()
assert p.wait() == 0
q = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(R / 'package-replay.mp4'), '-f', 'null', '-'], capture_output=True)
assert q.returncode == 0 and not q.stderr, q.stderr
(R / 'replay-hashes.json').write_text(json.dumps(hashes))
print('package replay: 60 frames, 2 seconds, narrated MP4, full decode clean')
"""
replay = run([sys.executable, '-c', replay_code], cwd=C)
(Q / 'package-rerender.log').write_bytes(replay.stdout + replay.stderr)
expected = json.loads((Q / 'determinism.json').read_text())['hashes']
actual = json.loads((C / 'replay-hashes.json').read_text())
assert expected == actual, 'extracted archive does not reproduce the same frames'
probe = json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(C / 'package-replay.mp4')]).stdout)
vs = next(x for x in probe['streams'] if x['codec_type'] == 'video')
assert int(vs['nb_read_frames']) == 60
package_report = dict(passed=True, extracted_archive_real_replay=True, replay_frames=60,
                      replay_path=str(C / 'package-replay.mp4'), full_timeline_RGB_samples=len(expected),
                      same_RGB_frames=True, full_replay_decode_exit=0, decode_errors_empty=True,
                      bundled_narration_and_font_used=True, no_network_calls=True,
                      scope='a real 2-second narrated MP4 rendered from the extracted archive plus full-timeline timestamp RGB comparisons; NOT a second complete encode')
(Q / 'package-rerender.json').write_text(json.dumps(package_report, indent=2))
ALLOWED += ['qa/package-rerender.json', 'qa/package-rerender.log']
count = build()

with zipfile.ZipFile(Z) as z:
    members = z.namelist()
    assert z.testzip() is None
report = dict(
    master=dict(path=str(V), bytes=V.stat().st_size, sha256=sha(V)),
    source_zip=dict(path=str(Z), bytes=Z.stat().st_size, sha256=sha(Z), entries=count, CRC_errors=None),
    duration_seconds=qa['duration'], frames=qa['frames'], scene_count=len(S),
    narration_seconds=narration_seconds, real_tts_scenes=real_tts,
    qa=str(Q / 'qa.json'), source_fidelity=str(R / 'source-fidelity-review.json'),
    package_replay=str(Q / 'package-rerender.json'), tts_provenance=str(R / 'tts-provenance.json'),
    poster=str(R / 'poster.jpg'),
    publication_performed_by_this_build=False,
    published_status='not checked by this build; publishing is a separate explicit step',
    remaining_limits=[
        'no full continuous human listening and no ASR pronunciation check',
        'no independent content reviewer',
        'caption timing is a proportional estimate inside measured scenes, not forced alignment',
        'the package replay is 2 seconds plus timeline RGB samples, not a second full-length encode',
        'native Cairo/system dependency: same-machine RGB equality is not a cross-OS guarantee',
        'placeholder audio is not speech' if real_tts < len(provenance) else 'all scenes synthesised',
    ])
(R / 'artifact-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
