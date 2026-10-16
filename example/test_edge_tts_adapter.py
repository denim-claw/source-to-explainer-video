"""Offline regression tests. Live service smoke is deliberately separate."""
import json
import pathlib
import tempfile
import unittest
import wave
from unittest.mock import patch
import edge_tts_adapter as adapter


class CacheTests(unittest.TestCase):
    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            adapter.synthesize('unused.wav', ' ')

    def test_offline_reuse_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            wav = pathlib.Path(tmp) / 'scene-01.wav'
            mp3 = wav.with_suffix('.mp3')
            meta = wav.with_name('scene-01-metadata.json')
            with wave.open(str(wav), 'wb') as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(48000)
                audio.writeframes(b'\0\0' * 480)
            mp3.write_bytes(b'test cache only; not synthesized audio')
            meta.write_text(json.dumps(dict(provider='edge', model='edge-tts', text='hello',
                voice='ko-KR-SunHiNeural', rate='+0%', pitch='+0Hz',
                sha256=adapter.digest(wav), original_sha256=adapter.digest(mp3))))
            with patch.object(adapter, '_generate', side_effect=AssertionError('network forbidden')):
                self.assertEqual(adapter.synthesize(wav, 'hello'), 'reused')
                for kwargs in ({'text': 'changed'}, {'text': 'hello', 'rate': '+5%'}):
                    with self.assertRaises(ValueError):
                        adapter.synthesize(wav, **kwargs)
                mp3.write_bytes(b'changed')
                with self.assertRaises(ValueError):
                    adapter.synthesize(wav, 'hello')

    def test_partial_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            wav = pathlib.Path(tmp) / 'scene.wav'
            wav.write_bytes(b'partial')
            with self.assertRaises(ValueError):
                adapter.synthesize(wav, 'hello')


if __name__ == '__main__':
    unittest.main()
