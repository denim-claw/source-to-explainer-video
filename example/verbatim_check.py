"""Find long runs shared by narration/on-screen text and a private source transcript.

python example/verbatim_check.py --source private/transcript.txt --plan scenes-draft.json \
    [--min 15] [--allow '짧은 인용구'] [--out qa/verbatim.json]

Normalisation (both sides): Unicode NFKC, then remove whitespace and punctuation/symbols.
A finding is a maximal shared run of at least --min normalised characters that still has
--min characters after the --allow phrases are cut out of it. The report keeps
only the matched run, the scene id, the field and the length: never surrounding source text.
Exit status 1 when any non-allowed run is found.
"""
import argparse
import json
import pathlib
import sys
import unicodedata


def normalise(s):
    s = unicodedata.normalize('NFKC', s)
    return ''.join(ch for ch in s if not (ch.isspace() or unicodedata.category(ch)[0] in 'PS'))


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for x in obj:
            yield from strings(x)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('label', 'text', 'labels', 'label_before', 'label_after', 'items', 'full'):
                yield from strings(v)
            elif isinstance(v, (list, dict)):
                yield from strings(v)


def scene_texts(scene):
    yield 'narration', scene.get('narration', '')
    for c in scene.get('cue_definitions', []):
        yield 'cue', c.get('text', '')
    for o in scene.get('diagram', {}).get('objects', []):
        for s in strings(o):
            yield 'on_screen', s


def shared_runs(text, source, minimum):
    """Maximal runs of text (normalised) that occur in source (normalised)."""
    runs, i, n = [], 0, len(text)
    while i + minimum <= n:
        if text[i:i + minimum] not in source:
            i += 1
            continue
        j = i + minimum
        while j < n and text[i:j + 1] in source:
            j += 1
        runs.append(text[i:j])
        i = j
    return runs


def residual(run, allowed):
    """Longest piece of run left after cutting out every allowed (normalised) phrase."""
    pieces = [run]
    for a in allowed:
        if a:
            pieces = [x for p in pieces for x in p.split(a)]
    return max((len(p) for p in pieces), default=0)


def check(plan, source_text, minimum=15, allow=()):
    src = normalise(source_text)
    allowed = [normalise(a) for a in allow]
    found = []
    for scene in plan:
        for field, raw in scene_texts(scene):
            for run in shared_runs(normalise(raw), src, minimum):
                if residual(run, allowed) < minimum:
                    continue
                found.append(dict(scene=scene.get('id'), field=field, length=len(run), run=run))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=pathlib.Path, required=True)
    ap.add_argument('--plan', type=pathlib.Path, required=True)
    ap.add_argument('--min', type=int, default=15)
    ap.add_argument('--allow', action='append', default=[])
    ap.add_argument('--out', type=pathlib.Path)
    a = ap.parse_args()
    plan = json.loads(a.plan.read_text())
    plan = plan['scenes'] if isinstance(plan, dict) else plan
    found = check(plan, a.source.read_text(encoding='utf-8'), a.min, a.allow)
    report = dict(min_normalised_chars=a.min, normalisation='NFKC; whitespace and P*/S* removed',
                  allowed=a.allow, findings=found, passed=not found,
                  scope='Exact runs only; paraphrase closeness is not measured.')
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text + '\n')
    print(text)
    sys.exit(1 if found else 0)


if __name__ == '__main__':
    main()
