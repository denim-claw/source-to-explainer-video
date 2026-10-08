---
name: source-to-explainer-video
description: Use when turning a verified source (book chapter, paper, code change, PR) into a narrated explainer video with diagrams, subtitles, fidelity review and encoded-file QA; optionally emits a diagram artifact or a mobile HTML page instead of, or alongside, the video.
version: 1.0.0
author: min (curator profile) — merged from book-concept-video + video-deliverable-qa + karpathy-output-understanding
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [explainer-video, narration, animation, korean, source-verification, video-qa, asd-ste100, diagram, html]
    related_skills: [ocr-and-documents, content-publishing, web-fulltext-extraction]
---

# Source → explainer output

Turn one **verified source** into something a human can actually absorb. The default
output is a **narrated explainer video**; a diagram artifact or a mobile HTML page is
produced only when the request asks for it.

This skill merges three older ones: `karpathy-output-understanding` (clear text →
diagram → interactive page), `book-concept-video` (chapter → narrated concept video)
and `video-deliverable-qa` (verify the encoded file, never the authoring surface).

## When to use

- A book chapter, paper, spec, RFC, release note or code change must become a
  Korean-language explainer with **narration + diagrams + subtitles**.
- The user asks for "a 3Blue1Brown-style explanation video" of some material. That
  reference means *concept animation with narration*; it does not authorise copying
  another creator's assets, characters or phrase-by-phrase script.
- An existing explainer must be checked before delivery: the encoded MP4, not a
  preview or a snapshot of the authoring surface.
- The user wants the same source as a diagram or an interactive page *instead of* a
  video — then skip §4–§7 and emit only the requested artifact.

**Not** for: verbatim audiobook narration of a whole work, re-uploading a
copyrighted video, or replacing a real renderer with a slide deck of static text.

## 0. Output contract (decide first, ask nothing low-stakes)

| Request | Emit |
|---|---|
| "설명 영상", "3Blue1Brown 스타일", no format named | narrated MP4 (§4–§7) |
| "다이어그램", "구조도" | diagram artifact (§3b) |
| "웹", "HTML", "탭" | mobile-first 3-tab page (§3c) |
| "영상 + 웹" | video first, then the page |

Deliver every artifact with: absolute path, duration, size, SHA256, the QA reports,
and the fidelity report. Never publish or upload without a separate, explicit
instruction.

## 1. Fix the source before anything else

1. Verify identity: title, author, edition, and the exact start/end of the range.
   Never substitute a topical guide, a different edition, or a whole PDF for one
   chapter.
2. Record: printed page numbers, PDF page numbers, and the 1-based ordinal of the
   first page of the *next* section. Scans can duplicate pages — compare the actual
   rendered pages before asserting a range.
3. Compute the source's SHA256 and keep it in `source-verification.json`. Private
   scans, the full OCR text, and the source PDF never enter the delivered package.
4. Read the whole range. List every section, claim, condition/exception,
   self-check item, case study and tip.

For code-review sources, the "range" is the diff plus its surrounding files and the
test results — see `references/from-code-review.md`.

## 2. Plan before spending

- Write the scene table first: id, source location, source claim, the *one* visual
  change that explains it, narration, and the exception that must survive.
- One claim per scene. One action per instruction. One visual change per claim.
- Mark every invented metaphor as invented. If a diagram's counts, lengths or
  coordinates are not measured data, say so on screen or in the package.
- Design animation where the **change itself carries the logic** (an expected path
  aligning, a bottleneck clearing, one shape morphing between two interpretations, a
  claim box replaced by another). Percentage-based wobble, a generic shared curve, or
  three static labels holding up a whole scene are not explainer animation.
- Allocate the layout before writing text: title band, diagram band, a reserved
  slack strip for one semantic sentence, and the caption band. Author one annotation
  at a time — do not add decoration per cue.
- Emit clearer prose first even when the final output is video: the ASD-STE-inspired
  rewrite (§3a) is what keeps the narration short, checkable and free of invented
  facts.

## 3. Optional artifacts

### 3a. ASD-STE-inspired clear text (always produce, cheap)

Rewrite at roughly **80 % ASD-STE100 strictness**: one claim per sentence, one action
per instruction, one term per concept, active voice, no new facts, all numbers,
conditions, exceptions and scope qualifiers preserved, interpretation marked
separately. Say "ASD-STE100-inspired, 80 %" — never "ASD-STE100 compliant" or
"certified". See `references/asd-ste-80.md`.

### 3b. Diagram artifact

Author a typed JSON diagram (workflow / architecture / sequence / dataflow /
lifecycle), at most 12 primary nodes, then **validate before delivering** and only
report success on a passing validation. If the local diagram toolchain is unavailable,
emit the diagram as a self-contained SVG plus the JSON spec and say which validation
did not run. Do not silently substitute a text outline.

### 3c. Mobile-first HTML page

Exactly three tabs unless the user names them: `01 명료한 글` · `02 다이어그램` ·
`03 인터랙티브`. Tab switching without reload, `aria-selected="true"` on the active
tab, arrow-key navigation, works at mobile width, source links visible, and a clear
statement of which content is source-derived and which is interpretation. Publish
through the normal content-publishing path of the profile you are in — do not invent a
second publishing route.

## 4. Narration and measured timing

