# Source fidelity — a separate check from "the video plays"

## Per-scene source map

Keep these fields in the scene JSON or a companion table:

- printed / PDF page range and section
- the source claim, plus its conditions and exceptions
- how the video expresses it
- **which part is source-derived, which is an invented metaphor, which is added commentary**
- what was condensed or omitted, and why

## Dangerous transforms to refuse

- Turning one person's case into a general prescription.
- "Own the outcome" read as "do all the work alone".
- "You don't need to be the technical expert" read as "don't learn the technology".
- "Build autonomous teams" read as "the PM role is worthless".
- Presenting diagram sizes, particle counts or coordinates as measured data.
- Attributing your own framework (a cycle order, a bottleneck graph) to the original author.
- Confusing a *reporting* figure with an *editorial* one, or a vendor benchmark with an
  independent measurement.
- Presenting an experimental protocol as a recommendation for production use.

## Coverage and second pass

- Compare section/claim/exception/self-check lists against the actual source inventory in
  code, not by memory.
- Re-read the source per scene and diff the sentences. Distinguish "wrote the script after
  reading once" from "ran an independent second-pass audit" — and if a separate reviewer
  did not review it, do not claim one did.
- Do not convert user satisfaction into factual approval.

## Verbatim-run check (automatic)

`example/verbatim_check.py --source <private transcript> --plan scenes-draft.json` normalises
both sides (Unicode NFKC, then removes whitespace and punctuation) and reports every run of
at least `--min` normalised characters (default 15, about 20 with spaces in Korean) that
appears in both narration/on-screen text and the source. Quoted key phrases can be allowed
with `--allow`. Keep the transcript inside the private source folder; the report stores only
the matched run, scene id and length, not surrounding source text. Without a transcript the
check is unrun: say so.

OCR transcripts break runs at misread characters (one bad glyph splits a 19-character copy
into 13 + 5), so use `--min 12` on OCR text and keep the deliberately quoted key phrases in an
`--allow` file. An allowed phrase is cut out of a run before the length test, so a quote plus
a particle passes while a long copy next to a short quote still fails. For an image-only scan
without Korean OCR data, `tessdata_best/kor.traineddata` in the private source folder with
`--tessdata-dir` is enough; keep transcript and model out of the repository.

## Privacy and copyright

- A user-supplied personal scan is an authorised analysis source. Never copy the PDF, the
  full OCR text, or long verbatim passages into a deliverable package or a shared skill.
- Explain in your own sentences; keep page/section for short key phrases.
- Distinguish independent explanation from whole-work narration.
- Bundled fonts must carry their own licence file; do not ship a font you cannot license.
- Reference lists keep the original author's naming. If the source's romanisation of a
  name is uncertain, keep the source-language name rather than inventing a spelling.
