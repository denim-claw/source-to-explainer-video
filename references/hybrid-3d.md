# Hybrid diagrams and short 3D narrative shots

Keep concept-2d the default. Select concept-3d for genuinely spatial relations and
narrative-3d for concrete actions/events. Hybrid argumentative material should alternate
only when the claim benefits: abstract trade-offs use diagrams, concrete abandonment
or destruction uses legible actions. Figures idling near boxes are not an explanation.

## Reusable kit and rights gate

Read [the kit API](../assets/hybrid-3d/README.md) and
[third-party notices](../THIRD_PARTY_NOTICES.md) before import. The repository bundles
original MIT procedural people, houses/sets, lion/fox/wolf, camera fitting and CC0
fire/smoke PNG atlases. Prefer those over searching afresh or rebuilding crude fire
cones. Do not infer an imported asset from a suggested asset-store link.
An output license is not a source-redistribution license. Record each imported file's
origin/license/hash. Unknown or paid source rights block public packaging. A sprite
flipbook is flat imagery; never call it a volumetric simulation or recorded footage.

## Camera and staging

- One immutable camera/lens **per shot**, change framing only at cuts. Never re-fit
  each frame: automatic following cancels the apparent walking/departure.
- Fit the full-shot motion union of the selected focal objects, not the whole world.
  Cut to a medium/close shot for consequence; do not make all actors microscopic.
- Actors must have a visible facing cue; animals need distinctive silhouettes (mane,
  pointed ears, muzzle, brush tail). Markers or eyes alone are not animal models.
- Root coordinates: people face +Z; animals face +X. Pose absolute transforms and
  preserve base scale. Do not mix a factory wrapper with its .root Object3D.
- Fire needs depth occlusion, enough emitter area and independent light/gain; adding
  one glowing image is not lighting integration. Check encoded frames for overexposure.
- Stylized gaits have no foot-lock/IK/physics. A sampled bounding-box pass proves
  framing at those samples, not readable acting, source fidelity or user approval.
- Constructed events, destruction methods and reactions not specified by the source
  must be disclosed as illustrative reconstruction, not historical fact.

## Timing and output checks

Synthesize sentence-level speech only when a narrated output is requested. Preserve
recorded provider/model/voice and actual PCM timings; effect/layout fixes reuse audio.
Do not silently replace the configured default TTS provider or generate paid speech
for a silent asset test. Captions follow measured utterance boundaries; keep captions
in stable screen space below the geometry, not as overlapping popup narration cards.
Full-chapter coverage means each argument, condition, exception and example has a
source mapping, **not** that a compressed summary is a verbatim translation.

Use `renderAt(t)` with no wall clock or incremental transforms. For software WebGL,
benchmark a short true render before promising a full-render ETA. Disable shadow maps
and MSAA if measured costs require it; cheap ground shadows can keep bodies legible.
Inspect actual encoded frames, before/after semantic anchors and cut +0/.08/.17/.4 s;
check same-machine reversed seeks separately from technical decode/source fidelity.

## Runnable public proof

[example-3d](../example-3d/README.md) uses only bundled textures/code and a pinned npm
lockfile. It is an original **silent asset demo**, not a narrated explainer, book
chapter, full-source review, user approval or proof of caption/audio synchronization.
Run the Node unit tests, asset hash/grid checks and browser proof before packaging.
Keep changed-file rights and secrets checks separate from visual review. Never publish
private chapter assets just to demonstrate the public skill.