- Synthesise per scene with the specified model/voice and keep the **original WAV**,
  model name, voice, interaction id and usage. Never re-wrap a headered WAV and never
  substitute a different TTS silently.
- Validate completed audio (script text, model, voice, metadata) **before** loading
  any API key, and load the key lazily only when audio is genuinely missing. A missing
  credential must not block reuse of verified audio, re-rendering, or QA.
- Measure length from the WAV frame count / sample rate. Concatenate with a short
  scene gap; state the gap.
- Only use a mild `atempo` when needed; re-measure afterwards and rebuild every
  timestamp. Local timing changes never need a new paid call.
- Distribute caption timings **proportionally by character count inside each measured
  scene**, split at word boundaries into at most two-line chunks. Report this as an
  estimate — it is not forced word alignment, and no full human listen has happened.
- Anchor scene transitions and highlight cues to a keyword that exists in the
  narration; assert the keyword matches, or fail loudly.

Details and exact API shape: `references/tts.md`.

## 5. Render honestly

- `renderAt(t)` must be a **pure function of time**: no wall clock, no remote assets,
  no accumulated state — so reverse-order seeking produces identical pixels.
- 1280×720, 30 fps, H.264 `yuv420p`, AAC mono 48 kHz unless the user asked otherwise.
  State the values you actually produced.
- Copy swaps **instantly at the cut**; signal the cut with a non-text element. Never
  cross-fade two different strings, and never fade copy in from zero opacity.
- Keep one canonical renderer path. Frame-by-frame Pillow + FFmpeg is a real renderer
  and is preferred over substituting a different engine mid-series.
- Layout constants, morph/progressive-drawing rules and the slack-strip contract:
  `references/renderer-notes.md`.

## 6. Verify the encoded file (never the authoring surface)

Required before any "done":

1. `ffprobe -count_frames` on the **shipped** file: codec, dimensions, fps, duration,
   counted frames, audio channels/sample rate. Check `fps × seconds == frames`.
2. Full decode with empty stderr.
3. Extract the frames you judge **from the master**, never from a preview.
4. Cut-point samples at the cut, +0.08 s, +0.17 s, +0.4 s for every scene — this is
   where blanked or double-printed copy hides.
5. Semantic before/after samples at the real transition anchors, clamped to the scene;
   intermediate morph/draw phases too, not only the end state.
6. Text-vs-text **and** label-vs-card-rectangle collision checks; sample intermediate
   phases.
7. Audio peak / RMS / clipped-sample count.
8. Same-machine forward/reverse seek determinism, with the scope stated.
9. ONE script regenerates every derivative from the master — contact sheets, cut
   sheets, phone-size frames. A hand-run ffmpeg step leaves stale bytes behind.

Full checklist: `references/video-qa.md`.

## 7. Package and report

- Whitelist archive: script/design, scenes JSON, narration + source audio, subtitles,
  fonts **and their licence**, pinned requirements, QA reports, README, fidelity
  report. Exclude private scans, full source text, secrets, virtualenvs, temp renders.
- Test the archive (CRC), count entries, and assert the exclusions programmatically.
- Verify the archive is genuinely runnable: extract it to a clean directory, render a
  **real short narrated MP4** using only bundled code, fonts and audio, probe it, count
  its frames, decode it fully, and compare representative full-timeline RGB hashes
  against the original renderer. Report that scope exactly — it is not a second
  full-length encode.
- Keep the archive's own size/hash in a verification JSON **outside** the archive
  (a document that embeds the hash of the archive containing it is self-referential).
  Build the archive last, then re-confirm the master's on-disk hash.
- Report: absolute paths, duration, sizes, SHA256, which QA ran, which did **not** run,
  and the remaining limits. Never present a dismissed check as a pass.

## Pitfalls

- **Treating a good-looking render as a correct explanation.** Encoded-file QA proves
  the file plays; it does not prove the source was understood. Keep the fidelity
  report separate and never cite one as evidence for the other.
- **Claiming a technique the file does not contain.** If a check did not run (ASR,
  full listen, forced alignment, motion assertions), name it as not run.
- **Reusing another chapter's QA output, voices or scene counts.** Validate audio
  provenance per scene and fail on mismatch.
- **Proportional caption timing described as accurate sync.**
- **Publishing under cover of a production request.** A video request is not a
  publishing approval.
- **Delivering via a bespoke upload helper.** Hand over the verified file through the
  interface's native attachment and let the on-disk reports be the evidence.
- **A stale derivative beside a new master.** Re-render, re-derive, re-report and
  re-archive together after any copy or geometry fix, then re-inspect the frames whose
  bytes changed.
- **Same-machine RGB equality read as cross-platform reproducibility.** Record the
  native library versions and treat other OSes as unverified.
- **Reduced-size phone frames treated as compliance approval.** They are legibility
  checks.

## Verification

- `source-verification.json` — source hash, printed/PDF ranges.
- `source-fidelity-review.json` — every unit and condition, plus what was condensed.
- `qa/qa.json` — encoded-master checks above.
- `qa/visual-review.json` — what a human actually looked at, and what they did not.
- `qa/package-rerender.json` — archive extracted, real short narrated render, hashes.
- `artifact-verification.json` — master + archive paths, sizes, SHA256, entry count.
