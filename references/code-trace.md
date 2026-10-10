# Code-trace mode

Use when the viewer wants to follow source lines and changing runtime values, rather
than hear a high-level PR summary. This is a mode of the same skill. Reuse the audio,
measured preparation, encoding, encoded-file QA and packaging in §§4–7 / `pipeline.md`.
Read `from-code-review.md` for behavioural reviews instead: its no-line-by-line and
~8-minute rules do not apply to this mode. Agree a useful source range and pacing.

## Choose the evidence and presentation

| Method | What appears | Evidence required |
|---|---|---|
| Source-line walkthrough | sliced source panel, keyword-timed line highlights, right-hand value panel | exact source revision/range; values labelled illustrative unless backed by an execution trace |
| Debugger walkthrough | the same panels with recorded arguments/locals/results from a real run | execute the original module with injected auth/DB/storage fakes and fixed clock; record the scenario and trace semantics |

Select the method from the user's request. A debugger walkthrough must execute the
original implementation: rewriting its algorithm in a demo proves only the rewrite.
The injected fakes isolate external effects; they do not establish production integration.

## Pin source and collect a trace

- Record repository, commit, path, source hash and inclusive original line range. For a
  newly authored fixture not committed yet, pin its Git blob and explicitly record that
  scope. Read that blob (`git show <commit>:<path>` or `git cat-file blob <blob>`).
- Display lines from that exact source, preserving whitespace, names, literals and original
  numbers. Split a wide/long function across panels; never silently elide or reflow code.
- Inject fakes through the module's dependency boundary. Fake authentication, DB/external
  reads and writes; record their arguments and results. Fix time and seeds where used.
  Do not start the application or load live credentials just to produce a trace.
- Record whether each event shows state before a line, after a line or at return. Python
  line events occur before execution. Avoid showing a computed value as if it already
  existed before its assignment.
- Cover one named scenario per episode; name unexecuted branches. Add error/concurrency
  scenarios only when needed by the requested explanation.
- Do not move private code, trace values, generated footage or assets into a public
  example/PR. Use an independently authored fictional fixture for reusable demonstrations.

## Prepare panels and measured cues

Each scene needs: source location, code range, visible panel interval, narration,
highlighted line(s), keyword anchor, value snapshot and trace-event reference.

Use measured per-scene WAV lengths and the shared `prepare.py` cue model. Find each
keyword in the narration; fail if absent. With proportional captions, say timing is an
estimate; use alignment only if actually run. Keep original audio provenance and license.
Temporary local speech is sufficient for a no-cost renderer proof and must be reported
as temporary. Validate matching completed audio before considering any paid API.

A highlight uses a half-open interval `[start, end)` in its own scene's time coordinates.
Require `panel_start <= highlight_start < highlight_end <= panel_end`. A cue that lands
in the preceding or following panel is a failure even if the full video timestamp is valid.
The value snapshot must match the displayed execution point. Label illustrative values
for the source-line method; debugger values cite the recorded event.

Use a right-side value panel with real-font pixel measurements. Wrap JSON strings and
long tokens at measured width; move excess values to another scene/panel if height runs
out. Do not silently clip, abbreviate an important value or shrink code until unreadable.
Titles/captions remain in shared reserved bands; copy swaps instantly at scene cuts.
`renderAt(t)` stays pure so backward seeking cannot change execution state.

## QA that is specific to this mode

Alongside `video-qa.md`, assert:

1. Every displayed source row equals the Git original line by line. Keep this fidelity
   report separate from visual QA. Screenshot/OCR is not the source-of-truth comparison.
2. Each highlight is inside its source range **and its panel's active time interval**.
   Sample just before/at/after every cue and panel boundary from the encoded master.
3. Value/code text fits its actual panel rectangles with the rendered font; check both
   width and height, panel separation, caption/title boundaries and representative phone
   frames. Geometry checks do not substitute for inspecting encoded pixels.
4. Displayed debugger values agree with trace-event locals; external arguments agree with
   the fake's call log. Do not imply that a fake write reached a real database.
5. Extracted-archive replay includes the panel renderer, exact source snapshot, trace,
   shared helpers, audio, fonts and license. It must not depend on the original checkout.

## Deliver several parts when needed

A 15 MB transport limit is a delivery constraint, not a duration rule. Configure the
actual byte limit (the example uses 15,000,000 bytes) and check the **encoded bytes**.
Split at scene boundaries so a spoken claim/code step survives intact. Re-encode each
part and re-check count, codecs, audio and full decode. Verify parts cover the timeline
once with no missing/duplicated frames. If a single scene exceeds the limit, shorten the
scene or adjust encoding, then rerun its QA; do not cut mid-explanation silently.

Provide per-part duration/bytes/SHA256 and one mobile-friendly page with inline controls,
part selection and direct links. Prefer relative URLs for a local package. Hosting/upload
requires explicit authorization. Prototype assets are not automatically public artifacts.

## Real open-source example

`example-debugger/` traces a real function from `selvage-lab/selvage` at a pinned commit:
blob-checked source, a scenario taken verbatim from the repository's test (checked by
parsing the test file), a tracer over the original module imported from fetched files,
highlights that name trace events by index, and a full-width code panel with a watch bar
for long real-world lines. `trace_check.py` and `test_trace.py` show the refusals that
matter: invented values, highlights outside their range or panel time, and edited source.

## Runnable public fixture

`example-code-trace/` contains `codedraw.py`, `panels.py`, a dependency-injected
`harness.py`, fictional `inventory.py`, the multi-part `player.html` template and a
`pipeline.py` adapter. See its README for the one-command build. It reuses the existing
example pipeline instead of carrying a second TTS/prepare/encoder/QA/package implementation.
