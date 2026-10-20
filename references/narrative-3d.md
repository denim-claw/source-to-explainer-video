# narrative-3d — book ideas acted out, not diagrams in depth

## Mode choice

When the reference's appeal is a ruler walking, inspecting courtiers, issuing orders,
or subjects reacting, preserve that storytelling grammar for concrete events. Route
abstract claims separately: love versus fear, obligation, control and conditional choices
may use concise animated infographics within the same 3D production. Direct concept
labels above the graphic are appropriate; arbitrary numbered objects with a lookup legend
are not. Do not force every abstraction into difficult mannequin acting, or replace every
concrete scene with labelled symbols. Choose whichever visible change explains the claim
most directly. Do not interpret rejection of popup cards as rejection of character scenes.

3Blue1Brown-inspired art direction means restrained palette, clear composition,
coordinated narration and explanatory action. It does not mean every book must become
nodes, circles, arrows and graphs. Stylized miniature sets and faceless humanoids are
allowed; decorative clutter, unreadable UI and meaningless camera motion are not.

## Required production and review procedure

Read `3d-hybrid-production-review.md` for the complete 3D-only workflow and unit-ledger
fields. Classify each claim as concrete action, abstract relation or a deliberate mixed
shot; approve a narrated moving pilot covering both concrete and abstract treatment
before expanding. Do not use ever-denser still probes to compensate for an unreadable
visual grammar. Source fidelity, sampled semantics, continuous motion, technical QA and
user aesthetic acceptance are separate verdicts.

## Scene contract

Each shot lists: source claim; invented illustrative situation; character objective;
physical action; visible reaction/consequence; shot scale/camera; narration clause;
required assets/rig; and cut time derived from measured audio.

For a narrative-event shot, at least one character must perform a legible action that
changes another character's situation. 'Move a sphere' or 'orbit a static figurine' does
not qualify. Use a small cast, recognizable silhouettes, clear eyelines, plausible
feet/ground contact and an uncluttered set. For an abstract-relation shot, require a
readable animated contrast, connection or conditional branch instead of mandatory human
performance; direct labels may identify love or fear without a numbered key. Hold one
camera idea per shot. No popup paragraph or side narration panel. Dialogue/narration
remains in bottom subtitles.

For a 12-second Prince pilot, a possible ILLUSTRATIVE (not quoted historical) sequence:
- 0–4 s: ruler walks toward waiting courtiers; the courtiers turn and attend.
- 4–8 s: a restrained punitive command creates fear; show the order/response without gore.
- 8–12 s: ruler stops an excessive punishment or seizure; show the practical limit through
  action, not a floating warning line. The narrator attributes the argument to Machiavelli.
This is a storyboard seed, not a claim that these incidents appear in chapter XVII.
Change beats/timings to fit the verified script and measured audio.

Do not insert an eighteenth-century guillotine into a Renaissance scene as historical
fact. If a modern symbolic execution device is used, label the scene as an anachronistic
illustration; prefer period-neutral staging. Non-graphic punishment imagery is enough;
no need to simulate a beheading to communicate the claim.

## Assets needed before full render

Create/reuse a rigged humanoid with root, torso, head, upper/lower arms, upper/lower legs;
a distinguishable ruler (crown/cloak), 2–3 courtiers/guards, palace/courtyard floor and
simple architectural background, and only story-relevant props (throne, scroll, staff,
chest or restraint). Build reusable walk, stop, turn, look, gesture, recoil/bow clips.
Primitive-based rigs can work; melted shapes, sliding feet and static chess pieces do not.

Use hybrid-3d.md and the asset repository notices for licensing and durable roots. Prefer original procedural rigs or
verified commercially reusable assets with redistribution rights. Do not claim an asset
or clip exists until its code/model is actually present and tested.

## Approval gate before investing in full production

Render and inspect a representative action shot, not just a pretty still. Check walk
contact, silhouette, shot framing, eyeline/response, subtitle readability and whether
viewers can tell what happened without reading an explanatory popup. Technical QA alone
cannot approve narrative quality. Reject a narrative-event shot with no meaningful
performed action, even if it is 3D, plays cleanly and has no clipping. Judge an explicitly
routed abstract infographic by its visible relation and changing logic, not by the
presence of actor performance. In a mixed-style preflight, inspect both a concrete event
and an abstract relation before expanding to the chapter.

For model comparisons, both models receive the same narrative-mode brief and audio.
Require genuinely separate scene code. Verify actual model identity in usage records;
CLI requested model alone is insufficient when routing/fallback may select another model.
Report substitutions rather than calling a different model's movie an S5F result.
