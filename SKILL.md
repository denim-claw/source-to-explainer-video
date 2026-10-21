---
name: source-to-explainer-video
description: Use when a source or code execution must become a narrated explainer video, including line-level or debugger-style walkthroughs.
version: 1.5.3
author: min (curator) — merged from book-concept-video + video-deliverable-qa + karpathy-output-understanding
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [explainer-video, narration, animation, korean, source-verification, video-qa, asd-ste100, diagram, html]
    category: media
    related_skills: [ocr-and-documents, content-publishing, web-fulltext-extraction]
---

# Source → explainer output

Turn one **verified source** — a book chapter, a paper, a spec, a release note, a **code
change or PR** — into something a human can absorb. The default output is a **narrated
explainer video**; a diagram artifact or a mobile HTML page is produced only when the
request asks for it.

Merges three earlier skills: `karpathy-output-understanding` (clear text → diagram →
interactive page), `book-concept-video` (chapter → narrated concept video) and
`video-deliverable-qa` (verify the encoded file, never the authoring surface).
A public copy with runnable examples lives at
https://github.com/denim-claw/source-to-explainer-video (same SKILL.md plus `example/`,
`example-concept/`, `example-architecture/`, `example-debugger/` and `example-code-trace/`).

## When to use

- A book chapter, paper, spec, release note or **code change / PR** must become a Korean
  explainer with narration + diagrams + subtitles.
- The user asks for a "3Blue1Brown-style" explanation video of some material. That means
  *concept animation with narration*; it does not authorise copying another creator's
  assets, characters or phrasing.
- An explainer must be checked before delivery — verify the **encoded MP4**, never a
  preview or a snapshot of the authoring surface.
- The user wants the same source as a diagram or interactive page *instead of* a video:
  emit only that artifact.

**Not** for verbatim narration of a whole work, re-uploading a copyrighted video, or
replacing a real renderer with a slide deck of static text.

## 0. Output contract (decide first, ask nothing low-stakes)

| Request | Emit |
|---|---|
| "코드 레벨로", "디버거처럼", "실행 순서/값을 따라가기" | narrated code-trace MP4; read `references/code-trace.md`, then reuse §4–§7 |
| "아키텍처 리뷰", "구조 설명", "이 PR/저장소 리뷰" | narrated behavioural review MP4; read `references/from-code-review.md` |
| "영어/한국어 둘 다", "자막 두 벌" | one master per language from the same plan (§4, `example/variant.py`) |
| "설명 영상", "3Blue1Brown 스타일", no format named | narrated MP4 (§4–§7) |
| "다이어그램", "구조도" | diagram artifact (§3b) |
| "웹", "HTML", "탭" | mobile-first 3-tab page (§3c) |
| "영상 + 웹" | video first, then the page |

Report every artifact with absolute path, duration, size, SHA256, the QA reports and the
fidelity report. Never publish or upload without a separate explicit instruction.

### Optional 3D / hybrid mode

Keep `concept-2d` the default. Select `concept-3d` for spatial relations and
`narrative-3d` for concrete events/actions; hybrid explanations may use both.
**Only when a 3D mode is selected**, load
`references/3d-hybrid-production-review.md` (including the actual MP4 references under
`assets/prince-references/`, with manifest timecodes), `references/narrative-3d.md` and
`references/3d-mode-quality.md`. Route concrete events to readable actor/action/
consequence and abstract relations to concise direct-label motion diagrams. Do not
force abstract emotions into mannequin acting or make viewers decode numbered badges.
Preserve the approved renderer; native Blender requests include abstract graphics in
that same native pipeline, with screen-space caption compositing allowed.

The 3D-only workflow requires a narrated moving pilot, a falsifiable per-utterance
visual ledger, native preflight before full production, and separate review of the
actual encoded master (including settled connectors and phone-size qualifiers).
Reconcile independent findings rather than inheriting an all-PASS author summary.
Sampled semantics, continuous motion, listening, source fidelity, technical QA and
user aesthetic approval remain separate verdicts. Preserve approved speech and old
masters during local repairs. Validate that every item in an equal-status list belongs
to one common visible group before its shared branch applies; disconnected label
nodes can silently exclude part of the claim. Preserve claim-bearing modifiers and
relational roles. Check settled endpoints instead of mistaking intended dashed or
progressively revealed links for defects; never change necessity into permission to
satisfy a gap review. Critical qualifications must read at phone size, and a disclaimer
does not substantiate an unsupported spoken superlative.

