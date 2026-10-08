# source-to-explainer-video

Turn one **verified source** — a book chapter, a paper, a spec, a code change — into a
narrated explainer video with semantic diagrams, subtitles, a source-fidelity review and
an audited, re-renderable source package.

Optional outputs: a diagram artifact, or a mobile-first interactive HTML page, instead of
or alongside the video.

This is a **Hermes Agent skill** plus a **runnable example**. It merges three earlier
skills into one:

| earlier skill | what it contributed |
|---|---|
| `karpathy-output-understanding` | clear-text pass (ASD-STE-inspired), diagram, interactive page, "the human reviews outputs more than code" framing |
| `book-concept-video` | scene planning, per-scene TTS with provenance, measured timing, pure-function frame renderer, source fidelity |
| `video-deliverable-qa` | verify the **encoded file**, cut-point samples, derivative ownership, archive replay |

## Why video first

An interactive page asks for attention at a desk. A narrated explanation can be heard
while commuting, so a reviewer arrives already holding the shape of the material: which
path moved, which condition the claim depends on, what is still unverified. This skill
therefore defaults to video and treats written/HTML deliverables as opt-in.

## Layout

```
SKILL.md                        the skill itself — workflow, contracts, pitfalls
references/
  pipeline.md                   exact command order and invariants
  renderer-notes.md             layout constants, semantic animation vocabulary, cut rules
  tts.md                        per-scene synthesis, provenance, reuse rules, captions
  video-qa.md                   the encoded-file checklist
  source-fidelity.md            inventory/conditions/risk transforms
  from-code-review.md           using the same pipeline to explain a diff or PR
  asd-ste-80.md                 the ~80 % strictness clear-text pass
example/                        a complete, runnable 3-scene project
requirements.txt                pinned dependencies
```

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd example
bash assets/fetch-font.sh          # or: export EXPLAINER_FONT=/abs/path/font.otf
bash make_demo_audio.sh            # PLACEHOLDER room-tone audio, not speech
../.venv/bin/python design.py
../.venv/bin/python prepare.py
../.venv/bin/python render.py --samples
../.venv/bin/python render.py --determinism
../.venv/bin/python render.py      # → master.mp4
../.venv/bin/python qa.py
../.venv/bin/python fidelity.py
../.venv/bin/python package.py
```

The example renders a real 1280×720 / 30 fps H.264 + AAC MP4, audits the encoded file and
packages a whitelist archive with a **real** extracted-archive replay (a 2-second
narrated MP4 plus full-timeline RGB hash comparisons). See `example/README.md`.

## Requirements

- Python 3.11+
- `ffmpeg` / `ffprobe`
- Pillow, NumPy, fontTools (pin them from `requirements.txt`)
- optional: a system Cairo library + `cairosvg` for the thin SVG annotation layer
- a CJK-capable font with a redistributable licence (fetched, not committed)

## Design rules that matter most

1. **Fix the source identity before producing anything.** Exact range, exact edition,
   recorded hash. Never substitute a similar work.
2. **One claim per scene, one visual change per claim.** The change carries the logic —
   a path opening, a shape morphing between two readings, a state replaced.
3. **Declare your metaphors.** If coordinates, counts or lengths are not measured data,
   say so on screen or in the package.
4. **Verify the encoded file, never the authoring surface.** Probe, count frames, decode
   fully, sample every cut at +0.08/+0.17/+0.4 s.
5. **Keep the fidelity review separate from the video QA.** A file that plays proves
   nothing about whether the explanation is right.
6. **Name the checks you did not run** — human listening, ASR, forced alignment,
   independent review.
7. **Publishing is a separate explicit step.** Producing a video is not permission to
   distribute it.

## Licensing

- This repository (skill text and example code): MIT — see `LICENSE`.
- Fonts: fetched separately; keep their licence file with them. See
  `example/assets/README.md`.
- A source you explain (a book, a paper, someone's code) keeps its own rights. Explaining
  a source is not a licence to redistribute it, and generated output containing
  substantial verbatim text may still infringe.
- Do not commit private scans, full OCR text, credentials, or customer data.
