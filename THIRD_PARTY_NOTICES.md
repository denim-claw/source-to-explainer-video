# Rights and provenance

## This 3D addition

- Original procedural JavaScript (people, sets/house, animals, fixed-shot camera,
  fire/smoke compositing) and the silent demo: repository MIT license.
- `assets/hybrid-3d/textures/*.png`: **Unity Technologies / Unity Labs Paris,
  CC0 1.0 Universal**. These files are expressly excluded from the repository's MIT
  grant; their original CC0 dedication applies. Attribution is recorded as provenance,
  not imposed as a new CC0 condition. No Unity or Creative Commons logo is bundled.
- Source: Thomas ICHÉ, [Free VFX image sequences and flipbooks, 2016-11-28](https://unity.com/blog/engine-platform/free-vfx-image-sequences-flipbooks).
  The official page explicitly releases the listed sequences under CC0 and lists
  Flame02, Flame03, WispySmoke01 and WispySmoke02.
- We unpacked each named `*-flipbooks.zip`, converted its **TGA**, not its HDR EXR,
  to RGBA PNG, and preserved the pixel content. `textures/manifest.json` records
  source URLs, ZIP/TGA/PNG SHA256, dimensions, grids and transformation.
- CC0 permits commercial reuse, modification and redistribution of the dedicated
  copyright rights. It does not grant trademarks/patents or guarantee other rights.
  See [full legal code](assets/hybrid-3d/textures/CC0-1.0.txt) and
  https://creativecommons.org/publicdomain/zero/1.0/ . No endorsement is claimed.

## Dependencies and tools (not vendored)

`package-lock.json` pins the optional 3D test/demo dependencies. Three.js 0.186.1 is
MIT; puppeteer-core 25.14.0 is Apache-2.0. npm retains their own license/notice files
in node_modules. Dependencies do **not** become MIT through this project. System
Chromium and FFmpeg are external tools with their own licenses; no browser binary,
FFmpeg binary, fonts or node_modules are redistributed in this addition. H.264 patent
licensing is outside the copyright grant. Redistributing a complete application,
container or toolchain requires a separate dependency/license review.

## Explicitly not included

Private book-chapter videos, Gemini recordings/provider metadata, full Gutenberg
chapter files or translations, protected-page setup links, publish/auth credentials,
.env files and local render logs. No Kenney/Quaternius/ActionVFX/JangaFX asset was
imported by this change. Search results or a stock-media output license are not proof
of editable-asset redistribution rights.

Existing public examples retain their own source notices and licenses (including
Open Publication License, MIT and Apache-2.0); this addition does not relicense them.
The existing repository LICENSE says the same about third-party material.

This is a documented copyright/provenance check, not legal advice or a guarantee of
clearance in every jurisdiction or use. Verify additional image/personality/mark,
source-content, audio-service, commercial and patent requirements for your deployment.