For local repairs, keep per-unit old/new renderer provenance, rerender only affected
complete shots, compare encoded samples across ALL units (lossy re-encoding may affect
untouched neighbors), and reinspect every changed sample. Preserve source speech and
verify encoded-audio identity when stream-copying it. These additions do not change
the default 2D renderer, existing TTS defaults or non-3D workflows.

Reusable original native assets are maintained in
https://github.com/denim-claw/prince-core-blender-assets; consult its manifest,
licensing notices and tested scope before importing. Do not copy private chapter
speech, source text or uncleared third-party models into either public repository.

Read `references/hybrid-3d.md`, `assets/hybrid-3d/README.md` and
`THIRD_PARTY_NOTICES.md` before importing assets. The kit includes actual local PNGs,
not only absolute paths to someone's asset store.

- Use original MIT people/sets/house/animals and the CC0 fire/smoke atlases when useful.
  A licensed rendered output does not license redistribution of editable stock files.
- Lock the camera per **shot**, reframe only at hard cuts. Fit the full-shot motion
  union of chosen focal objects once, never auto-follow or refit every frame.
- Distinct silhouettes and readable cause/consequence matter; an animal marker is
  not an animal model and figures idling near a box are not an explanation.
- Declare invented actions/destruction as illustrative reconstruction, not facts.
- Measured speech timing, bottom screen-space subtitles and source review still apply.
  Reuse speech for visual-only revisions; keep the configured TTS provider unchanged.
- Frame/seek/bounds tests are separate from visual acceptance and source fidelity.
  Run a short real encoded preflight; inspect the actual MP4 before full production.

`example-3d/` is a **silent asset smoke test**, not a narrated chapter or source review.

### Choose the explanation style for a video

| Viewer wants | Read | Approach |
|---|---|---|
| Understand a book, paper or spec | shared workflow below | narrated concept animation |
| Understand what a code change does | `references/from-code-review.md` | behavioural delta; no line-by-line diff narration |
| Understand how a codebase is built | `references/from-code-review.md` §6 | architecture review pinned to one commit; behaviour, not line-by-line |
| Follow code execution and changing values | `references/code-trace.md` | source-line highlights or a recorded debugger harness |

These are styles inside this skill, not nested skills. Diagram/HTML remain output formats.
Code-trace overrides the behavioural-review pacing rule; audio, measured preparation,
rendering, encoded-file QA and packaging stay shared.

## 1. Fix the source before anything else

1. Verify identity: title, author, edition, exact start/end of the range. Never substitute
   a topical guide, another edition, or a whole PDF for one chapter.
2. Record printed pages, PDF pages, and the first page of the **next** section. Scans can
   duplicate pages — compare the actually rendered pages before asserting a range.
3. Keep the source SHA256 in `source-verification.json`. Private scans, full OCR text and
   the source PDF never enter the delivered package.
4. Read the whole range; list every section, claim, condition/exception, self-check item,
   case study and tip.

For code sources the "range" is the diff plus surrounding files plus test evidence.

## 2. Plan before spending

- Write the scene table first: id, source location, source claim, the *one* visual change
  that explains it, narration, and the exception that must survive.
- One claim per scene. One action per instruction. One visual change per claim.
- Mark invented metaphors as invented. If counts/lengths/coordinates are not measured
  data, say so on screen or in the package.
- Design animation where the **change carries the logic**: a path opening, a bottleneck
  clearing, one shape morphing between two interpretations, a claim replaced. Percentage
  wobble, one shared curve for every scene, or three static labels are not explainer
  animation.
- Reserve the layout first: title band, diagram band, slack strip for ONE semantic
  sentence, caption band. Add one annotation at a time.
- Produce the clear-text pass even when the output is video: it keeps narration short,
  ordered and free of invented facts.
- Expected duration: roughly 40–60 s of finished video per scene; a behavioural code review
  should stay under ~8 minutes of narration. Code-trace episodes instead use the agreed
  code range and split at scene boundaries when a delivery size limit requires it.

