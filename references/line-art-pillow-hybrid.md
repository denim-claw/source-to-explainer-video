# Optional Pillow × SVG line-art scenes

Use line art selectively when people, their actions or relationships, or a spatial setting are necessary to the explanation. Prefer labeled diagrams, flows, and exact charts for models, agents, and data; do not add humanoid figures merely to represent software. Keep the project's established typography, palette, narration and captions. Review one 15–20 second scene before extending the treatment.

- **Pillow owns** the background, diagrams, data, titles and the single caption layer. **SVG owns** the actor and prop layers. Produce true transparent RGBA, not a keyed screenshot. Test edges, painted bounds, excluded regions and unchanged pixels where actor alpha is zero.
- Define scene-local motion in **sample-anchored time groups**, separate from layout slots. Test moving the group without changing event order, and moving or resizing a slot without changing its event times. Inspect whether the painted arms and props cross captions or data.
- Bake springs on a fixed 60 Hz grid; make `__render(t)` an absolute, repeatable render. Compare both SVG and PNG on forward and reverse seeks. State which actor owns and handles a prop, who makes a decision, and what the source actually supports.
- Use **decoded PCM samples**, not MP3 container duration or character count, as the authoritative clock. Render the final output and check decoded audio, scene transitions, captions and representative phone-size frames. Technical compositing success does not establish visual quality or improved learning.

## Included tools

- [SVG assets and capture demo](../assets/line-art/README.md) — MIT upstream notice included. The bundled example does not include any narration or project footage.
- `scripts/hybrid_scene.py` — time groups, layout slots, actor/prop ownership checks and transparent compositing.
- `scripts/build_narration_timing.py` — assemble per-utterance audio into a mono WAV plus `timing.json`. Older seconds fields are derived from integer samples. Example: `python3 scripts/build_narration_timing.py --out output first.mp3 second.mp3`. For existing single-take narration workflows, keep their measured alignment path.
- `python3 scripts/test_hybrid_scene.py` — synthetic layout, alpha, semantic ownership and FFmpeg MP3 padding regression checks. Requires Pillow and FFmpeg/ffprobe.
