# Pipeline — exact commands

```
design.py        source plan → scenes-draft.json (the only editorial file)
tts / audio      audio/scene-NN.wav + audio/scene-NN-metadata.json (+ raw-audio/ copy)
prepare.py       measured lengths → scenes.json, narration.wav, captions.srt, script.md, storyboard.md
render.py        scenes.json + narration → master MP4  (+ --samples, --determinism)
qa.py            encoded master audit → qa/qa.json + every derivative in qa/
subset-font.py   smaller package font, proven frame-identical
fidelity.py      source-fidelity-review.json / source-map.json
package.py       whitelist archive + provenance + extracted-archive replay
```

## Order of operations

```bash
# 1. Editorial plan (no paid calls yet)
python design.py

# 2. Prove the renderer before spending a generation budget: render a short
#    proof with placeholder timings, then a narrated preflight of the first
#    two scenes plus any scene that uses a NEW technique.
python prepare.py --proof && python render.py --samples && python preflight.py

# 3. Audio (paid). Reruns reuse verified audio; only missing scenes are synthesised.
python tts.py

# 4. Measured timing, then geometry before pixels
python prepare.py
ffmpeg -v error -y -i narration.wav -c:a flac narration.flac
python render.py --samples            # authoring bbox audit
python preflight-geometry.py          # text↔text and label↔card collisions
python render.py --determinism        # pure-function check
python preflight.py                   # short narrated MP4

# 5. Full render, then the encoded-file audit
python render.py
python qa.py
python subset-font.py

# 6. Source fidelity and packaging
python fidelity.py
python package.py
```

## Invariants

- `scenes-draft.json` is the single editorial source. Everything else is derived; never
  hand-edit `scenes.json`.
- The estimated captions, transition anchors and cue times all come from measured WAV
  lengths. Change audio → rerun `prepare.py` → everything re-derives.
- `--proof` must be unusable as a deliverable: `qa.py` asserts
  `provisional_proof == False`, so a proof render can never be reported as final.
- `subset-font.py` must prove the package font renders **identical** frames at many
  timestamps before the archive is allowed to ship it in place of the source font.
- `package.py` builds the archive **last** and writes the archive hash to
  `artifact-verification.json` outside the archive.

## Environment

- Python 3.11+, `ffmpeg`/`ffprobe`, and a **system** Cairo shared library
  (`libcairo2` on Linux) if you use the SVG annotation layer.
- Pin versions in `requirements.txt`; record the native Cairo version in
  `toolchain.json`. Same-machine RGB equality is not cross-OS reproducibility.
- Video encoding goes through the `ffmpeg` CLI as a subprocess with raw RGB frames on
  `stdin` — no in-process encoder.

## Cost hygiene

- Everything except step 3 is free and local. Re-running steps 4–6 never calls TTS.
- Completed audio is validated against the script text, model, voice and metadata
  before any API key is read; a missing key must not block reuse or re-render.
- Store per-scene usage from the API response and keep paid estimates separate from
  invoices.