## 3. Optional artifacts

### 3a. ASD-STE-inspired clear text (always produce — cheap)

Rewrite at ~**80 % ASD-STE100 strictness**: one claim per sentence, one action per
instruction, one term per concept, active voice, no new facts, all numbers/conditions/
exceptions preserved, interpretation marked separately. Say "ASD-STE100-inspired, 80 %" —
never "compliant" or "certified".

Worked contrast, in Korean:

> 나쁨 — "성능 개선이 기대되며 대체로 안정적으로 동작할 것으로 보입니다."
> 좋음 — "p95 지연이 1.8초에서 0.4초로 줄었습니다. 표본은 2,000건이며, 야간 시간대는 측정하지 않았습니다."

Clear wording and factual correctness are **different checks**.

For Korean narration, captions and documents, also apply `references/writing-ko.md`
(short sentences, matched subject and predicate, no translationese, read it aloud).

### 3b. Diagram artifact

Typed JSON diagram (workflow/architecture/sequence/dataflow/lifecycle), ≤12 primary
nodes, **validate before delivering** and only report success on a passing validation. If
no diagram toolchain is available, emit a self-contained SVG plus the JSON spec and name
the validation that did not run. Never silently substitute a text outline.

### 3c. Mobile-first HTML page

Exactly three tabs unless the user names them: `01 명료한 글` · `02 다이어그램` ·
`03 인터랙티브`. Tab switching without reload, `aria-selected="true"` on the active tab,
arrow-key navigation, works at mobile width, source links visible, and a clear statement
of what is source-derived vs interpretation. Publish through the profile's normal
content-publishing path — never invent a second publishing route.

Users read published pages mostly on a phone: check the mobile layout yourself before
reporting it as done, and do not put conversational meta-copy ("이거 저장") on a public
page.

## 4. Narration and measured timing

- **Default to Edge TTS**: no API key or separate API charge, but the voice may sound less
  natural; it is an online service, not an availability or unlimited-use guarantee. Before
  synthesis, offer Edge vs. more natural Gemini (API key required) when asking is appropriate.
  If there is no answer, proceed with Edge. Explicit natural-voice preference selects Gemini;
  confirm its key is configured without asking the user to paste a key in chat. Never silently switch.
- Synthesise **per scene**. Gemini: keep the original WAV, model, voice, interaction id
  and usage. Edge: preserve original MP3 and decode a pipeline WAV; unavailable id/usage
  stay null. Use `example/edge_tts_adapter.py`; commands in `references/tts.md`.
  Never re-wrap a headered WAV.
- Validate completed audio (script text, model, voice, metadata) **before** loading any
  API key; load the key lazily only when audio is genuinely missing. A missing credential
  must not block reuse, re-render or QA.
- Measure length from WAV frames / sample rate. Concatenate with a stated gap.
- `atempo` only for a mild adjustment; re-measure and rebuild every timestamp. Timing
  fixes never need a new paid call.
- Caption timing: **proportional by character count inside each measured scene**, split at
  word boundaries into ≤2-line chunks. Report it as an estimate — not forced alignment,
  and no full human listen has happened.
- Anchor transitions and highlight cues to a keyword present in the narration; assert the
  keyword matches or fail loudly.

- Several languages: keep one plan whose spoken and displayed strings carry every
  language, then build one master, caption file and QA set per language. Never mix
  measured timings across languages.

Details and the exact request shape: `references/tts.md`. A working Gemini client with
key-less reuse is `example/gemini_tts.py`; `example/variant.py` drives one language
variant through the whole pipeline.

## 5. Render honestly

- `renderAt(t)` is a **pure function of time** — no wall clock, no remote assets, no
  accumulated state, so reverse seeking yields identical pixels.
- 1280×720, 30 fps, H.264 `yuv420p`, AAC mono 48 kHz unless asked otherwise; state what
  you actually produced.
- Copy swaps **instantly at the cut**; signal the cut with a non-text element. Never
  cross-fade two strings, never fade copy in from zero opacity.
- Keep one canonical renderer path. Frame-by-frame Pillow + FFmpeg is a real renderer and
  is preferred over swapping engines mid-series.
