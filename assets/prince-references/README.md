# Bundled Prince video references

Four actual MP4 files are included beside this file, not just links.
`manifest.json` records exact hashes, measured durations and ten useful excerpt ranges.
Total video size: 44,845,122 bytes. Original approved masters; no extra render/TTS.

## Pick the example that matches the task

- `prince-15.mp4`: compact abstract diagrams; negation and conditional use.
- `prince-17.mp4`: concrete cases followed by labelled abstract relationships.
- `prince-18.mp4`: animal-role metaphors and coequal lists/common branches.
- `prince-25.mp4`: connected flood/diversion, residual risk, actor motives and callbacks.

Start with one relevant excerpt from the manifest. Inspect the actual file with
available video tools or extract frames with FFmpeg. A file being bundled does not
mean it has already been viewed by the current agent. Record inspected scope honestly.
Use the visual pattern, not the previous chapter's narration or QA as a template.
Do not automatically re-review all four films, rerender them, or synthesize new audio.

Example (substitute the manifest's actual range and your scratch output path):

```sh
ffmpeg -ss 62.58 -i prince-25.mp4 -frames:v 1 reference-frame.jpg
```

## Known limits

- 15: editorial wording and a spoken qualifier retain source-review limitations.
- 17: one necessary-condition connector remains a clarity issue; do not copy it as a correct permission arrow.
- 18: one animal-action reading remains pending; the final modern superlative lacks comparative evidence.
- 25: final additional visual/ASR/full-listening checks were not run by user direction.
- Technical decoding and waveform checks are not full human listening or continuous semantic approval.
- The water is a kinematic illustration, not a fluid simulation or zero-risk promise.

## Source and third-party material

These are independently produced Korean explanations of a public-domain classic,
not recordings of a modern Korean translation. Chapters 15/17/18 use Luigi Ricci's
English edition (Project Gutenberg 57037); 25 uses W. K. Marriott (1232).
Gutenberg lists both editions as public domain in the USA; check applicable local law.

- Rendered font: Noto CJK, SIL Open Font License. Font binaries are not included here.
- Generated speech: Google Gemini (Orus / Charon); not recordings of actual speakers.
- Animal models: Cozy Animals 3D Models by Gamideo / dragofive,
  https://dragofive.itch.io/cozy-animals-3d . Publisher declares CC0 and Meshy AI origin.
  Upstream ownership has not been independently established. Raw models are not bundled.
- Original procedural toolkit: https://github.com/denim-claw/prince-core-blender-assets .

The repository's code license is not a warranty of rights in every generated output
or third-party component. Preserve source/asset credits and assess third-party terms
before further redistribution. No private source scans, account data or credentials
are included in this directory.
