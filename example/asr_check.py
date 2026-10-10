"""Optional ASR check: transcribe each scene WAV with whisper.cpp and compare to the script.

    python asr_check.py <build-dir> <lang>     needs whisper-cli and WHISPER_MODEL=/abs/ggml-*.bin

Writes <build-dir>/qa/asr.json. A similarity score flags scenes worth a human listen;
it is not a pronunciation grade, and a small model mishears names and code identifiers.
Audio is cut at pauses (silencedetect) into windows of about 12 s.
"""
import difflib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile


def normalize(text):
    return re.sub(r'[^0-9a-z가-힣]', '', text.lower())


def pauses(wav):
    """Midpoints of silences, so windows end between words rather than inside one."""
    log = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(wav), '-af', 'silencedetect=n=-35dB:d=0.25',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', log)]
    return [(a + b) / 2 for a, b in zip(starts, ends)]


def transcribe(wav, lang, model, target=12.0, limit=25.0):
    """Cut at pauses near `target` seconds: on a whole 30 s file a small model can skip
    the middle, and a fixed cut can split a word."""
    seconds = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                    str(wav)], check=True, capture_output=True, text=True).stdout)
    cuts, start = [], 0.0
    for point in pauses(wav) + [seconds]:
        if point - start >= target or point >= seconds:
            assert point - start <= limit, f'{wav.name}: no pause within {limit}s after {start:.1f}s'
            cuts.append((start, point))
            start = point
    parts = []
    with tempfile.TemporaryDirectory() as tmp:
        for begin, end in cuts:
            if end - begin < 0.3:
                continue
            clip = pathlib.Path(tmp) / 'clip.wav'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(begin), '-t', str(end - begin), '-i', str(wav),
                            '-ar', '16000', '-ac', '1', str(clip)], check=True)
            out = pathlib.Path(tmp) / 'out'
            subprocess.run(['whisper-cli', '-m', model, '-l', lang, '-mc', '0', '-nt', '-otxt', '-of', str(out), str(clip)],
                           check=True, capture_output=True)
            parts.append(out.with_suffix('.txt').read_text(errors='replace').strip())
    return ' '.join(parts)


def main():
    build, lang = pathlib.Path(sys.argv[1]), sys.argv[2]
    model = os.environ.get('WHISPER_MODEL')
    if not model or not pathlib.Path(model).is_file():
        raise SystemExit('Set WHISPER_MODEL to a whisper.cpp ggml model file; nothing was checked.')
    scenes = json.loads((build / 'scenes.json').read_text())['scenes']
    rows = []
    for s in scenes:
        heard = transcribe(build / s['audio'], lang, model)
        score = difflib.SequenceMatcher(None, normalize(s['narration']), normalize(heard), autojunk=False).ratio()
        rows.append(dict(scene=s['id'], similarity=round(score, 3), script=s['narration'], heard=heard))
    report = dict(tool='whisper.cpp whisper-cli', model=pathlib.Path(model).name, language=lang,
                  scope='automatic transcript similarity per scene; not a human listen and not a pronunciation grade',
                  min_similarity=min(r['similarity'] for r in rows), scenes=rows)
    (build / 'qa' / 'asr.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    for r in rows:
        print(r['scene'], r['similarity'])


if __name__ == '__main__':
    main()
