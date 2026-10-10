"""Per-scene Gemini speech with provenance and key-less reuse (references/tts.md).

The transcript and the speaking style travel in separate fields, so the model reads only
the transcript. The returned WAV is kept exactly as received. GEMINI_API_KEY is read
only when a scene has no matching audio yet; it is never printed or stored.
"""
import base64
import hashlib
import json
import os
import pathlib
import time
import urllib.error
import urllib.request
import wave

MODEL = 'gemini-3.8-flash-lite-tts'
ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/interactions'
MAX_SECONDS_PER_CHAR = 0.45


def _find_audio(node):
    if isinstance(node, dict):
        if node.get('type') == 'audio' and isinstance(node.get('data'), str):
            return node
        node = list(node.values())
    if isinstance(node, list):
        for value in node:
            found = _find_audio(value)
            if found:
                return found
    return None


def _request(text, voice, style, key):
    body = {'model': MODEL,
            'input': [{'type': 'user_input', 'content': [{
                'type': 'text', 'text': text,
                'annotations': [{'type': 'speech_metadata', 'style': style}]}]}],
            'response_format': {'type': 'audio'},
            'generation_config': {'speech_config': [{'voice': voice}]}}
    request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), headers={
        'Content-Type': 'application/json', 'x-goog-api-key': key})
    return json.load(urllib.request.urlopen(request, timeout=180))


def synthesize(wav, text, voice, style, attempts=4):
    """Write wav + wav-metadata.json, or reuse them when text/model/voice/style match.

    Returns 'reused' or 'synthesized'. Never overwrites audio whose metadata disagrees
    unless the transcript itself changed (a new script is a new scene recording).
    """
    wav = pathlib.Path(wav)
    meta = wav.with_name(wav.stem + '-metadata.json')
    if wav.exists() and meta.exists():
        old = json.loads(meta.read_text())
        if (old.get('text'), old.get('model'), old.get('voice'), old.get('style')) == (text, MODEL, voice, style):
            assert old.get('sha256') == hashlib.sha256(wav.read_bytes()).hexdigest(), f'{wav} changed after synthesis'
            return 'reused'
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        raise SystemExit(f'{wav.name}: no matching audio and GEMINI_API_KEY is missing; no other TTS is substituted.')
    for attempt in range(1, attempts + 1):
        try:
            response = _request(text, voice, style, key)
            break
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == attempts:
                raise SystemExit(f'{wav.name}: Gemini TTS HTTP {error.code}')
        except urllib.error.URLError:
            if attempt == attempts:
                raise
        time.sleep(4 * attempt)
    audio = response.get('output_audio') or _find_audio(response.get('steps'))
    assert audio and audio.get('mime_type', '').startswith('audio/wav'), f'{wav.name}: no WAV audio returned'
    raw = base64.b64decode(audio['data'])
    wav.parent.mkdir(parents=True, exist_ok=True)
    tmp = wav.with_suffix('.part')
    tmp.write_bytes(raw)
    with wave.open(str(tmp)) as w:
        seconds = w.getnframes() / w.getframerate()
        rate = w.getframerate()
    if not 0.5 < seconds < len(text) * MAX_SECONDS_PER_CHAR + 3:
        tmp.unlink()
        raise SystemExit(f'{wav.name}: implausible speech length {seconds:.2f}s for {len(text)} characters')
    tmp.replace(wav)
    meta.write_text(json.dumps({
        'text': text, 'model': MODEL, 'voice': voice, 'style': style,
        'id': response.get('id'), 'mime_type': audio.get('mime_type'), 'usage': response.get('usage'),
        'seconds': seconds, 'sample_rate': rate, 'attempt': attempt,
        'sha256': hashlib.sha256(raw).hexdigest(), 'temporary': False}, ensure_ascii=False, indent=2))
    return 'synthesized'
