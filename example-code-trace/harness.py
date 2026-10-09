"""Execute the real fictional module with injected fakes and record safe locals.

Line events describe state BEFORE that line executes. Return events describe the result.
No reimplementation of reserve(), I/O monkeypatch or live service is used.
"""
import json
import pathlib
import sys

from inventory import reserve

ROOT = pathlib.Path(__file__).parent
FIXED_TIME = '2030-01-02T03:04:05Z'


def record():
    calls, events = [], []

    def call(name, args, result=None):
        calls.append({'name': name, 'args': list(args), 'result': result})
        return result

    def tracer(frame, event, arg):
        if frame.f_code is reserve.__code__ and event in ('line', 'return'):
            values = {k: frame.f_locals[k] for k in
                      ('units', 'authenticated', 'stock', 'remaining', 'saved_at')
                      if k in frame.f_locals}
            events.append({'event': event, 'line': frame.f_lineno,
                           'values': values, 'calls': list(calls),
                           'result': arg if event == 'return' else None})
        return tracer

    previous = sys.gettrace()
    try:
        sys.settrace(tracer)
        result = reserve(
            2, authenticate=lambda user: call('authenticate', (user,), True),
            load_stock=lambda item: call('load_stock', (item,), 5),
            save_stock=lambda *args: call('save_stock', args),
            clock=lambda: call('clock', (), FIXED_TIME))
    finally:
        sys.settrace(previous)
    assert result == {'remaining': 3, 'saved_at': FIXED_TIME}
    assert calls[-1]['args'] == ['demo-item', 3, FIXED_TIME]
    return {'scenario': 'fictional success path', 'fixed_time': FIXED_TIME,
            'event_semantics': 'line: before execution; return: completed result',
            'events': events, 'result': result, 'calls': calls}


if __name__ == '__main__':
    print(json.dumps(record(), indent=2))
