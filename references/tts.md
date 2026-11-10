# TTS — measured narration with provenance

## Interface

- Synthesise **per scene**, not the whole script in one call. Per-scene gives you
  measured lengths, per-scene retry, partial reuse, and a usable provenance chain.
- Gemini: keep the **original WAV exactly as returned**. If the API returns a headered WAV,
  never strip and re-wrap it, and never guess the container.
- Store per scene: model, voice, request id, mime type, the exact script text, usage,
  measured duration, attempt number, and the WAV SHA256.
- Separate the "style" instruction from the transcript per the API's own schema; ask the
  model to speak only the transcript.

Compatibility note: the Gemini speech-generation route used here returns audio through an
`interactions`-style endpoint where transcript and `speech_metadata.style` are separate
fields. Re-check the current official schema before changing anything — do not invent
field names, and do not silently fall back to a different TTS.

## Optional Edge TTS (no API key)

**Default:** Edge TTS, with no API key and no separate API charge; the voice may sound
less natural. It is an online consumer speech service, not an offline engine, unlimited-use
promise or availability guarantee. Review service terms for your use. The builder prints
this default and its limitation. Never silently fall back between providers.

Before synthesis, offer this choice when asking is appropriate: "무료지만 다소 부자연스러울 수
있는 Edge TTS로 만들까요, 아니면 API 키가 필요한 더 자연스러운 Gemini TTS로 만들까요?"
If the user does not answer or has not been asked, proceed with Edge by default. Treat an
explicit preference for natural voice as Gemini and confirm the required key is configured;
never request the key in chat. A preference for free/no-key narration means Edge.

```sh
python -m pip install -r example/requirements-edge.txt
python example/edge_tts_adapter.py --text '장면별 설명입니다.' \
  --wav build/audio/scene-01.wav --voice ko-KR-SunHiNeural
# A UTF-8 file works too: --text-file narration.txt (instead of --text).
# Run again with identical inputs: prints reused without importing edge_tts or networking.
```

For example builders using `example/variant.py`, Edge is the default. Set `TTS_PROVIDER=gemini`
to choose Gemini before running that builder's existing command. Optional `TTS_VOICE` overrides
ko-KR-SunHiNeural / en-US-AriaNeural. Edge caches live under `audio-cache/edge/<lang>`;
Gemini caches are unchanged. Edge ignores the Gemini free-form style instruction, never
speaks it, and records style as null. The standalone adapter also accepts --rate and
--pitch; include these settings in cache identity.

Preserve scene-NN.mp3 exactly as received; decode scene-NN.wav via ffmpeg to mono 48 kHz
PCM s16le for the existing prepare/render pipeline. The WAV is not native lossless TTS.
Metadata records provider, client version, transcript, voice, rate, pitch, both hashes,
measured WAV length and original filename; unavailable request id / usage are null.
Copy the original MP3 with its WAV and metadata when staging. Partial/mismatched/tampered
caches fail closed; select a new output path or deliberately remove the old cache.
No network retries or automatic provider switch are made by this adapter.

If synthesis returns HTTP 403, first check the imported edge-tts version and path:
older clients can break when the service changes. 7.3.1 passed a live Korean smoke test;
7.2.7 returned 403 in the same environment. Do not infer success from offline cache tests.
Test offline: `python -m unittest discover -s example -p test_edge_tts_adapter.py -v`.
Naturalness and pronunciation still require human listening.

## Optional xAI Grok TTS (paid, `XAI_API_KEY`)

Opt-in only; Edge remains the default and there is no automatic switch between providers.
Endpoint `POST https://api.x.ai/v1/tts` with `text`, `voice_id`, `language` (`ko` for Korean)
and `output_format` (`codec: wav`, `sample_rate: 48000`); there is no model field.
Price checked 2026-11-10: $15.00 per 1M input characters (docs.x.ai/developers/models).
Tell the user the scene count and estimated cost and get approval before the first call.

```sh
# Default: one take for the whole plan, cut into audio/scene-NN.wav
python example/grok_tts_adapter.py --scenes-json scenes-draft.json --out-dir audio
# Per scene, when only one scene should be redone or a take is too long (>60,000 chars):
python example/grok_tts_adapter.py --text '장면별 설명입니다.' \
  --wav build/audio/scene-01.wav            # default --voice perseus, --language ko
# Run again with identical inputs: prints reused without reading XAI_API_KEY.
```

