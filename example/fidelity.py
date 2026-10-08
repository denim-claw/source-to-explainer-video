"""Source-fidelity review — a SEPARATE check from the video QA.

Compares the plan against a coded inventory of the source's units and self-checks,
and records what was condensed, which exceptions had to survive, and which checks
were NOT performed. Edit INVENTORY/CHECKS for your own source.
"""
import json
import pathlib

R = pathlib.Path(__file__).parent
S = json.loads((R / 'scenes-draft.json').read_text())

# (id, source location, scenes, what the video says about it)
INVENTORY = [
    ('comprehension_gap', 'source §1', [1], 'reading time is not review time; the output must be checkable'),
    ('one_shape_two_readings', 'source §2', [2], 'the same fact supports a checklist reading or a judgement reading'),
    ('conditions_kept', 'source §2', [2], 'the metaphor is declared as a metaphor, not as the author model'),
    ('verify_what_is_claimable', 'source §3', [3], 'playing file checks are separate from explanatory correctness'),
    ('state_the_gap', 'source §3', [3], 'unrun checks are reported as unrun, not as passes'),
]

# (item, scenes) — the source's own self-check list
CHECKS = [
    ('checker can see the claim and its conditions', [1, 2]),
    ('invented metaphors are labelled', [2]),
    ('encoded file is probed and fully decoded', [3]),
    ('caption timing is described as an estimate', [3]),
    ('unperformed checks are named', [3]),
]

covered_scenes = {s['id'] for s in S}
for _, _, scenes, _ in INVENTORY:
    assert set(scenes) <= covered_scenes, 'inventory points at a missing scene'
for _, scenes in CHECKS:
    assert set(scenes) <= covered_scenes, 'checklist points at a missing scene'
assert all(s.get('exceptions') for s in S), 'every scene must state the exception it preserves'
assert all(s['claim'] and s['visual'] and s['narration'] for s in S)

report = dict(
    reviewer='author: planned from the source, then re-compared the plan against a coded inventory',
    review_scope='Author second pass over the plan; NOT an independent reviewer and NOT a full human listen',
    verdict='All inventoried units and self-check items are mapped to scenes; the exceptions that qualify each claim are present in the plan.',
    source_location='replace with printed/PDF page ranges and the source SHA256',
    inventory=[dict(id=i, source=p, scenes=sc, source_based_explanation=t, status='covered') for i, p, sc, t in INVENTORY],
    inventory_count=len(INVENTORY),
    checklist=[dict(item=item, scenes=sc, status='covered') for item, sc in CHECKS],
    checklist_count=len(CHECKS),
    scene_map=[dict(scene=s['id'], location=s['section'], claim=s['claim'], qualification=s['exceptions'], visual=s['visual']) for s in S],
    condensed_or_omitted=[
        dict(content='long verbatim quotations from the source',
             reason="claims, conditions and named sources are explained in the author's own sentences"),
        dict(content='the full source text and any private scan',
             reason='never packaged or redistributed'),
    ],
    risk_controls=[
        'no invented statistic presented as measured data',
        'declared metaphor is labelled on screen or in the package',
        'no claim that the file playing well proves the explanation is correct',
    ],
    private_source_text_packaged=False,
    independent_review=False,
    full_human_listening=False,
    asr_pronunciation_check=False,
    forced_alignment=False,
)
(R / 'source-fidelity-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
(R / 'source-map.json').write_text(json.dumps(dict(inventory=report['inventory'], checklist=report['checklist'], scene_map=report['scene_map']), ensure_ascii=False, indent=2))
print('fidelity', report['inventory_count'], 'units', report['checklist_count'], 'checks', len(S), 'scenes')
