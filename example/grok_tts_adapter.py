"""Opt-in xAI Grok TTS: preserve the returned audio, derive header-repaired pipeline WAVs,
record provenance, reuse offline without reading the key.

One take (default for Grok): every scene in ONE request with character timestamps, then cut
per-scene WAVs at the pauses between scenes. One voice performance keeps tone and pace even.
    python example/grok_tts_adapter.py --scenes-json scenes-draft.json --out-dir audio
Per scene (one request per scene, cheaper to redo a single scene):
    python example/grok_tts_adapter.py --text '설명 영상입니다.' --wav build/audio/scene-01.wav
Requires XAI_API_KEY only when audio is genuinely missing. Paid per character; get approval first.

Why a repaired copy: as of 2026-11 the unary POST /v1/tts response with codec=wav carries a
streaming-style RIFF header whose RIFF and data sizes are placeholders (0x7fffffff-ish).
`wave` then reports hours of audio and ffmpeg's full decode ends with "corrupt input packet".
The original bytes are kept unchanged as scene-NN.xai-original.wav; the pipeline WAV
carries the same PCM bytes (hash recorded for both) behind a header with the true sizes.
"""
import argparse
import base64
import hashlib
import json
import os
import pathlib
import struct
import tempfile
import time
import urllib.error
import urllib.request

ENDPOINT = 'https://api.x.ai/v1/tts'
MODEL = 'xai-tts'          # the endpoint takes no model field; this names the provider route
SAMPLE_RATE = 48000
PRICE_NOTE = '$15.00 per 1M input characters (docs.x.ai/developers/models, checked 2026-11-10)'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def split_wav(data):
    """Return (fmt_chunk, pcm) using the real byte length; ignore placeholder size fields."""
    if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise ValueError('Response is not RIFF/WAVE')
    i, fmt = 12, None
    while i + 8 <= len(data):
        cid, size = data[i:i + 4], struct.unpack('<I', data[i + 4:i + 8])[0]
        if cid == b'fmt ':
            fmt = data[i + 8:i + 8 + size]
        elif cid == b'data':
            if fmt is None:
                raise ValueError('data chunk before fmt chunk')
            pcm = data[i + 8:]
            if len(pcm) % 2:
                pcm = pcm[:-1]
            return fmt, pcm
        i += 8 + size + (size & 1)
    raise ValueError('No data chunk')


def check_fmt(fmt):
    tag, channels, rate, _, align, bits = struct.unpack('<HHIIHH', fmt[:16])
    if (tag, channels, rate, bits, align) != (1, 1, SAMPLE_RATE, 16, 2):
        raise ValueError(f'Unexpected WAV format tag={tag} ch={channels} rate={rate} bits={bits}')
    return channels, rate, bits


def build_wav(fmt, pcm):
    return (b'RIFF' + struct.pack('<I', 4 + 8 + len(fmt) + 8 + len(pcm)) + b'WAVE'
            + b'fmt ' + struct.pack('<I', len(fmt)) + fmt
            + b'data' + struct.pack('<I', len(pcm)) + pcm)


