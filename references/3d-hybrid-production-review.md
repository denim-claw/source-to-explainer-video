# 3D-only hybrid explanation: production and review

## Scope and boundaries

Apply only after selecting `narrative-3d` or `concept-3d`. Preserve `concept-2d`, its
renderer and shared defaults. A mixed visual grammar inside an approved 3D production
is not permission to replace the film with a separate 2D pipeline. When native Blender
is requested, keep both concrete scenes and abstract graphics in that declared native
route; screen-space captions/compositing remain allowed.

Treat production approval, source/voice changes, visual acceptance, asset redistribution
and publication as separate permissions. Keep previous masters, inputs and reports.
Do not change approved narration or regenerate TTS for a layout/visual repair. Verify
cached script/model/voice/audio provenance before reuse; credentials are unnecessary
when all needed audio is valid. Never push assets or publish the video from a skill-save
request. Update only the active profile's skill files.

## 1. Route meaning before building geometry

- Use **concrete narrative action** for a town collapsing, someone intervening, property
  being taken, an army holding formation or a person visibly departing. Show actor →
  trigger/contact → consequence. A labelled box cannot replace the requested event.
- Use **abstract motion diagrams** for love, fear, obligation, control, conditions or
  trade-offs when physical acting makes them harder to understand. Put direct Korean
  concept names beside/above the relevant graphic. Animate the relationship: connect,
  sever, exclude, compare, require or choose. Human performance is not mandatory here.
- Use a **mixed shot or hard cut** when an event illustrates a separate abstract claim.
  Keep source-derived history, the author's judgment and an invented explanatory
  reconstruction distinguishable. Do not invent punishment, permission or causation.
- Remove viewer-facing numbered badges and lookup legends. Keep internal object/unit
  IDs for QA only. Direct concept/role labels are allowed, not an excuse for paragraph
  cards or subtitles that rescue an otherwise meaningless image.
- Prefer a simple legible relation to elaborate mannequin pantomime. Repeated trouble
  with agency/grip is a reason to reblock, cut closer or reroute the abstraction, not to
  add more decorative movement or anonymous markers.

## 2. Freeze inputs and write a falsifiable unit contract

Inventory the source units, exact approved utterance IDs/text, WAV hashes and measured
timeline. Derive required coverage from this manifest; never hardcode another chapter's
unit count. Create a new build directory and hash source/scene/renderer/style inputs.

For **every spoken unit**, record these fields in one canonical ledger:

- `unit_id`, `source_unit_id`, `source_location`, `narration_exact`, `start`, `end`;
- `visual_route`: concrete / abstract / mixed, plus renderer and style signature;
- internal actor/object identity map; direct on-screen labels and attribution;
- initial state, semantic anchor(s), visible action/relation, settled end state;
- intended reading and the strongest likely wrong reading;
- falsifiable pass criterion and source condition/exception that must survive;
- shot IDs, held camera/framing and focal-object set, required props/contacts;
- native frame IDs, encoded frame/time evidence and master hash;
- source, native semantics, encoded semantics, continuous motion, phone legibility,
  audio/listening and technical verdicts separately;
- issue → observed reading → correction → reinspection evidence → disposition.

Use PASS / PARTIAL / FAIL / NOT_RUN with reasons. Missing coverage is not a pass.
Keep extracted files, actually viewed tiles and reviewed unique unit IDs distinct.
A manifest proves existence, not review; bounds prove framing, not meaning.

## 3. Validate the grammar in a short narrated moving pilot

Render a bounded actual MP4 with the hardest representative concrete action and one
abstract relationship, using existing approved speech where possible. Check it at full
and phone size. The viewer should recognize who acts and what changes, or directly read
the abstract relationship without decoding a legend. A beautiful still does not prove
action; a sparse still sequence encoded at 30 fps is not continuous animation.

If repeated probes produce the same ambiguity, stop the probe loop and change the
staging/visual route. More frames, precise hand-target coordinates or another agent's
optimistic summary do not fix unreadable agency. Prototype the revised critical moving
shot first. Keep one camera pose/lens per shot; closer views are hard cuts, not drifting
zooms or per-frame camera fitting.

After approval of a pilot for an already-authorized chapter, actually start the next
bounded implementation step. Do not stop at agreement or repeatedly ask for the same
permission. A new renderer, changed script/voice or external publication remains a
separate decision. Record whether code is being edited, a job is dispatched or a real
render process is running; these are not equivalent.

## 4. Native preflight before full production

