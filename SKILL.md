---
name: source-to-explainer-video
description: Use when a source must become a narrated explainer video.
version: 1.0.0
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
A public copy with a runnable example lives at
https://github.com/denim-claw/source-to-explainer-video (same SKILL.md plus `example/`).

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
| "설명 영상", "3Blue1Brown 스타일", no format named | narrated MP4 (§4–§7) |
| "다이어그램", "구조도" | diagram artifact (§3b) |
| "웹", "HTML", "탭" | mobile-first 3-tab page (§3c) |
| "영상 + 웹" | video first, then the page |

Report every artifact with absolute path, duration, size, SHA256, the QA reports and the
fidelity report. Never publish or upload without a separate explicit instruction.

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
- Expected duration: roughly 40–60 s of finished video per scene; a single code change
  should stay under ~8 minutes of narration.

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

- Synthesise **per scene**; keep the original WAV, model, voice, interaction id and usage.
  Never re-wrap a headered WAV, never silently substitute another TTS.
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

Details and the exact request shape: `references/tts.md`.

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

## Proven implementation references (curator profile)

- `/home/claw/pm-book-ch5-video/v2-2d/` — 2D relation diagrams + CairoSVG annotations:
  `design.py`, `render.py`, `qa.py`, `package.py`.
- `/home/claw/pm-book-ch6-video`, `pm-book-ch13-video`, `pm-book-ch7-video`,
  `pm-book-ch8-video` — chapter productions with fidelity, preflight and package replay.
- `/home/claw/source-to-explainer-video/example/` — minimal runnable example
  (proves the pipeline with placeholder audio and no paid TTS).
- Older skills kept for their chapter-specific notes: `book-concept-video`,
  `video-deliverable-qa`, `karpathy-output-understanding`.

## min의 책 영상 보관 방식 (curator 프로필)

- 장별 완성 후 R2에 MP4를 적재하고 하나의 모바일 친화 HTML 시리즈 페이지에 장별 인라인
  재생기·직접 링크를 연결한다. 새 장도 같은 시리즈에 추가한다.
- 이것은 보관 방식 승인이지 제3자 책 기반 전체 장 해설을 불특정 다수에게 공개할 권리
  확인이 아니다. 업로드 전 `content-publishing` 저작권 게이트를 적용하고, 개인 학습용이면
  페이지뿐 아니라 영상 자산 자체도 인증으로 보호한다.
- Telegram 전달은 기본 `MEDIA:/절대/경로`. 완성된 장을 다음 장보다 먼저 전달하고, 이미
  처리한 지연 완료 알림 때문에 재생성하거나 재전송하지 않는다.
