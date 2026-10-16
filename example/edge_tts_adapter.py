"""Opt-in Edge TTS: preserve MP3, decode WAV, record provenance, reuse offline.

python example/edge_tts_adapter.py --text '설명 영상입니다.' --wav build/audio/scene-01.wav
Requires edge-tts and ffmpeg. No API key; network service availability is not guaranteed.
"""
import argparse
import asyncio
import hashlib
import json
import pathlib
import subprocess
import tempfile
import wave

MODEL = 'edge-tts'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


async def _generate(text, voice, rate, pitch, output):
    import edge_tts  # lazy: verified reuse works without the package or network
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(output))


def synthesize(wav, text, voice='ko-KR-SunHiNeural', rate='+0%', pitch='+0Hz'):
    """Return synthesized/reused. Refuse partial, changed or mismatched cache files."""
    if not text.strip():
        raise ValueError('Narration must not be empty')
    wav = pathlib.Path(wav)
    mp3 = wav.with_suffix('.mp3')
    meta = wav.with_name(wav.stem + '-metadata.json')
    identity = dict(provider='edge', model=MODEL, text=text, voice=voice, rate=rate, pitch=pitch)
    if any(p.exists() for p in (wav, mp3, meta)):
        if not all(p.is_file() for p in (wav, mp3, meta)):
            raise ValueError('Incomplete audio cache; choose a new output path or remove it explicitly')
        old = json.loads(meta.read_text())
        if any(old.get(k) != v for k, v in identity.items()):
            raise ValueError('Audio metadata differs; choose a new output path')
        if old.get('sha256') != digest(wav) or old.get('original_sha256') != digest(mp3):
            raise ValueError('Audio changed after synthesis')
        return 'reused'
    wav.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.edge-', dir=wav.parent) as tmp:
        raw = pathlib.Path(tmp) / 'original.mp3'
        decoded = pathlib.Path(tmp) / 'decoded.wav'
        asyncio.run(_generate(text, voice, rate, pitch, raw))
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(raw),
                        '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s16le', str(decoded)],
                       check=True, capture_output=True)
        with wave.open(str(decoded)) as audio:
            sample_rate = audio.getframerate()
            seconds = audio.getnframes() / sample_rate
        if seconds <= 0:
            raise ValueError('Empty decoded audio')
        from importlib.metadata import version
        record = dict(identity, adapter_version=1, client_version=version('edge-tts'),
                      id=None, usage=None, mime_type='audio/wav',
                      original_mime_type='audio/mpeg', original_file=mp3.name,
                      original_sha256=digest(raw), sha256=digest(decoded),
                      seconds=seconds, sample_rate=sample_rate, attempt=1, temporary=False,
                      style=None, note='Edge TTS; no API key; naturalness not human-verified. '
                      'WAV is decoded from preserved original MP3, not native lossless speech.')
        raw.replace(mp3)
        decoded.replace(wav)
        meta.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return 'synthesized'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    text = parser.add_mutually_exclusive_group(required=True)
    text.add_argument('--text')
    text.add_argument('--text-file', type=pathlib.Path)
    parser.add_argument('--wav', type=pathlib.Path, required=True)
    parser.add_argument('--voice', default='ko-KR-SunHiNeural')
    parser.add_argument('--rate', default='+0%')
    parser.add_argument('--pitch', default='+0Hz')
    args = parser.parse_args()
    narration = args.text if args.text is not None else args.text_file.read_text(encoding='utf-8')
    print(synthesize(args.wav, narration, args.voice, args.rate, args.pitch))


if __name__ == '__main__':
    main()