Implement and inspect every unit's relevant native before/transition/after states.
Use the real semantic anchors, not fixed scene percentages that can both fall before
a late event. Test meaningful action as a moving clip when stills cannot prove it.

For concrete actions, check readable actor identity, direction, contact, reaction and
consequence. Numeric grasp distance does not prove a visible grip; walking away does
not by itself prove mutiny. Reject out-of-reach targets instead of hiding them by
clamping the arm. For abstract claims, verify directed links, both sides of contrasts,
negations, conjunctions, conditions and author attribution. Do not imply that a necessary
condition is sufficient permission or that a circumstance caused an outcome.

Validate the **semantic graph**, not only line cap coordinates. When narration lists
several equal-status qualities and then branches into alternatives, identify the whole
list as one semantic group and verify that every member reaches the shared branch.
Prefer a single multiline group label or an explicit bracket/common container; two
nearby labelled nodes without a group connection are not one list, and a new directed
edge between equal items can falsely introduce hierarchy. Inspect this grouping after
all reveals and immediately before the cut, at full and phone size.

Check labels against the exact utterance for claim-bearing modifiers such as most,
least, always, only, both and not. A correct subtitle does not excuse a diagram that
silently weakens a superlative, changes few to none, or drops a condition. Distinguish
an incomplete visual paraphrase from an unsupported spoken claim before fixing it.

For an entrusted pupil, teacher, deceiver or other relational role, name the relation
or stage its recognizable consequence; two named figures approaching or gesturing
only establish proximity, not teaching, care or deceit. Use a concise direct role
label when literal reenactment would invent an event or make the shot harder to read.

Major contradictions, missing central meaning and ambiguous causal agency block the
full render. Review native evidence here; do not require a nonexistent full master to
pass preflight. Conversely, a preflight pass cannot be reused as encoded acceptance.

## 4b. Bound review cost and keep completion reachable

- Declare the required source-backed claim, affected unit IDs and minimum before/change/settled evidence before delegating a repair. Default to one correction plus one targeted reinspection. Treat optional realism separately; an illustrative spill does not require a scientifically validated fluid/tree-contact mechanism unless that is the actual brief.
- Separate diagnostic extractions from required acceptance samples in the manifest. Do not make every newly extracted frame a fresh mandatory review task. Freeze the required sample set before inspection; never relax it retrospectively just to turn an existing failure green.
- Reuse inspected evidence only by exact image hash, extraction settings and unit/phase mapping. Do not inherit native review for a newly encoded frame. Merge unchanged evidence once and direct further work only to changed claims.
- When the user explicitly stops further review and requests the current version, preserve existing failures and approvals, record the authorized scope change separately, and deliver a clearly scoped review copy after technical checks. Mark omitted checks NOT_RUN; never forge native/pilot/listening approval or bypass security/permission controls. A stopped visual-review loop is not permission to ignore damaged media or missing speech.
- Keep a durable work record outside renderer fingerprint inputs: current build/master, process handle, latest user decision, completed audio hashes, required next command and remaining checks. Re-read live state after reset; do not restart paid synthesis or completed shots from an old summary.
- Attribute cost by production stage. Show noncached input/output and cache-read totals separately; distinguish dedicated child tasks from a mixed parent session and external speech/image calls. Never present a partial total as the full project cost or convert API prices into subscription-quota percentages.

### Reusable connected-flow asset

