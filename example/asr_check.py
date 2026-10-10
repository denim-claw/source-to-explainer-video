"""Optional ASR check: transcribe each scene WAV with whisper.cpp and compare to the script.

    python asr_check.py <build-dir> <lang>     needs whisper-cli and WHISPER_MODEL=/abs/ggml-*.bin

Writes <build-dir>/qa/asr.json. A similarity score flags scenes worth a human listen;
it is not a pronunciation grade, and a small model mishears names and code identifiers.
Audio is cut into fixed windows, so a word split at a boundary can lower the score slightly.
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


def transcribe(wav, lang, model, window=15.0):
    """Fixed windows: on a whole 30 s file a small model sometimes skips the middle."""
    seconds = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                    str(wav)], check=True, capture_output=True, text=True).stdout)
    parts = []
    with tempfile.TemporaryDirectory() as tmp:
        start = 0.0
        while start < seconds:
            clip = pathlib.Path(tmp) / 'clip.wav'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-t', str(window), '-i', str(wav),
                            '-ar', '16000', '-ac', '1', str(clip)], check=True)
            out = pathlib.Path(tmp) / 'out'
            subprocess.run(['whisper-cli', '-m', model, '-l', lang, '-mc', '0', '-nt', '-otxt', '-of', str(out), str(clip)],
                           check=True, capture_output=True)
            parts.append(out.with_suffix('.txt').read_text().strip())
            start += window
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
