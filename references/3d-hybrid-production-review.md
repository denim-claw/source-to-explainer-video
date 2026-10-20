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

Major contradictions, missing central meaning and ambiguous causal agency block the
full render. Review native evidence here; do not require a nonexistent full master to
pass preflight. Conversely, a preflight pass cannot be reused as encoded acceptance.

## 5. Produce with bounded ownership and resumable provenance

Benchmark a real representative native frame and record engine/device/AA/shadows.
Do not silently lower quality to hit an ETA. Keep the approved renderer and actual
animation sample rate explicit; encoded fps alone proves neither native 3D nor motion.

Use the shared nonblocking render lock; report busy and exit, with no wait loop. Keep a
supervising owner live for long production or use the supported persistence mechanism.
Short-lived helpers may finish bounded probes/code; do not assume their children will
survive helper cleanup. Save per-shot checkpoints, input signatures and real produced
frame manifests. Report completed valid frames, not extrapolated progress.

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
   label knockouts or dashed strokes must still read as a connected relation at phone
   size. Check both inputs for conjunctions and necessary-versus-sufficient wording.
5. **Phone legibility:** derive from that same MP4; check primary labels and secondary
   qualifications, not just subtitles. A technically readable small qualifier may still
   fail rapid phone viewing. Full-size screenshots do not establish phone readability.
6. **Independent supervisor pass:** re-open the selected MP4 and evidence yourself;
   do not inherit an author's or child's all-PASS summary. Resolve unit ID → timestamp →
   frame hash → contact-sheet tile before review. Sheet geometry must include every tile.
   Treat reviewer misidentifications as leads to verify, not automatic source corrections.
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
hash, evidence times, wrong reading and disposition. A disclaimer in chat alone does
not reconcile stale QA. Keep unresolved required gates PARTIAL/FAIL and unrun checks
NOT_RUN even if the user likes the result.

Fix pixels in a fresh build; preserve approved audio/source and earlier masters. Rebuild
all affected native/composed frames, encode a new master and regenerate derivatives.
If shared diagram logic changes, inspect all affected units, not just the reported one.
Reuse prior inspection only for byte-identical samples with identical extraction
settings; identical midpoints do not prove unchanged transitions or motion.

Report the actual artifact, what was verified and what remains unverified. When the
user asks to see work in progress, attach the requested real MP4 if it exists, labelled
review copy when gates remain open; do not substitute a directory, HTML gallery or an
older rejected version. Attach a short pilot as a pilot, never as the full chapter.
Production completion and chat attachment do not grant public-release rights.

## Synchronize public skill and asset repositories safely

Synchronize reusable behavior, not an entire private installation byte-for-byte.
Inspect remotes, visibility, branch and existing dirty edits; stage only intended
paths and preserve unrelated work. Export through an explicit sanitized file list:
remove local production paths, personal context, source text, speech, videos and
uncleared models. Preserve intentional public TTS/default-2D contracts. Keep native
reusable source in the separate asset repository, with notices, manifest hashes
and an actual clean-runtime render/import test. Verify documentation links and
unchanged non-3D sections; run existing asset tests before committing. After each
push, read back the exact remote ref/commit before claiming synchronization.

## Reusable public assets

Use the separately maintained [native Blender asset pack](https://github.com/denim-claw/prince-core-blender-assets)
for original procedural people, props and native hybrid helpers. Read its README,
manifest, notices and actual proof scope before reuse. Static figures are not natural
locomotion rigs, and a silent generic smoke test does not establish narrated source
fidelity or full human viewing/listening. The portable Three.js kit remains available
through [hybrid-3d.md](hybrid-3d.md); do not silently switch an approved native job to it.
