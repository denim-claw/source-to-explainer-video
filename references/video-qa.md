# Encoded-file QA — the checklist that actually catches defects

Applies whenever a rendered video is about to be reported as finished.

## Verify the encoded file, never the authoring surface

```bash
ffprobe -v error -count_frames -show_streams -show_format -of json master.mp4
ffmpeg  -v error -i master.mp4 -f null -            # require empty stderr
ffmpeg  -v error -y -ss 12.5 -i master.mp4 -frames:v 1 out.png
```

- Counted frames must equal `round(duration × fps)` for the intended fps.
- Audio stream count, channel count, sample rate and codec are asserted, not assumed.
- A file can probe clean and still contain broken frames — the full decode is separate.
- A live preview, a browser screen recording, or a snapshot of the authoring surface
  is **not** evidence about the encoded file.

## Copy and cuts — the failure that layout audits miss

- Author a copy change as an instant swap at the cut. Fading in from zero opacity
  blanks the text for ~0.15 s; cross-fading two strings double-prints them.
- Signal the cut with a non-text element (rule, tick, wipe) that visibly re-draws.
- Inspect frames straddling **every** cut: the cut time, +0.08 s, +0.17 s, +0.4 s.
- Check every element whose copy swaps, not only the headline.
- Audit text against occluding shapes: compare node-label bounding boxes with the full
  card rectangle including fill and border. A card painted later can clip a label even
  when text↔text collisions are zero.
- Sample intermediate morph phases and progressive-drawing phases, not only end states,
  then confirm the fix in the encoded file.

## Derivatives and hashes

- ONE script owns every derivative (scaled previews, extracted frames, contact sheets,
  phone crops) and regenerates all of them from the master.
- Hash the shipped master and archive at the end of the run; write every reported
  number from those hashes.
- Re-confirm the on-disk artifact still matches the recorded hash immediately before
  reporting — another process sharing the tree can rewrite it.
- Archive: test CRC, count entries, assert exclusions (no `node_modules`, secrets,
  temp renders, or media you did not mean to ship). Report archive size separately
  from video size.
- Runnable-source proof: extract to a clean directory and render a real short narrated
  MP4 with only bundled code/fonts/audio; probe, count frames, decode fully, and
  compare representative full-timeline RGB hashes with the original renderer. State
  the scope: short replay + timeline samples ≠ a second full-length encode.
- Record toolchain provenance: pinned versions, native library versions, and the
  built-in encoder tag of the produced file when it disagrees with the installed
  package.

## Motion claims

- Pixel change proves motion, not meaning. If you assert that a diagram now shows a
  different relationship, sample the before/after states **at the real transition
  anchor**, clamped to the scene range — fixed scene percentages can land entirely
  before a late transition.
- If a motion-assertion pass exists but no assertions were registered, say the pass was
  disabled. Never present a dismissed check as a pass.

## Reporting

- Korean summary for min: absolute paths to every artifact, then only numbers the
  verification artifacts actually produced.
- Name the audits that did not run (full human listen, ASR pronunciation, forced
  alignment, independent content review) explicitly.
- Present the asset as a draft when approval is a separate step; list pending
  approvals separately (legal/review, platform safe areas, unverified data).
- Ship the file over the interface's native attachment the moment a verified master
  exists.
- A late internal completion notice for a step already polled and delivered is not new
  work: do not re-render, re-send or repeat viewing links.
- Reduced-size phone frames are legibility QA, not compliance approval.