- **One take (default)**: scene narrations are joined with a blank line (`\n\n`) and sent with
  `with_timestamps: true`. The JSON response carries base64 audio plus `graph_chars` /
  `graph_times`, which map 1:1 onto the request text (checked; the adapter refuses to cut
  otherwise). Each cut sits midway between the last spoken character of a scene and the first
  character of the next (observed pause ≈0.3 s). The take's PCM must equal the concatenated
  scene PCM byte for byte. Keep `take.xai-response.json`, `take.xai-original.wav`, `take.wav`
  and `take-metadata.json` with the scene WAVs. Use scene gap 0 in the pipeline config.

- **Default voice `perseus`**: use it without an audition. It was chosen once by a user
  listening among 19 male voices (`GET /v1/tts/voices` lists ids and gender only). Audition
  other voices only on request. Rough autocorrelation F0 on one Korean sentence, for that
  optional audition: helios ~118 Hz, perseus ~123 Hz, altair ~133 Hz (flattest),
  kepler ~133 Hz. Pitch figures are estimates; pronunciation needs human listening.
- **WAV header quirk**: the unary response is a streaming-style RIFF whose RIFF/data sizes are
  placeholders (~0x7fffffff). `wave` then reports hours of audio and a full ffmpeg decode ends
  with `corrupt input packet`. The adapter keeps the response unchanged as
  `scene-NN.xai-original.wav`, validates fmt (PCM, mono, 48 kHz, 16-bit) and writes
  `scene-NN.wav` with identical PCM bytes and true sizes; both hashes plus `pcm_sha256` go in
  the metadata. This is a header repair, not a re-encode or a guessed container.
- Metadata: provider, voice, language, speed, transcript, `x-trace-id` as `id`, input
  character count as usage, estimated cost, measured seconds. The key is never recorded.
- Test offline: `python -m unittest discover -s example -p test_grok_tts_adapter.py -v`.

## Reuse rules (this is where money is saved)

```python
if wav.exists() and meta.exists():
    old = json.loads(meta.read_text())
    assert old["text"] == scene["narration"]
    assert old["model"] == MODEL and old["voice"] == VOICE
    return                      # reuse; no new call
KEY = load_key()                # lazy: only when audio is genuinely missing
```

- Validate script/model/voice/metadata **before** reading any credential. A missing key
  must not block re-render, QA or packaging of already-verified audio.
- Report reused-scene count and new-call count **separately**; never present a key-less
  reuse run as new synthesis.
- Never overwrite an existing WAV whose metadata disagrees — fail and let a human decide.

## Timing

- Measure `frames / sample_rate`. Do not trust a duration reported by the service.
- Concatenate scenes with a fixed gap (0.6 s is a good default) and state it.
- `atempo` only for a mild adjustment; re-measure after and rebuild every timestamp.
  Pitch is preserved by `atempo`; a *pitch-shifting* speed change is a different edit and
  must be described as such.
- If you must hit a target length, prefer cutting scope over speeding speech up.

## Captions

- Split narration at sentence boundaries, then at word boundaries into chunks that fit at
  most two lines at the real font width.
- Distribute each chunk's duration proportionally to its character count **inside the
  measured scene**, anchored so scene-level offsets stay exact.
- Report this as an estimate. Only claim true sync if you ran forced alignment or an ASR
  check — and say which one.

## QA on audio

- Peak, RMS, clipped-sample count at a stated analysis rate.
- Compare the raw WAV set against the concatenated narration: for lossless formats the
  PCM must be byte-identical after decode.
- None of these establish pronunciation quality or naturalness — human listening does.

## Reference implementation

`example/gemini_tts.py` implements the rules above for the Gemini interactions endpoint:
transcript and `speech_metadata.style` in separate fields, the returned WAV kept as is,
metadata with id/usage/sha256, reuse before the key is read, and a plausibility bound on
length. `example/asr_check.py` adds an optional whisper.cpp transcript comparison per
scene; report it as a similarity score, never as a pronunciation grade.