- Check label-vs-card geometry, not only text-vs-text: a card or checklist cell painted
  later clips a label while no two texts overlap.

Layout constants and the semantic animation vocabulary: `references/renderer-notes.md`.

## 6. Verify the encoded file (never the authoring surface)

1. `ffprobe -count_frames` on the **shipped** file; check `fps × seconds == frames`.
2. Full decode with empty stderr.
3. Extract judged frames **from the master**, never from a preview.
4. Cut-point samples at the cut, +0.08 s, +0.17 s, +0.4 s for every scene.
5. Semantic before/after samples at the real transition anchors, plus intermediate morph
   and progressive-drawing phases.
6. Text↔text, label↔card-rectangle, and **card↔card** collision checks.
7. Audio peak / RMS / clipped samples.
8. Same-machine forward/reverse seek determinism, with the scope stated.
9. ONE script regenerates every derivative from the master.

Full checklist: `references/video-qa.md`.

## 7. Package and report

- Whitelist archive: scripts, scenes JSON, narration + source audio, subtitles, fonts
  **and their licence**, pinned requirements, QA reports, README, fidelity report.
  Exclude private scans, full source text, secrets, venvs, temp renders.
- Test the archive (CRC), count entries, assert the exclusions in code.
- Prove runnability: extract to a clean directory and render a **real short narrated
  MP4** using only bundled code/fonts/audio; probe, count frames, decode fully, and compare
  representative full-timeline RGB hashes with the original renderer. State the scope —
  it is not a second full-length encode.
- Keep the archive's size/hash in a verification JSON **outside** the archive. Build it
  last, then re-confirm the master's on-disk hash.
- Report absolute paths, duration, sizes, SHA256, which QA ran, which did **not**, and the
  remaining limits.

## Pitfalls

- **A good-looking render treated as a correct explanation.** Encoded-file QA proves the
  file plays; it does not prove the source was understood. Keep the fidelity report
  separate and never cite one as evidence for the other.
- **Claiming a technique the file does not contain** — ASR, full listen, forced alignment.
  Name unrun checks as unrun.
- **Reusing another chapter's QA output, voices or scene counts.** Validate provenance per
  scene and fail on mismatch.
- **Proportional caption timing described as accurate sync.**
- **Publishing under cover of a production request.** A video request is not a publishing
  approval.
- **A stale derivative beside a new master.** Re-render, re-derive, re-report and
  re-archive together after any copy or geometry fix.
- **Same-machine RGB equality read as cross-platform reproducibility.**
- **Reduced-size phone frames treated as compliance approval.**
- **Exposing source material you were given.** A user-supplied scan or a colleague's
  unreleased diff is authorised for analysis, not redistribution.
- **Overwriting a namesake variable in a long audit script** (e.g. reusing `a` for the
  audio stream and then for a card rect). Runtimes fail late with a `KeyError`; rename loop
  variables.

## Verification

- `source-verification.json` — source hash, printed/PDF ranges.
- `source-fidelity-review.json` — every unit and condition, plus what was condensed.
- `qa/qa.json` — the encoded-master checks above.
- `qa/visual-review.json` — what a human actually looked at, and what they did not.
- `qa/package-rerender.json` — archive extracted, real short narrated render, hashes.
- `artifact-verification.json` — master + archive paths, sizes, SHA256, entry count.

## Runnable implementation references

- `example/` — minimal pipeline proof with explicitly labelled placeholder audio.
- `example-concept/` — one OPL-licensed book section as concept animation, ko/en.
- `example-architecture/` — public QM architecture review pinned by commit/blob hashes.
- `example-debugger/` — actual recorded execution of a public selvage function.
- `example-code-trace/` — minimal trace example.
- `example-3d/` — original silent 3D asset demo, pinned dependencies and deterministic
  browser proof. It does not establish narration sync, complete source coverage,
  historical fidelity or aesthetic approval.

Keep private deployments, signed setup links, recordings, full source text, local
absolute paths and per-user publishing credentials outside a public skill package.
Publishing a private study page requires explicit approval and protection of the media
itself, not just its index page. Follow the deployment's separate rights/auth gate.