The companion [native asset repository](https://github.com/denim-claw/prince-core-blender-assets)
provides `blender/flow_diversion.py::FlowDiversion`: a connected inlet/turn/outlet and
a separate landward overflow crossing, with distinct screen-label anchors and pure
phase updates. See its README and `tests/flow_diversion_proof.py`. It is a fixed-layout
kinematic metaphor, not fluid simulation or validated tree-contact physics. A clean
three-file copy rendered three native Workbench AA16 stills and passed topology,
reverse-seek and visibility checks; this is not continuous-motion or visual approval.
Use it only where flow and residual-risk distinctions carry the source-backed claim.

## 5. Produce with bounded ownership and resumable provenance

Benchmark a real representative native frame and record engine/device/AA/shadows.
Do not silently lower quality to hit an ETA. Keep the approved renderer and actual
animation sample rate explicit; encoded fps alone proves neither native 3D nor motion.

Use the shared nonblocking render lock; report busy and exit, with no wait loop. Keep a
supervising owner live for long production or use the supported persistence mechanism.
Short-lived helpers may finish bounded probes/code; do not assume their children will
survive helper cleanup. Require a handoff with frozen-input checks, all-unit native
verdicts, pilot hash/QA, full expected contiguous ranges, a validate-only command and
one supervisor command that owns render → composition → encode → post-encode QA.
Run validation in the parent, verify the pilot hash/decode and inspect actual encoded
pilot evidence. Once required preflight gates pass under existing production/style
approval, launch the full supervisor with persistent ownership and completion
notification in the same turn; do not leave an authorized chapter at ready-to-run.
Verify a live renderer and distinguish full-production progress from a previous
pilot's shared progress file by checking the mode and required frame range.
Save per-shot checkpoints, input signatures and real produced frame manifests.
Report completed valid frames, not extrapolated progress.

After interruption, reuse only complete matching shots with contiguous ranges and
matching input/style/camera signatures. Preserve partial directories and rerender an
incomplete shot into a fresh directory. Verify exactly one current source per expected
global frame before encoding. A newly created hash baseline proves current integrity,
not missing historical provenance. Fix encoding/extraction defects at that stage rather
than rerendering valid native frames or paying for fresh speech.

## 6. Review the actual encoded master on separate axes

1. **Technical integrity:** probe counted frames, dimensions/fps/SAR/pixel format,
   audio stream and duration; decode the whole file; check audio peak/RMS/clipping.
   Compare original/decoded waveform where useful. Correlation does not establish
   pronunciation, listening or source accuracy.
2. **Semantic coverage:** extract evidence from the selected master, identified by
   hash. Review every unit with exact narration and its contract, including relevant
   before/transition/settled states. Review a moving excerpt when causality or non-action
   depends on timing. Maintain unique-ID coverage against the utterance manifest.
3. **Cuts and typography:** inspect cut +0 / +0.08 / +0.17 / +0.4 seconds, clamped to
   the shot. Copy swaps instantly; never crossfade different strings. Check actual-font
   bounds, later opaque fills, labels, captions and focal-object clipping.
4. **Settled connectors and logic:** inspect after reveal completes AND immediately
   before the cut. Follow a questionable branch through the intervening clip. A
   progressive stroke is not a persistent defect, but an endpoint gap must not be
   excused as animation. Confirm source/target attachment, direction and readable hold;
   distinguish regular intentional dash spacing from a missing terminal segment or an
   unintended break. Inspect the full-size endpoint and the declared relation style
   before accepting a reviewer's gap finding; then test phone-size readability, since
   numerically attached dashes may still be visually ambiguous. Keep required-condition
   paths and broken relationships visually distinct. Do not add a permission arrow just
   to appease a gap review: changing the arrowhead can turn necessity into sufficiency.
   Check both inputs for conjunctions and necessary-versus-sufficient wording.
5. **Phone legibility:** derive from that same MP4; check primary labels and secondary
   qualifications, not just subtitles. Promote any condition, exception or attribution
   needed to prevent a false reading into the main diagram or a dedicated readable beat;
   do not hide it in a small low-contrast source footer. Verify its actual dwell time at
   phone size. A technically decipherable still does not establish rapid reading, and
   full-size screenshots do not establish phone readability.
6. **Independent supervisor pass:** re-open the selected MP4 and evidence yourself;
   do not inherit an author's or child's all-PASS summary. Resolve unit ID → timestamp →
   frame hash → contact-sheet tile before review. Sheet geometry must include every tile.
   Give reviewers exact narration, phase times and intended action strength. Distinguish
   a progressive reveal from a settled gap, context established in preceding utterances
   from a genuinely missing label, and frightening/chasing from completed defeat.
   If still samples cannot establish retreat, restraint or failed resistance, inspect
   the moving excerpt before clearing that action gate; retain ACTION_CHECK_PENDING
   instead of turning labelled intent into proven action. Treat reviewer
   misidentifications as leads to verify, not automatic source corrections.
7. **Honest scope:** record reviewed IDs/timestamps and reviewer identity. Sampled
   semantics, continuous playback, full human viewing, full listening, source fidelity,
   technical integrity and user aesthetic acceptance remain independent. User approval
   of the result does not retroactively run omitted audits or erase observed defects.

For large FFmpeg selects, use bounded batches or a balanced expression tree. Parser
recursion can cause `Cannot allocate memory` without a damaged MP4. Retry extraction,
validate frame-index mapping, and rerun the affected QA rather than rerendering scenes.

## 7. Repair locally, reconcile findings, then report

When independent review contradicts an all-PASS report, keep the attributed original
review as history but update the current canonical ledger/summary with the unit, master
hash, evidence times, wrong reading and disposition. Normalize reviewer ID fields to
the production manifest, assert disjoint review partitions and an exact union of all
required IDs, then compute verdict totals in code. Retain separate source, visual,
action, phone and technical gates; do not turn a partial action reading into a generic
PASS because no contradiction was found. Keep the original ledger as an immutable
backup before reconciliation. A disclaimer in chat alone does not reconcile stale QA.
Keep unresolved required gates PARTIAL/FAIL and unrun checks NOT_RUN even if the user
likes the result.

An on-screen editorial or unverified-source notice does not substantiate a factual
superlative in frozen narration. Audit such claims before reusing speech; if the audio
is locked, preserve it and keep source fidelity PARTIAL until supporting evidence or
an explicitly authorized wording/audio correction resolves the claim. Make the
notice readable without suggesting that a larger disclaimer alone clears source QA.

Fix pixels in a fresh build; preserve approved audio/source and earlier masters. Rebuild
all affected native/composed frames, encode a new master and regenerate derivatives.
If shared diagram logic changes, inspect all affected units, not just the reported one.
Reuse prior inspection only for byte-identical samples with identical extraction
settings; identical midpoints do not prove unchanged transitions or motion. Distinguish
that inspection-reuse requirement from a fresh renderer replay: if rerendered image
hashes differ, measure decoded pixel differences and inspect the fresh output rather
than asserting byte equality or treating the mismatch alone as a semantic defect.
Report exact-hash integrity and approximate visual reproducibility separately; tiny
raster differences do not justify silently inheriting an earlier review verdict.

### Targeted revisions without a full native rerender

Keep a per-unit provenance map for mixed old/new builds. Rerender every frame of each
changed shot and preserve the original complete checkpoint, exact source/renderer/
style/timing hashes and frame hashes for each reused shot. A new global renderer hash
must not silently bless old caches; conversely, do not rerender an entire chapter only
to satisfy a naive global-hash cache key when unchanged per-unit contracts and their
original producing code are independently verified. Require exactly one selected
source for every global frame and assert unchanged duration, IDs and boundaries.
Never modify the old build to make its checkpoints match the new implementation.

Re-encoding a repaired chapter can change decoded pixels in neighboring untouched
shots through inter-frame compression. Compare identical extraction settings across
ALL unit IDs, not only planned repairs, and reinspect every changed sample—including
untouched neighbors. Keep unchanged-native provenance separate from encoded-image
byte equality. Do not inherit visual review merely because a shot was not scheduled
for native repair. Preserve all old/new comparison mappings and cutoff samples.

When speech is unchanged, keep the original WAV and provider metadata immutable and
prefer copying the existing encoded audio stream when container/timeline settings
permit it. Verify both source-WAV identity and extracted encoded-stream identity;
stream-copy success does not prove pronunciation or listening. Rebuild timing from
measured audio only if the audio or gap policy actually changes.

Report the actual artifact, what was verified and what remains unverified. When the
user asks to see work in progress, attach the requested real MP4 if it exists, labelled
review copy when gates remain open; do not substitute a directory, HTML gallery or an
older rejected version. Attach a short pilot as a pilot, never as the full chapter.
Production completion and chat attachment do not grant public-release rights.

## Synchronize public skill and asset repositories safely

Synchronize the reusable behavior, not the entire private installation byte-for-byte.
Inspect target remotes, visibility, branch and existing dirty edits; stage only the
intended paths and preserve unrelated work. Export private references through an
explicit sanitized file list: remove local production paths, personal context,
source text, speech, videos and uncleared models. Preserve public TTS/default-2D
contracts when they intentionally differ from the installed private profile. Keep
native reusable source in the separate asset repository, with license notices,
manifest hashes and a real clean-runtime render/import test. Verify documentation
links and unchanged non-3D sections; run existing asset tests before committing.
After pushing each repository, read the exact remote ref/commit back before claiming
synchronization. A local commit or successful-looking push alone is insufficient.

## Reusable public assets

For chapter-based pattern selection and links to generic public asset proofs, read
[`native-reference-patterns.md`](native-reference-patterns.md). The four private
chapter videos are not bundled; use a separately maintained local viewing index for
exact master revisions and timecodes. Start from one relevant pattern rather than
repeating an entire film's design or review.

Use the separately maintained [native Blender asset pack](https://github.com/denim-claw/prince-core-blender-assets)
for original procedural people, props and native hybrid helpers. Read its README,
manifest, notices and actual proof scope before reuse. Static figures are not natural
locomotion rigs; a generic smoke test does not establish narrated source fidelity or
full human viewing/listening. The portable Three.js kit remains available through
[hybrid-3d.md](hybrid-3d.md); do not silently switch an approved native job to it.
