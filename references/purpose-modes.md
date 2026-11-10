# Purpose modes — why is the viewer watching?

Ask once, before the scene table: **"어떤 목적이세요?"** The answer changes structure,
length, example coverage and the fidelity threshold. It does not change the rules that
hold in every mode: no verbatim narration of the work, attribute the author's claims to
the author, keep conditions and exceptions, pre-TTS fidelity gate, paid-TTS approval.

| | ① 얼개 — before study | ② 갈무리 — after study | ③ 상세 — full understanding |
|---|---|---|---|
| Viewer goal | Get a map, then read the source and note what is unclear | Retrieve what was read and connect the concepts | Understand the whole range from the video alone |
| Structure | Range map (questions, key terms, flow) → core claims in source order → "questions to check while reading" | Question first (retrieval) → answer → concept map → explain-it-yourself prompt | Source order; every claim, condition, example and self-check |
| Examples | One representative example per claim; name the rest with their page ("p.xx 사례 더 있음") | Name examples only as short cues | All, condensed but present |
| Page marks | Every scene, on screen (for notes) | Page index per concept | Every scene, on screen |
| Length (≈10 source pages) | 3–4 min | 2–3 min | 6–9 min |
| Fidelity threshold | 100 % of core claims and their conditions; omitted examples listed in the fidelity report | 100 % of core concepts | 100 % of inventory units, checked in code |

## Rules

- No answer → ③. It is closest to the default explainer and least likely to drop content.
- Several modes chosen → one source inventory (units with page ranges) and one fidelity
  base; then a separate plan, narration, TTS cache, captions, QA and master per mode, like
  language variants. Use separate output directories so audio caches never collide.
- Build ③'s inventory first even when only ① or ② is requested: the shorter modes are
  derived from it, and their coverage threshold is checked in code against that list.
- A correction found in one mode applies to every mode, including on-screen labels.
- ② must not introduce content the source range lacks; a retrieval question needs an
  answer that is in the range.
- Learning benefit of any mode is a design hypothesis unless a learning test was run.
