# Renderer notes — 1280×720 frame renderer (Pillow + CairoSVG + FFmpeg)

## Structure

- Cache font objects, glyph tiles and per-scene backgrounds. Position, phase and
  progress come only from `t`.
- Scene selection: `bisect` over accumulated start times. Never leave accumulated state,
  so reverse-order seeking yields identical frames.
- Push `rgb24` frames into the FFmpeg process on `stdin` together with the measured
  narration and the `mov_text` subtitle track.
- Use fixed seeds / deterministic coordinates. No meaningless random jitter.

## Layout (1280×720)

| Band | Range | Notes |
|---|---|---|
| Header label | y≈26 | small, muted, project · unit · chapter |
| Title | y≈69, 40 px | never fades; swaps instantly at the cut |
| Section line | y≈133, 21 px | source scope, e.g. `§2.3 · printed pp.41–44` |
| Cut rule | y≈174 | the non-text cut signal |
| Diagram | y≈190–590 | keep every element inside this box at both ends of any morph |
| Annotation strip | y≈552–583 | reserved slack; exactly one semantic sentence |
| Caption band | y≈605–691 | 26 px, at most 2 lines, wrapped at real pixel width |
| Progress rule | y≈600 | grows with `t / total` |
| Footer | y≈698, 12 px | attribution + "own diagram / independent explanation" |

Check legibility at 640 px width. Do not claim the tiny footer is readable there.

## Text safety

- Measure with the real font (`ImageFont.getlength`) — never estimate character counts.
- Wrap long strings at word boundaries into at most two caption lines; longer strings
  become multiple caption chunks inside the same measured scene.
- Draw a background knockout behind text that crosses a connector or node.
- Text-vs-text collision checks are insufficient: compare **node-label bounding boxes
  against card fill rectangles** too, since a card painted later can clip a label.
- Assert `label_width <= card_width - 12` for every boxed label; a silently clipped
  label is the most common defect.

## Semantic animation vocabulary

- **Transition morph** — one shape with a fixed correspondence between start and end
  states (e.g. an N-point loop sampled by arc length between a rectangle and a circle).
  The same vertices must carry through, so the viewer reads *one object changing
  meaning*, not two shapes swapping. Label both states and label the endpoints.
- **Progressive drawing** — reveal boxes and connectors in the order the narration
  introduces them, each over ~1 s, with intermediate phases sampled for QA.
- **State replacement** — a card's text becomes another card's text at the anchor where
  the claim changes; the old state is not deleted, it is shown as replaced.
- **Path opening / closing** — a blocked connector becomes open (or the reverse) to show
  a bottleneck clearing or a loop closing.
- **Sequential activation** — checklist items light up as their sentence is spoken.

Not acceptable as explainer animation: percentage-based shaking of the whole diagram, a
single shared curve reused for every scene, three fixed labels carrying an entire scene,
or particles whose movement implies a claim that is nowhere stated.

## Copy at cuts

- Instant swap at the cut. No string cross-fade, no fade-in from zero opacity.
- Respect the frame grid: a nominal cut between frames resolves to the previous frame,
  which is why +0.08 / +0.17 / +0.4 s samples matter.

## Audio

- Distinguish the TTS WAV rate from the delivered AAC rate; after `loudnorm` the encoder
  rate can drift, so pass `-ar 48000` explicitly.
- Default narration candidate: mono 96 kbps AAC. A lighter copy is optional and must be
  described as lossy, not as equal quality.
- Peak/RMS/clipping checks never substitute for human listening.

## Verification boundaries

- Renderer determinism, encoded frame change, full decode, and source fidelity are four
  different checks. Never use one as evidence for another.
- Fixing one footer string invalidates the master, derivatives, reports and archive —
  regenerate them together, then re-inspect only the frames whose bytes changed.
- Keep original production QA separate from prototype/preview QA.
