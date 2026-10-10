# source-to-explainer-video — runnable example

A minimal but complete pipeline that produces a **narrated explainer MP4** from a
planned scene list, then audits the encoded file and packages a re-renderable source
archive. This example dogfoods its own checklist: it explains what the pipeline checks.

```bash
python3 -m venv .venv && .venv/bin/pip install -r ../requirements.txt
bash assets/fetch-font.sh          # or: export EXPLAINER_FONT=/abs/path/font.otf
bash make_demo_audio.sh            # PLACEHOLDER room-tone audio, not speech
.venv/bin/python design.py
.venv/bin/python prepare.py
.venv/bin/python render.py --samples
.venv/bin/python render.py --determinism
.venv/bin/python render.py         # → master.mp4
.venv/bin/python qa.py             # → qa/qa.json + every derivative in qa/
.venv/bin/python fidelity.py       # → source-fidelity-review.json
.venv/bin/python package.py        # → source.zip + artifact-verification.json
```

`make_demo_audio.sh` generates room tone so the pipeline can be proven end to end with
**no paid TTS call**. Replace those WAVs with real narration (see
`../references/tts.md`) before calling the result a deliverable — `package.py` records
`real_tts_scenes` so you cannot forget.

## What each file is

| File | Role |
|---|---|
| `config.json` | header/footer text, size, fps, gap, encoder settings |
| `design.py` | the **only** editorial file: scene list, claims, narration, diagrams |
| `prepare.py` | measured audio → `scenes.json`, `narration.wav`, `captions.srt`, script, storyboard |
| `render.py` | pure-function frame renderer; `master.mp4`; `--samples`, `--determinism` |
| `qa.py` | encoded-master audit and **all** derivatives |
| `fidelity.py` | source-fidelity review, separate from the video QA |
| `package.py` | whitelist archive, provenance, extracted-archive replay |
| `gemini_tts.py` | per-scene Gemini speech with key-less reuse (used by the language examples) |
| `variant.py` | builds one language variant of a plan through the whole pipeline |
| `asr_check.py` | optional whisper.cpp transcript similarity per scene |

## Adding to the diagram vocabulary

Objects live in `design.py` and are drawn in `render.py`:

| type | meaning |
|---|---|
| `node` | a person, system or state (circle + knockout label) |
| `box` | a claim or artifact card |
| `label` | free text with a knockout behind it |
| `flow` / `line` / `arrow` | relationship, with moving dots for information |
| `gate` | a bottleneck or constraint marker |
| `checks` | checklist items that light up as their sentence is spoken; optional per-item `colors` |
| `morph` | one shape changing interpretation (fixed vertex correspondence) |
| `wbox` / `wlink` | progressive drawing of a box or connector at a narration anchor |
| `timeline` | release-style ticks; `count: [before, after]` adds or removes ticks one by one |
| `mesh` | peers on a ring: all-pairs links before, a star around one hub after |
| `chips` | a short list (queue, holders, record kinds) whose members change at the anchor |
| `curve` | a polyline with moving dots, for a feedback loop |

A `color` may be a single hex value, or `[before, after]` to cross-fade the semantic
state at the scene's transition anchor. A `pos` may be `[x, y]` or `[x1, y1, x2, y2]`
to move during the transition.

## Honest limits of this example

- Placeholder audio is room tone; nothing here speaks.
- Caption timing is a proportional estimate inside each measured scene, not forced
  alignment.
- `qa.py` does not perform ASR or a human listen, and `fidelity.py` is an author
  second pass — not an independent reviewer.
- Same-machine RGB equality is not cross-OS reproducibility.
