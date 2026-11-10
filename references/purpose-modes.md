# Purpose modes — why is the viewer watching?

Ask once, before the scene table: **"어떤 목적이세요?"** The answer changes structure,
length, example coverage and the fidelity threshold. It does not change the rules that
hold in every mode: no verbatim narration of the work, attribute the author's claims to
the author, keep conditions and exceptions, pre-TTS fidelity gate, paid-TTS approval.

## Default study flow (recommended)

**③ 상세 first → read the source with the video's page marks → ② 갈무리 a day or more later.**
③ works as concept pre-training before reading (key terms and their meaning first, then the
relations; Mayer, Mathias & Wetzell 2002; Mayer & Pilegard 2014). Page marks let the viewer
jump to the passage that confused them. ② is retrieval practice, the best-supported part of
the flow (Roediger & Karpicke 2006; Karpicke & Blunt 2011; Adesope et al. 2017). ① is
optional and off by default: overviews of an already well-organised text add little
(Luiten et al. 1980; Mayer 1978), and question-only previews help only the questioned items
(St. Hilaire et al. 2024).

| | ③ 상세 — full understanding | ② 갈무리 — after study | ① 얼개 — optional, before study |
|---|---|---|---|
| Viewer goal | Understand the range; use page marks to read where unclear | Retrieve what was read and connect it | A concept-first map when ③ is not wanted |
| Structure | Range map → source order, every claim, condition, example, self-check → recap with explain-it-yourself questions | Intro (how pauses work) → question → **visible pause** → short answer with pages, repeated → concept map last | 3–5 key concepts (name + one-line meaning) → one labelled relation diagram → 2–4 open questions |
| Examples | All, condensed | Only as cues inside answers | None or one line |
| Answers | Given | Given **after** the pause | **Not** given for the open questions; the source answers them |
| Page marks | Every scene | In every answer | Every concept |
| Length (≈10 source pages) | 6–9 min | 3–4 min including pauses | 2–4 min |
| Fidelity threshold | 100 % of inventory units, in code | 100 % of core units | 100 % of core claims named |

## Rules

- No answer → ③, then offer ② after reading. ① only on request.
- Several modes → one source inventory (units with page ranges) and one fidelity base; then a
  separate plan, narration, TTS cache, captions, QA and master per mode, in separate
  directories so audio caches never collide.
- Build ③'s inventory first even when only ② or ① is requested; shorter modes are checked in
  code against it. A correction found in one mode applies to every mode, on-screen text included.
- ③: end the range-map scene with one bridge sentence into the first section ("그럼 첫 구간,
  ~부터 봅니다") so the jump from map to content is not abrupt. Optional: one short check
  question at section ends of long chapters (Szpunar et al. 2013); it costs a new take.
- ②: put each question in its own scene with a `hold` of about 4 s (6 s for an application
  question) and an on-screen countdown; the pause is silence added in preparation, not a
  paid call. Set `transition_at_pause: true` on question scenes so the semantic before/after
  QA samples straddle the pause (the countdown is the change); make the countdown large
  enough to register (a ring plus an emptying full-width bar worked). Give an application
  question with no fixed answer its own follow-up scene that says so and points to the
  author's example, instead of leaving it unanswered.
  Open a recall video with a short silent text card (how to use it: question, pause,
  answer with page) instead of narrated instructions; viewers rewatch recall videos and
  a narrated preamble becomes the slowest part. Mix recall, connect and apply questions. Show the whole-range diagram at the
  end, not the start. Recommend watching a day or more after reading; the benefit shows at
  delayed tests, not five minutes later. Answers must lie inside the range.
- ①: never reveal the answers to its open questions (feedback right after prequestions lowered
  later scores; Sana et al. 2020); omit or shorten for viewers who already know the field
  (expertise reversal; Kalyuga et al. 2003).
- Evidence comes mostly from students learning science/technical material in laboratory
  studies. The size of any benefit for adults reading practical books is unmeasured; treat
  the design as a hypothesis unless a learning test is run.

## References

Existence and bibliographic data checked against Crossref (ERIC for Mayer 1978) on 2026-11-10;
the cited findings were checked against abstracts or text by separate review agents, not by a
human reader.

- Adesope, Trevisan & Sundararajan (2017). Rethinking the use of tests: A meta-analysis of practice testing. *Review of Educational Research*, 87(3). doi:10.3102/0034654316689306
- Kalyuga, Ayres, Chandler & Sweller (2003). The expertise reversal effect. *Educational Psychologist*, 38(1). doi:10.1207/S15326985EP3801_4
- Karpicke & Blunt (2011). Retrieval practice produces more learning than elaborative studying with concept mapping. *Science*, 331. doi:10.1126/science.1199327
- Luiten, Ames & Ackerson (1980). A meta-analysis of the effects of advance organizers on learning and retention. *AERJ*, 17(2). doi:10.3102/00028312017002211
- Mayer (1978). Can advance organizers counter the effects of text organization? ERIC ED154376.
- Mayer, Mathias & Wetzell (2002). Fostering understanding of multimedia messages through pre-training. *J. Exp. Psych.: Applied*, 8(3). doi:10.1037/1076-898X.8.3.147
- Mayer & Pilegard (2014). Segmenting, pre-training, and modality principles. *Cambridge Handbook of Multimedia Learning* (2nd ed.). doi:10.1017/CBO9781139547369.016
- Roediger & Karpicke (2006). Test-enhanced learning. *Psychological Science*, 17(3). doi:10.1111/j.1467-9280.2006.01693.x
- Sana et al. (2020). Optimizing the efficacy of learning objectives through pretests. *CBE-Life Sciences Education*, 19(3), ar43. doi:10.1187/cbe.19-11-0257
- St. Hilaire, Chan & Ahn (2024). Guessing as a learning intervention: A meta-analytic review of the prequestion effect. *Psychonomic Bulletin & Review*, 31(2). doi:10.3758/s13423-023-02353-8
- Szpunar, Khan & Schacter (2013). Interpolated memory tests reduce mind wandering and improve learning of online lectures. *PNAS*, 110(16). doi:10.1073/pnas.1221764110
