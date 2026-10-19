# Portable hybrid-3D kit

Code: MIT (repository `LICENSE`). Four PNG textures: CC0-1.0, **not** MIT.
See [THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md) and `textures/manifest.json`.
All texture files are included; no machine-local asset store or signed URL is needed.

```js
import * as THREE from 'three';
import {animalKit} from './animals.mjs';
import {FLIPBOOKS, loadFlipbookTexture, makeFlameCluster,
        radialGlowTexture} from './fx-flipbook.mjs';
const fox = animalKit(THREE).fox({scale: 0.9});
scene.add(fox.root);
fox.pose({phase: time * 8, stride: 1, turn: Math.PI});
const texture = await loadFlipbookTexture(THREE, new THREE.TextureLoader(),
  './textures/Flame03_16x4.png');
const fire = makeFlameCluster(THREE, {texture, spec: FLIPBOOKS.flame03,
  scale: 1.0, gain: 0.30, lightGain: 3.6,
  glowTexture: radialGlowTexture(THREE)});
scene.add(fire.root);
fire.update(time, 1);
```

Paths in this snippet are relative to this directory; resolve URLs against your page.
Make the scene and lights yourself; this is not an opinionated renderer.
Load textures **before** rendering. Runtime modules inject Three.js; none import a
private renderer, access a credential, or call a hosted generation API.

- `animalKit(THREE)` supplies `lion`, `fox`, `wolf`. Each returns `{root, pose}`.
  Animal forward is **+X** at yaw 0; yaw PI reverses it. +Y is up; root is at the floor.
  Pose uses absolute phase/turn/crouch/stride, not elapsed-frame accumulation.
- `actorKit(THREE)` in `../narrative-3d/actors.mjs` supplies articulated people:
  `{root,body,joints,pose}`. Human forward is **+Z**, intentionally different from
  quadrupeds. Human pose keys: walk, phase, bow, reach, stop, recoil.
- `setKit(THREE)` in `../narrative-3d/sets.mjs` supplies court, throne, chest,
  meetingRoom and house (all Object3D roots). `house` has a named `roof` child.
- Helpers returning `{root, ...}` must register/add **root**, never the wrapper.
- `fitFixedShot(THREE, shot, opts)` in `fixed-shot.mjs` fits a sampled full-motion
  union of explicit focal objects once. Keep its camera unchanged until a cut.
  Use `view:{w:1280,h:560}` to reserve a caption band; caller sets the viewport.
- `FLIPBOOKS.*.fps` is the authored **playback speed**, not claimed source capture fps.
- Fire: clone the texture per emitter; flip UV rows from the top-origin atlas;
  disable atlas mipmaps; use half-texel inset. Gain and lightGain are independent.
  Ground glow belongs to fire.root. Smoke geometry is scaled exactly once.
- Smoke uses normal alpha blending; fire uses additive blending. Both remain
  **flat camera-facing billboards**, not volumetric fire/light or real footage.
  `facing` is radians around +Y, fixed for the shot. Pick it for the locked camera.
- Everything is a stylized procedural approximation. Gaits have no IK/foot-locking,
  physics or mocap. Bounds checks are not proof that acting or explanation is clear.

Dispose geometries/materials, cloned maps and the shared source textures after use.
Never use a paid stock pack here just because its *rendered output* is licensed:
redistribution of editable source assets needs its own permission.
