"""Run after pipeline.py: regression checks for the trace-specific failure modes."""
import copy
import json
import pathlib
import sys
import unittest

from PIL import Image
import pipeline
from harness import FIXED_TIME, record

sys.path.insert(0, str(pipeline.BUILD))
from panels import values


class TraceInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((pipeline.BUILD / 'scenes.json').read_text())

    def test_original_function_records_before_line_state_and_save_arguments(self):
        previous = sys.gettrace()
        trace = record()
        before_subtract = next(e for e in trace['events'] if e['event'] == 'line' and e['line'] == 11)
        after_subtract = next(e for e in trace['events'] if e['event'] == 'line' and e['line'] == 12)
        self.assertNotIn('remaining', before_subtract['values'])
        self.assertEqual(after_subtract['values']['remaining'], 3)
        self.assertEqual(trace['calls'][-1]['args'], ['demo-item', 3, FIXED_TIME])
        self.assertIs(sys.gettrace(), previous)

    def test_rejects_highlight_outside_own_panel_time(self):
        data = copy.deepcopy(self.data)
        data['scenes'][0]['highlights'][0]['end'] = data['scenes'][0]['duration'] + 0.01
        with self.assertRaises(AssertionError):
            pipeline.check_trace(data)

    def test_rejects_invented_debugger_values(self):
        data = copy.deepcopy(self.data)
        data['scenes'][0]['highlights'][0]['values']['units'] = 99
        with self.assertRaises(AssertionError):
            pipeline.check_trace(data)

    def test_rejects_value_panel_height_overflow(self):
        with self.assertRaises(AssertionError):
            values(Image.new('RGB', (1280, 720)), {'oversized': 'X' * 1000})

    def test_automatic_byte_limit_split_covers_each_frame_once(self):
        # Force the small demo's first group to split; verify real encoded parts.
        try:
            parts = pipeline.split_parts(self.data, max_bytes=230_000, max_scenes=2)
            self.assertEqual(len(parts), 3)
            self.assertEqual(sum(p['frames'] for p in parts), self.data['frames'])
            self.assertTrue(all(p['bytes'] <= 230_000 for p in parts))
            self.assertEqual([s for p in parts for s in p['scenes']], [1, 2, 3])
        finally:
            pipeline.split_parts(self.data, max_bytes=15_000_000, max_scenes=2)


if __name__ == '__main__':
    unittest.main()
