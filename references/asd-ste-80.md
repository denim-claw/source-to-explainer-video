# ASD-STE-inspired clear text (≈80 % strictness)

Derived from the idea of using the aerospace simplified-technical-English standard to
make model output easier to inspect. This is an **adaptation**, not compliance: the
official standard has two parts (writing rules + a controlled dictionary) and a formal
issue number, and we do not claim to implement them.

Say "ASD-STE100-inspired, 80 %". Never "ASD-STE100 compliant", never "certified".

## Rules

- One claim per sentence. One action per instruction.
- Prefer short sentences and active voice.
- One term for one concept. Do not vary synonyms for style.
- No new facts. If the source does not state it, it does not appear.
- Keep every number, condition, exception and scope qualifier.
- Replace vague hedges with a concrete condition, or drop the claim.
- Mark interpretation separately from source content.
- Keep terminology stable across episodes; keep a term list in the project.

## Why full strictness is not used

The standard's dictionary and sentence rules become unnatural for a narrated
explanation and for Korean. At ~80 % you keep the parts that reduce misreading —
one claim per sentence, one term per concept, explicit conditions — while leaving enough
room for spoken rhythm.

## Worked contrast

Bad (vague, two claims, no condition):
> "필요한 경우 시스템의 상태를 확인한 후 적절한 조치를 수행하십시오."

Clear (one action each, condition explicit):
> "시스템 상태를 확인하십시오. 오류가 있으면 시스템을 중지하십시오."

Applied to an explanation script:
> 나쁨 — "성능 개선이 기대되며 대체로 안정적으로 동작할 것으로 보입니다."
> 좋음 — "p95 지연이 1.8초에서 0.4초로 줄었습니다. 표본은 2,000건이며, 야간 시간대는 측정하지 않았습니다."

The second version is shorter, checkable, and states what it did not measure.

## Separate checks

Clear wording and factual correctness are **different checks**. Passing the style rules
says nothing about whether the content is true. Keep both in the QA report.

## Where the clear text is used

Even when the requested output is a video, produce the clear-text pass first — it is what
keeps narration short, ordered and free of invented facts. It is also the natural tab 1
of an interactive page, and the correct body format for a written summary.