def _request(text, voice, language, speed, key, with_timestamps=False):
    body = dict(text=text, voice_id=voice, language=language,
                output_format=dict(codec='wav', sample_rate=SAMPLE_RATE))
    if with_timestamps:
        body['with_timestamps'] = True
    if speed != 1.0:
        body['speed'] = speed
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode('utf-8'), method='POST',
                                 headers={'Authorization': f'Bearer {key}',
                                          'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = resp.read()
            headers = {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as e:  # surface the server message, never the key
        raise RuntimeError(f'xAI TTS HTTP {e.code}: {e.read()[:300]!r}') from None
    return body, data, headers, time.time() - t0


def synthesize(wav, text, voice='perseus', language='ko', speed=1.0):
    """Return 'synthesized' or 'reused'. Refuse partial, changed or mismatched caches."""
    if not text.strip():
        raise ValueError('Narration must not be empty')
    wav = pathlib.Path(wav)
    orig = wav.with_name(wav.stem + '.xai-original.wav')
    meta = wav.with_name(wav.stem + '-metadata.json')
    identity = dict(provider='xai', model=MODEL, text=text, voice=voice, language=language,
                    speed=speed)
    if any(p.exists() for p in (wav, orig, meta)):
        if not all(p.is_file() for p in (wav, orig, meta)):
            raise ValueError('Incomplete audio cache; choose a new output path or remove it explicitly')
        old = json.loads(meta.read_text())
        if any(old.get(k) != v for k, v in identity.items()):
            raise ValueError('Audio metadata differs; choose a new output path')
        if old.get('sha256') != digest(wav.read_bytes()) or \
                old.get('original_sha256') != digest(orig.read_bytes()):
            raise ValueError('Audio changed after synthesis')
        return 'reused'

    key = os.environ.get('XAI_API_KEY')  # lazy: only when audio is genuinely missing
    if not key:
        raise SystemExit('XAI_API_KEY is not set; reuse needs no key, new synthesis does')
    body, data, headers, elapsed = _request(text, voice, language, speed, key)
    fmt, pcm = split_wav(data)
    channels, rate, bits = check_fmt(fmt)
    fixed = build_wav(fmt, pcm)
    seconds = len(pcm) / (rate * channels * bits // 8)
    if seconds <= 0.2 or seconds > max(60.0, len(text) * 0.6):
        raise ValueError(f'Implausible audio length {seconds:.2f}s for {len(text)} chars')
    record = dict(identity, adapter_version=1, endpoint=ENDPOINT, request=dict(body, text='<see text>'),
                  id=headers.get('x-trace-id'), usage=dict(input_characters=len(text)),
                  price_note=PRICE_NOTE, estimated_cost_usd=round(len(text) * 15 / 1e6, 6),
                  response_content_type=headers.get('content-type'),
                  response_date=headers.get('date'), elapsed_s=round(elapsed, 3),
                  mime_type='audio/wav', original_file=orig.name,
                  original_mime_type=headers.get('content-type'), original_sha256=digest(data),
                  original_header_sizes=dict(riff=struct.unpack('<I', data[4:8])[0]),
                  pcm_sha256=digest(pcm), sha256=digest(fixed), seconds=seconds,
                  sample_rate=rate, channels=channels, bits=bits, attempt=1, temporary=False,
                  style=None,
                  note='xAI Grok TTS. Original response kept byte-for-byte; pipeline WAV has '
                       'identical PCM with true RIFF/data sizes. Naturalness not human-verified.')
    wav.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.xai-', dir=wav.parent) as tmp:
        t_orig, t_wav = pathlib.Path(tmp) / 'o.wav', pathlib.Path(tmp) / 'w.wav'
        t_orig.write_bytes(data)
        t_wav.write_bytes(fixed)
        t_orig.replace(orig)
        t_wav.replace(wav)
        meta.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return 'synthesized'


SEPARATOR = '\n\n'


def cut_samples(texts, chars, times, rate, n_samples, sep=SEPARATOR):
    """Sample index where each scene after the first starts.

    The cut sits in the middle of the pause between the last spoken character of scene i and
    the first character of scene i+1, using the returned per-character timestamps.
    """
    full = sep.join(texts)
    if ''.join(chars) != full or len(chars) != len(times):
        raise ValueError('Timestamps do not map 1:1 onto the request text; refusing to cut')
    cuts, pos = [], 0
    for k, t in enumerate(texts[:-1]):
        end_idx = pos + len(t.rstrip()) - 1
        start_idx = pos + len(t) + len(sep)
        while full[start_idx].isspace():
            start_idx += 1
        a, b = times[end_idx][1], times[start_idx][0]
        if b < a:
            raise ValueError(f'Scene {k + 2} starts before scene {k + 1} ends in the timestamps')
        cuts.append(min(n_samples, max(0, round((a + b) / 2 * rate))))
        pos += len(t) + len(sep)
    if cuts != sorted(cuts) or (cuts and (cuts[0] <= 0 or cuts[-1] >= n_samples)):
        raise ValueError('Cut points are not strictly inside the take')
    return cuts


def synthesize_take(out_dir, texts, voice='perseus', language='ko', speed=1.0, request=None):
    """One request for all scenes; writes take files plus scene-NN.wav slices. Returns status."""
    if not texts or any(not t.strip() for t in texts):
        raise ValueError('Every scene needs narration')
    out = pathlib.Path(out_dir)
    meta = out / 'take-metadata.json'
    files = [out / 'take.xai-response.json', out / 'take.xai-original.wav', out / 'take.wav']
    scenes = [out / f'scene-{k + 1:02d}.wav' for k in range(len(texts))]
    identity = dict(provider='xai', model=MODEL, mode='one-take', texts=list(texts), voice=voice,
                    language=language, speed=speed, separator=SEPARATOR)
    if meta.exists() or any(p.exists() for p in files + scenes):
        if not meta.is_file() or not all(p.is_file() for p in files + scenes):
            raise ValueError('Incomplete take cache; choose a new output dir or remove it explicitly')
        old = json.loads(meta.read_text())
        if any(old.get(k) != v for k, v in identity.items()):
            raise ValueError('Take metadata differs from the plan; choose a new output dir')
        hashes = [digest(p.read_bytes()) for p in files] + [digest(p.read_bytes()) for p in scenes]
        if hashes != old['file_sha256'] + [x['sha256'] for x in old['scenes']]:
            raise ValueError('Take audio changed after synthesis')
        return 'reused'

    full = SEPARATOR.join(texts)
    if request is None:
        key = os.environ.get('XAI_API_KEY')  # lazy: only when audio is genuinely missing
        if not key:
            raise SystemExit('XAI_API_KEY is not set; reuse needs no key, new synthesis does')
        body, raw, headers, elapsed = _request(full, voice, language, speed, key, with_timestamps=True)
    else:  # injected for offline tests
        body, raw, headers, elapsed = request(full)
    resp = json.loads(raw)
    audio = base64.b64decode(resp['audio'])
    fmt, pcm = split_wav(audio)
    channels, rate, bits = check_fmt(fmt)
    frame = channels * bits // 8
    n = len(pcm) // frame
    seconds = n / rate
    if seconds <= 0.2 or seconds > max(60.0, len(full) * 0.6):
        raise ValueError(f'Implausible audio length {seconds:.2f}s for {len(full)} chars')
    ts = resp['audio_timestamps']
    cuts = cut_samples(texts, ts['graph_chars'], ts['graph_times'], rate, n)
    bounds = [0] + cuts + [n]
    slices = [pcm[bounds[k] * frame:bounds[k + 1] * frame] for k in range(len(texts))]
    if b''.join(slices) != pcm:
        raise AssertionError('Scene slices do not reassemble the take byte-for-byte')
    fixed = build_wav(fmt, pcm)
    scene_wavs = [build_wav(fmt, x) for x in slices]
    record = dict(identity, adapter_version=2, endpoint=ENDPOINT,
                  request=dict(body, text='<texts joined by separator>'),
                  id=headers.get('x-trace-id'), usage=dict(input_characters=len(full)),
                  price_note=PRICE_NOTE, estimated_cost_usd=round(len(full) * 15 / 1e6, 6),
                  response_date=headers.get('date'), elapsed_s=round(elapsed, 3),
                  reported_duration_s=resp.get('duration'), seconds=seconds, sample_rate=rate,
                  channels=channels, bits=bits, original_header_sizes=dict(riff=struct.unpack('<I', audio[4:8])[0]),
                  pcm_sha256=digest(pcm), cut_samples=cuts,
                  reassembly_check='concatenated scene PCM == take PCM (byte-identical)',
                  file_names=[p.name for p in files],
                  file_sha256=[digest(raw), digest(audio), digest(fixed)],
                  scenes=[dict(file=p.name, text=t, start_s=bounds[k] / rate,
                               seconds=(bounds[k + 1] - bounds[k]) / rate, sha256=digest(w),
                               pcm_sha256=digest(x))
                          for k, (p, t, w, x) in enumerate(zip(scenes, texts, scene_wavs, slices))],
                  note='One Grok take with per-character timestamps; scenes cut mid-pause. '
                       'Original JSON response and decoded WAV kept unchanged. '
                       'Naturalness not human-verified.')
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.xai-', dir=out) as tmp:
        staged = []
        for p, data in zip(files + scenes, [raw, audio, fixed] + scene_wavs):
            t = pathlib.Path(tmp) / p.name
            t.write_bytes(data)
            staged.append((t, p))
        for t, p in staged:
            t.replace(p)
        meta.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return 'synthesized'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument('--scenes-json', type=pathlib.Path, help='one take: list of scenes with "narration"')
    src.add_argument('--text')
    src.add_argument('--text-file', type=pathlib.Path)
    parser.add_argument('--out-dir', type=pathlib.Path, help='one take: directory for take + scene WAVs')
    parser.add_argument('--wav', type=pathlib.Path, help='per scene: output WAV')
    parser.add_argument('--voice', default='perseus')
    parser.add_argument('--language', default='ko')
    parser.add_argument('--speed', type=float, default=1.0)
    args = parser.parse_args()
    if args.scenes_json:
        plan = json.loads(args.scenes_json.read_text())
        plan = plan['scenes'] if isinstance(plan, dict) else plan
        texts = [x['narration'] for x in plan]
        print(synthesize_take(args.out_dir or args.scenes_json.parent / 'audio', texts,
                              args.voice, args.language, args.speed))
        return
    if not args.wav:
        parser.error('--wav is required for per-scene synthesis')
    narration = args.text if args.text is not None else args.text_file.read_text(encoding='utf-8')
    print(synthesize(args.wav, narration, args.voice, args.language, args.speed))


if __name__ == '__main__':
    main()
