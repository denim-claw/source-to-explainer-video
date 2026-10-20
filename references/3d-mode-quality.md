# concept-3d — renderer contract and blocking quality gates

This optional mode extends source-to-explainer-video. It does not replace concept-2d.
Read renderer-notes.md, hybrid-3d.md and the asset repository notices first. Do not revive rejected diorama
or popup layouts as templates. For both concept-3d and narrative-3d, apply
`3d-hybrid-production-review.md` to route claims, gate native preflight separately from
encoded acceptance, inspect settled connectors and reconcile supervisor findings.
This extension is conditional on a 3D mode; it does not redefine concept-2d.

## Production route

1. Fix source, script and claim→visual-action map using the shared workflow.
2. Declare visual_mode=concept-3d, aspect, dimensions, actual animation sample fps,
   encoded fps, renderer and asset manifest in scenes-draft.json / toolchain.json.
3. Choose assets against the visual brief: lightweight primitives for abstract relations
   or labelled functional preflights; verified meshes/rigs for anatomy-sensitive narrative
   quality upgrades. Use Blender for authored geometry/rigging and export glTF/GLB for
   Three.js, or render in Blender directly. Not every job needs both engines. Record
   which actually ran; never claim Blender from a planned exporter. Benchmark real
   rendering separately from judging art or clearing asset redistribution rights.
4. Separate 3D stage from screen-space typography. Render the scene, then composite
   labels/subtitles in a true screen-space pass (DOM/canvas overlay, orthographic UI
   scene, or offline compositor). Do not estimate a UI plane's dimensions in world space.
5. Implement renderAt(t) deterministically with seeded noise and loaded local assets.
   Animate all delivered frames at the declared sample rate; default 30 unique time
   samples per second. Duplicating sparse stills into a 30fps stream is not 30fps motion.
6. Produce a 5–10s narrated preflight with each new technique and the hardest layout.
   Check it before full rendering. Reuse valid cached speech for layout-only fixes.
7. Full render → audio/captions → encoded-file QA → fidelity audit → package.

## Machine gates (fail closed)

- Exact aspect: width*9 == height*16 for landscape; width*16 == height*9 for portrait.
  Check actual viewport, framebuffer/capture, compositor AND encoder, SAR=1, no
  unexpected rotation metadata. No cover-style scaling or crop as an overflow fix.
- Use an isolated frame directory per build and numbered contiguous frames. Assert
  frame count, size and dimensions for every frame; never glob mixed stale frames.
- Project registered focal-object bounds into camera screen space at all keyframes and
  motion extrema; include near/far visibility. Record object IDs and pixel bounds.
  Do not use the giant decorative ground plane as the focal-object bounding box.
- Measure all text bounds using the actual font. Assert safe-frame containment, stage /
  caption separation, and text↔text, text↔later opaque fill, label↔object occlusion checks.
- A collision/semantic test with zero registered objects is 'not run', not a pass.
- Cues, cuts, captions and total timeline derive from measured audio. Frame grid rounding
  is explicit; the last spoken clause must remain audible, with a short ending hold.
- Record distinct animation sample rate separately from encoded fps. Semantic before /
  after samples must actually show the claim's relationship changing, not only noise.
- ffprobe counted frames / audio streams / sample rate, full decode with empty stderr,
  peak/RMS/clipping and same-machine seek determinism remain required.

## Visual gates (independent of codec validity)

Review frames extracted FROM THE SHIPPED MP4, not authoring screenshots:
- each scene start; every cut at +0, +0.08, +0.17, +0.4s;
- before/after semantic anchors; intermediate morph states; motion extrema;
- longest subtitles and widest labels; first and final frame;
- full-size and phone-size derivatives (640×360 landscape; 360×640 portrait).

Reject if ANY focal item or text is accidentally cropped, unreadable, hidden behind
another object, distorted, or colliding with captions. Reject popup/narration-card UI,
decorative camera movement sold as explanation, and static-frame sequences sold as
animation. The reviewer must name actual frames, observed issues and their disposition.

Do not trust a vision tool's generic 'looks good'. If its description disagrees with
known scene contents, or the user reports clipping, treat the review as unreliable:
inspect the image directly using browser capture/available image loading, pixel crops,
font bboxes and projected coordinates. Do not repeatedly ask the same model to approve
the same image. User rejection blocks claiming acceptance.

## Required QA fields

qa/qa.json: master_sha256, dimensions, sar, dar, viewport, capture_dimensions,
render_sample_fps, encoded_fps, frame_count, timeline_seconds, full_decode,
text_bounds_checks, focal_bounds_checks, occlusion_checks, audio_checks, determinism.
qa/visual-review.json: master_sha256, sampled_timestamps, phone_derivatives,
observed_defects, unresolved_defects, reviewer_type, limitations, acceptance.
Set acceptance='rejected' or 'pending' if any required check is absent/unresolved.
Never say 'verified finished' based solely on ffprobe. Fix → rerender → regenerate
all derivatives and reports; do not resend the rejected master as a corrected version.
