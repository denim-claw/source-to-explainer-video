# Book section → concept explainer

English | [한국어](README.ko.md)

One section of Eric S. Raymond's *The Cathedral and the Bazaar* (v3.0), "Release Early,
Release Often", explained in six scenes. One scene plan produces a Korean and an English
master.

![An all-pairs mesh of eight debuggers becomes a star around one coordinator](preview/en.gif)

| | English | Korean |
|---|---|---|
| Video | [en.mp4](preview/en.mp4) · 3:07 · 4.8 MB | [ko.mp4](preview/ko.mp4) · 3:04 · 4.4 MB |
| Captions | [en.srt](preview/en.srt) · 38 cues | [ko.srt](preview/ko.srt) · 39 cues |
| Still | [en.png](preview/en.png) | [ko.png](preview/ko.png) |

## Why this source

The essay is published under the Open Publication License 2.0, which permits copying,
distribution and modification, so it can serve as a public example. Videos made from
commercial books for private study stay private.

The source is [this section on catb.org](http://www.catb.org/esr/writings/cathedral-bazaar/cathedral-bazaar/ar01s04.html).
`pipeline.py` fetches it and stops unless its SHA-256 matches the value pinned in `plan.py`.

## Scenes

| Scene | Source | Claim | Visual change |
|---|---|---|---|
| 1 | first two paragraphs | the goal of showing few bugs led to long release cycles | six release ticks thin out to two |
| 2 | lesson 7 | what was new was intensity, not quick releases | ticks multiply from two to eighteen |
| 3 | after lesson 7 | frequent releases maximized person-hours, at a price | the loop runs and the box becomes the maximized quantity |
| 4 | lesson 8 | enough eyeballs make bugs shallow; finder and fixer differ | a deep bug rises to the surface |
| 5 | parallelizable paragraph | debugging avoids quadratic coordination cost | a 28-link mesh becomes an 8-link star |
| 6 | last two paragraphs | an argument from experience; version numbers split risk | one release path forks into stable and cutting edge |

The Emacs Lisp archive story, the Stallman/Gosling comparison and contributor
self-selection are condensed. What was condensed, and why, is recorded in
`build/<lang>/source-fidelity-review.json`.

## Build

Run from the repository root after fetching the font (`bash example/assets/fetch-font.sh`).

```bash
export GEMINI_API_KEY=...                       # only for scenes without cached speech
export WHISPER_MODEL=/path/to/ggml-small.bin    # optional ASR comparison
.venv/bin/python example-concept/pipeline.py              # Korean and English
.venv/bin/python example-concept/pipeline.py --lang en    # one language
```

| File | Role |
|---|---|
| `plan.py` | source record, bilingual scene plan, fidelity inventory |
| `pipeline.py` | verifies the source, then runs `example/variant.py` per language |
| `../example/variant.py` | stages shared scripts into `build/<lang>/` and runs speech → prepare → render → QA → package |
| `../example/gemini_tts.py` | per-scene Gemini speech with reuse |

Speech is cached in `audio-cache/<lang>/`. When script, model, voice and style match, it is
reused and the API key is never read. Builds and audio stay out of Git; only the verified
masters and captions are copied into `preview/`.

## What was checked

| Check | Result |
|---|---|
| Format | 1280×720, 30 fps, H.264 + mono 48 kHz AAC; 5,601 (en) and 5,524 (ko) frames counted |
| Full decode | no errors |
| Cuts | 20 frames at each cut and +0.08/+0.17/+0.4 s, extracted from the encoded master |
| Layout | 73 samples per language; no text↔text or label↔card overlap |
| Audio | peak 0.796 (en) and 0.742 (ko), no clipped samples |
| Determinism | forward/reverse renders give equal RGB hashes (same machine) |
| Package replay | the 56-file archive, extracted to a clean folder, renders a 2-second MP4 and matches RGB hashes |
| ASR comparison | whisper.cpp small, per scene; similarity to the script 0.998–1.0 (en), 0.868–0.993 (ko) |

Speech: Gemini `gemini-3.8-flash-lite-tts`, voice `Charon`.

## Not checked

- The maintainer listened to the Korean version and found nothing to fix. No one has listened to the English version.
- ASR similarity is not a pronunciation grade.
- Caption timing is proportional to character count inside each measured scene, not forced alignment.
- The fidelity review is the author's second pass, not an independent review.
- Tick counts, the eight debuggers and the depth of a bug are metaphors, not measurements.
