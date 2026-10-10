"""Regression checks for the debugger example. Run after pipeline.py has built build/ko/.

    python example-debugger/test_trace.py
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / 'build' / 'ko'
sys.path[:0] = [str(ROOT.parent / 'example'), str(ROOT)]

import harness  # noqa: E402


class DebuggerTraceInvariants(unittest.TestCase):
    def mutated_build_fails(self, mutate):
        """Copy the built variant, apply one corruption, and expect trace_check.py to refuse it."""
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / 'b'
            shutil.copytree(BUILD, copy, ignore=shutil.ignore_patterns('*.mp4', 'package-check', 'samples', '*.zip'))
            mutate(copy)
            done = subprocess.run([sys.executable, 'trace_check.py'], cwd=copy, capture_output=True, text=True)
            self.assertNotEqual(done.returncode, 0, done.stdout)
            return done.stderr

    def edit_scenes(self, change):
        def mutate(copy):
            path = copy / 'scenes.json'
            data = json.loads(path.read_text())
            change(data)
            path.write_text(json.dumps(data, ensure_ascii=False))
        return mutate

    def test_original_function_runs_and_deletion_does_not_advance(self):
        previous = sys.gettrace()
        trace = harness.record(ROOT / 'build' / 'source')
        self.assertIs(sys.gettrace(), previous)
        self.assertEqual(trace['result'], {'__class__': 'LineRange', 'start_line': 3, 'end_line': 4})
        deleted = [e for e in trace['events'] if e['function'] == '_process_deleted_line']
        self.assertEqual(deleted[0]['values']['tracker']['current_line'], deleted[-1]['values']['tracker']['current_line'])

    def test_rejects_invented_value(self):
        def change(data):
            data['scenes'][3]['highlights'][0]['items'][0][1] = '99'
        self.assertIn('display differs', self.mutated_build_fails(self.edit_scenes(change)))

    def test_rejects_highlight_outside_code_range(self):
        def change(data):
            data['scenes'][1]['code_range'] = [52, 55]
        self.assertIn('outside the code range', self.mutated_build_fails(self.edit_scenes(change)))

    def test_rejects_cue_outside_its_panel(self):
        def change(data):
            data['scenes'][0]['highlights'][-1]['end'] = data['scenes'][0]['duration'] + 1
        self.assertIn('outside its panel', self.mutated_build_fails(self.edit_scenes(change)))

    def test_rejects_edited_source(self):
        def mutate(copy):
            path = copy / 'source-snapshot.py'
            path.write_text(path.read_text().replace('current_line += 1', 'current_line += 2', 1))
        self.assertIn('pinned blob', self.mutated_build_fails(mutate))

    def test_panel_refuses_more_than_eight_rows(self):
        sys.path.insert(0, str(BUILD))
        from PIL import Image
        from tracedraw import code_panel
        rows = (BUILD / 'source-snapshot.py').read_text().splitlines()
        with self.assertRaises(AssertionError):
            code_panel(Image.new('RGB', (1280, 720)), rows, 40, 50, None, 'too tall')


if __name__ == '__main__':
    unittest.main()
