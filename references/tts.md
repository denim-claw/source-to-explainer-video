# TTS — measured narration with provenance

## Interface

- Synthesise **per scene**, not the whole script in one call. Per-scene gives you
  measured lengths, per-scene retry, partial reuse, and a usable provenance chain.
- Keep the **original WAV exactly as returned**. If the API returns a headered WAV,
  never strip and re-wrap it, and never guess the container.
- Store per scene: model, voice, request id, mime type, the exact script text, usage,
  measured duration, attempt number, and the WAV SHA256.
- Separate the "style" instruction from the transcript per the API's own schema; ask the
  model to speak only the transcript.

Compatibility note: the Gemini speech-generation route used here returns audio through an
`interactions`-style endpoint where transcript and `speech_metadata.style` are separate
fields. Re-check the current official schema before changing anything — do not invent
field names, and do not silently fall back to a different TTS.

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
