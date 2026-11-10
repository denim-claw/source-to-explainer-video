"""Offline tests for grok_tts_adapter: no network, no key."""
import json
import os
import pathlib
import struct
import sys
import tempfile
import unittest
import wave
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import grok_tts_adapter as g  # noqa: E402

FMT = struct.pack('<HHIIHH', 1, 1, 48000, 96000, 2, 16)


def streaming_wav(pcm):
    """Mimic the observed xAI response: placeholder RIFF/data sizes."""
    return (b'RIFF' + struct.pack('<I', 0x80000023) + b'WAVE' + b'fmt ' + struct.pack('<I', 16)
            + FMT + b'data' + struct.pack('<I', 0x7fffffff) + pcm)


class GrokAdapterTest(unittest.TestCase):
    def test_repair_keeps_pcm_and_true_length(self):
        pcm = bytes(range(256)) * 375  # 96000 bytes = 1.0 s
        fmt, got = g.split_wav(streaming_wav(pcm))
        self.assertEqual(got, pcm)
        g.check_fmt(fmt)
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'x.wav'
            p.write_bytes(g.build_wav(fmt, pcm))
            with wave.open(str(p)) as w:
                self.assertEqual(w.getnframes(), 48000)
                self.assertEqual(w.readframes(48000), pcm)

    def test_rejects_unexpected_format(self):
        with self.assertRaises(ValueError):
            g.check_fmt(struct.pack('<HHIIHH', 1, 2, 44100, 176400, 4, 16))

    def test_synthesize_then_reuse_without_key(self):
        pcm = b'\x01\x00' * 48000
        resp = (dict(text='t'), streaming_wav(pcm), {'x-trace-id': 'abc', 'content-type': 'audio/wav'}, 0.1)
        with tempfile.TemporaryDirectory() as d:
            out = pathlib.Path(d) / 'scene-01.wav'
            with mock.patch.dict(os.environ, {'XAI_API_KEY': 'test'}), \
                    mock.patch.object(g, '_request', return_value=resp) as req:
                self.assertEqual(g.synthesize(out, '안녕하세요', 'helios'), 'synthesized')
                req.assert_called_once()
            meta = json.loads((pathlib.Path(d) / 'scene-01-metadata.json').read_text())
            self.assertEqual(meta['id'], 'abc')
            self.assertAlmostEqual(meta['seconds'], 1.0)
            self.assertNotIn('test', json.dumps(meta))  # key never recorded
            with mock.patch.dict(os.environ, {}, clear=True), \
                    mock.patch.object(g, '_request', side_effect=AssertionError('network')):
                self.assertEqual(g.synthesize(out, '안녕하세요', 'helios'), 'reused')
                with self.assertRaises(ValueError):
                    g.synthesize(out, '다른 문장', 'helios')
            out.write_bytes(out.read_bytes() + b'\x00\x00')
            with self.assertRaises(ValueError):
                g.synthesize(out, '안녕하세요', 'helios')


if __name__ == '__main__':
    unittest.main()
