"""Run selvage's real HunkLineCalculator on the repository's own test input and record it.

The module is imported from an exact snapshot of the pinned commit (implicit namespace
packages, no selvage install). Line events hold the state BEFORE that line executes;
return events hold the returned value. Nothing is reimplemented or patched.
"""
import dataclasses
import enum
import importlib
import json
import pathlib
import sys

# Input and expectation copied verbatim from tests/test_hunk_line_calculator.py
# (test_modification_with_context) at the pinned commit.
CONTENT = """ context line 1
 context line 2
-old line
+new line 1
+new line 2
 context line 3
 context line 4"""
START_LINE_MODIFIED = 1
EXPECTED = (3, 4)
SAFE = ('content', 'start_line_modified', 'lines', 'line', 'line_type', 'prefix',
        'tracker', 'first_change', 'last_change')


def show(value):
    if dataclasses.is_dataclass(value):
        fields = {f.name: show(getattr(value, f.name)) for f in dataclasses.fields(value)}
        return {'__class__': type(value).__name__, **fields}
    if isinstance(value, enum.Enum):
        return f'{type(value).__name__}.{value.name}'
    if isinstance(value, list):
        return f'list[{len(value)}]'
    return value


def record(snapshot_root):
    sys.path.insert(0, str(snapshot_root))
    try:
        module = importlib.import_module('selvage.src.diff_parser.utils.hunk_line_calculator')
    finally:
        sys.path.remove(str(snapshot_root))
    path = pathlib.Path(module.__file__).resolve()
    events = []

    def tracer(frame, event, arg):
        if pathlib.Path(frame.f_code.co_filename).resolve() != path:
            return None
        if event in ('line', 'return'):
            values = {k: show(frame.f_locals[k]) for k in SAFE
                      if k in frame.f_locals and k != 'content'}
            events.append({'event': event, 'function': frame.f_code.co_name, 'line': frame.f_lineno,
                           'values': values, 'result': show(arg) if event == 'return' else None})
        return tracer

    previous = sys.gettrace()
    try:
        sys.settrace(tracer)
        result = module.HunkLineCalculator.calculate_actual_change_lines(CONTENT, START_LINE_MODIFIED)
    finally:
        sys.settrace(previous)
    assert (result.start_line, result.end_line) == EXPECTED, result
    assert sys.gettrace() is previous
    return {'scenario': 'tests/test_hunk_line_calculator.py::test_modification_with_context',
            'input': {'content': CONTENT, 'start_line_modified': START_LINE_MODIFIED},
            'event_semantics': 'line: before execution; return: returned value',
            'result': show(result), 'events': events}


if __name__ == '__main__':
    print(json.dumps(record(sys.argv[1]), ensure_ascii=False, indent=1))
