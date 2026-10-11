"""Build the selvage debugger walkthrough in Korean and English.

    python example-debugger/pipeline.py              both languages
    python example-debugger/pipeline.py --lang ko    one language

Fetches the pinned selvage files, checks their Git blobs, confirms the scenario equals
the repository's own test, runs the ORIGINAL function under a tracer, then renders.
Needs GEMINI_API_KEY only for scenes without matching cached speech.
"""
import argparse
import ast
import hashlib
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
SHARED = ROOT.parent / 'example'
sys.path.insert(0, str(SHARED))
sys.path.insert(0, str(ROOT))

import harness  # noqa: E402
import plan  # noqa: E402
import variant  # noqa: E402
from trace_check import items_for  # noqa: E402

RAW = 'https://raw.githubusercontent.com/selvage-lab/selvage/{commit}/{path}'
SOURCE = ROOT / 'build' / 'source'
MONO = SHARED / 'assets' / 'NotoSansMonoCJKkr-Regular.otf'


def git_blob(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def fetch_sources():
    files = []
    for path, blob in plan.FILES.items():
        local = SOURCE / path
        local.parent.mkdir(parents=True, exist_ok=True)
        if not local.exists():
            local.write_bytes(urllib.request.urlopen(RAW.format(commit=plan.COMMIT, path=path), timeout=60).read())
        got = git_blob(local.read_bytes())
        assert got == blob, f'{path}: blob {got} differs from pinned {blob}'
        files.append(dict(path=path, git_blob=blob, sha256=hashlib.sha256(local.read_bytes()).hexdigest()))
    return files


def scenario_from_test():
    """The traced input must be the repository test's own literals, not a retyped copy."""
    tree = ast.parse((SOURCE / 'tests/test_hunk_line_calculator.py').read_text())
    test = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == plan.TEST_NAME)
    literals = {t.id: n.value.value for n in test.body if isinstance(n, ast.Assign)
                for t in n.targets if isinstance(t, ast.Name) and isinstance(n.value, ast.Constant)}
    expected = {c.left.attr: c.comparators[0].value for n in test.body if isinstance(n, ast.Assert)
                for c in [n.test] if isinstance(c, ast.Compare) and isinstance(c.left, ast.Attribute)}
    assert literals['content'] == harness.CONTENT, 'harness input differs from the repository test'
    assert literals['start_line_modified'] == harness.START_LINE_MODIFIED
    assert (expected['start_line'], expected['end_line']) == harness.EXPECTED
    return {'test': f'tests/test_hunk_line_calculator.py::{plan.TEST_NAME}', 'expected': expected}


def highlights(trace):
    events = trace['events']

    def hunk_index(upto):
        for event in reversed(events[:upto + 1]):
            if event['function'] == 'calculate_actual_change_lines' and 'line' in event['values']:
                return trace['input']['content'].splitlines().index(event['values']['line'])
        return None

    def after_prepare(build):
        data = json.loads((build / 'scenes.json').read_text())
        for scene in data['scenes']:
            cues = {c['source_keyword']: c['at'] for c in scene['cues']}
            definitions = scene['highlights']
            out = []
            for definition in definitions:
                event = events[definition['event']]
                out.append({'keyword': definition['keyword'], 'start': cues[definition['keyword']],
                            'event_index': definition['event'], 'event': event['event'],
                            'function': event['function'], 'line': event['line'],
                            'show': definition['show'], 'items': items_for(event, definition['show']),
                            'hunk_index': hunk_index(definition['event'])})
            for i, h in enumerate(out):
                h['end'] = out[i + 1]['start'] if i + 1 < len(out) else scene['duration']
            scene['highlight_definitions'] = definitions
            scene['highlights'] = out
        (build / 'scenes.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return after_prepare


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', choices=['ko', 'en'], action='append')
    args = parser.parse_args()
    if not MONO.is_file():
        raise SystemExit('Fetch the mono font first: bash example/assets/fetch-font.sh mono')
    files = fetch_sources()
    scenario = scenario_from_test()
    trace = harness.record(SOURCE)
    (ROOT / 'build' / 'trace.json').write_text(json.dumps(trace, ensure_ascii=False, indent=1))
    record = dict(repository=plan.REPO, commit=plan.COMMIT, license='Apache-2.0',
                  displayed_source=plan.SOURCE_PATH, files=files, scenario=scenario,
                  tests_run=plan.TESTS, not_traced=plan.REVIEW['not_traced'],
                  fetched_copies='build/source/ (not packaged except the displayed file)')
    extra = {'render.py': ROOT / 'render.py', 'base_render.py': SHARED / 'render.py',
             'tracedraw.py': ROOT / 'tracedraw.py', 'trace_check.py': ROOT / 'trace_check.py',
             'source-snapshot.py': SOURCE / plan.SOURCE_PATH, 'trace.json': ROOT / 'build' / 'trace.json',
             'assets/NotoSansMonoCJKkr-Regular.otf': MONO}
    config = {lang: dict(plan.CONFIG[lang], source_path=plan.SOURCE_PATH) for lang in ('ko', 'en')}
    for lang in args.lang or ['ko', 'en']:
        variant.build_variant(
            ROOT, lang, plan.PLAN, config, record, plan.REVIEW, plan.VOICE, plan.STYLE, gif_scene=4,
            extra_files=extra,
            package_extra=['base_render.py', 'tracedraw.py', 'trace_check.py', 'source-snapshot.py',
                           'trace.json', 'assets/NotoSansMonoCJKkr-Regular.otf', 'qa/debugger-trace.json'],
            after_prepare=highlights(trace),
            before_package=lambda build: print(variant.run(build, sys.executable, 'trace_check.py').strip()))


if __name__ == '__main__':
    main()
