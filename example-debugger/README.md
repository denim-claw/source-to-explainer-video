# Open-source function → debugger trace

English | [한국어](README.ko.md)

A six-scene debugger walkthrough of `HunkLineCalculator.calculate_actual_change_lines` from
[selvage](https://github.com/selvage-lab/selvage). Nothing is re-implemented: the original
file from a pinned commit is executed, and only the values recorded at each line appear on
screen.

![While a deleted line is processed, current_line stays put and the first and last change fill with 3](preview/en.gif)

| | English | Korean |
|---|---|---|
| Video | [en.mp4](preview/en.mp4) · 2:45 · 4.2 MB | [ko.mp4](preview/ko.mp4) · 2:51 · 4.2 MB |
| Captions | [en.srt](preview/en.srt) · 38 cues | [ko.srt](preview/ko.srt) · 40 cues |
| Still | [en.png](preview/en.png) | [ko.png](preview/ko.png) |

selvage is an Apache-2.0 public repository. This is an unofficial explanation.

## Why this function

With smart context, selvage sends the model only the code blocks that contain changed
lines. The starting point is the range a hunk actually changed, and this function computes
it. It is pure, so the original runs without fakes. Its key idea is that a deleted line
does not advance the line counter, because it no longer exists in the modified file. That
idea is easiest to see as values change on screen.

## Pinned source and scenario

- Repository `selvage-lab/selvage`, commit `e82f34a`
- Displayed file: `selvage/src/diff_parser/utils/hunk_line_calculator.py` (blob `8f5adab`)
- Imported with it: `selvage/src/context_extractor/line_range.py` (blob `7c61031`)
- Scenario: `test_modification_with_context` in `tests/test_hunk_line_calculator.py` (blob `5446cba`)

`pipeline.py` fetches these files at that commit and recomputes their blob hashes. It parses
the test file and checks that the harness input and expectation equal the test's literals
exactly. It then imports the module from the fetched files alone, without installing
selvage, and records the run with `sys.settrace`.

## Scenes

| Scene | Code | What it shows |
|---|---|---|
| 1 | lines 44–50 | the input splits into seven lines; a tracker starts with `current_line=1` |
| 2 | lines 52–59 | two context lines move `current_line` from 1 to 3 |
| 3 | lines 64–71 | the first character of `'-old line'` fails ADDED and matches DELETED |
| 4 | lines 84–90 | a deleted line: first and last change become 3; `current_line` stays |
| 5 | lines 74–79 | two added lines: the last change moves to 4, `current_line` to 5 |
| 6 | lines 102–108 | `LineRange(start_line=3, end_line=4)` is returned |

The WATCH bar shows values **before** the highlighted line executes, or just after a
function returns when labelled so. The HUNK row marks the diff line the loop is holding.

## Build

```bash
bash example/assets/fetch-font.sh             # text font
bash example/assets/fetch-font.sh mono        # monospace font for code
export GEMINI_API_KEY=...                     # only for scenes without cached speech
export WHISPER_MODEL=/path/to/ggml-small.bin  # optional ASR comparison
.venv/bin/python example-debugger/pipeline.py
.venv/bin/python example-debugger/test_trace.py
```

| File | Role |
|---|---|
| `plan.py` | pinned commit and blobs, bilingual scenes, the trace event behind each highlight |
| `harness.py` | runs the original function on the test input and records line events and locals |
| `pipeline.py` | verify source → match the test → record the trace → shared pipeline per language |
| `tracedraw.py` | full-width code panel, WATCH bar and HUNK row |
| `render.py` | adapter that draws the debugger view over the shared renderer |
| `trace_check.py` | checks the displayed code and values against the pinned source and the trace |
| `test_trace.py` | regression tests: invented values, out-of-range highlights and edited source are refused |

## What was checked

| Check | Result |
|---|---|
| Source | displayed rows equal the pinned blob |
| Values | all 26 highlights equal their recorded events; no value typed by hand |
| Timing | every highlight sits inside its own scene and code range |
| Layout | every 5th frame and each cue boundary ±1 frame; no text leaves its panel |
| Format | 1280×720, 30 fps, H.264 + AAC; 4,950 (en) and 5,143 (ko) frames counted; clean full decode |
| Package replay | the 63-file archive renders a 2-second MP4 from a clean folder and matches RGB hashes |
| Repository tests | `tests/test_hunk_line_calculator.py`: 7 passed at the same commit |
| ASR comparison | whisper.cpp small, per scene; similarity 0.970–1.0 (en), 0.754–0.891 (ko) |

The Korean scores are lower because the ASR model writes identifiers such as `current_line` and
`DELETED` in Hangul. No sentence was missing, and the maintainer heard
the names correctly when listening to the Korean version.

Speech: Gemini `gemini-3.8-flash-lite-tts`, voice `Puck`.

## Not checked

- Only one test scenario was executed. Unmatched prefixes (`\ No newline at end of file`),
  hunks without changes and deleted files starting at line 0 were read, not run.
- The maintainer listened to the Korean version and found nothing to fix. No one has listened to the English version.
- Caption timing is an estimate.
- No independent review by the selvage maintainers or anyone else.
