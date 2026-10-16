"""Provider selection tests without making TTS network calls."""
import contextlib
import io
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import variant


def fake_synthesize(cache, build, scene, result):
    wav=cache/f"scene-{scene['id']:02d}.wav"
    wav.parent.mkdir(parents=True,exist_ok=True)
    if wav.exists() and wav.is_dir():
        wav.rmdir()
    wav.write_bytes(b'wav-test')
    wav.with_name(wav.stem+'-metadata.json').write_text('{}')
    if any(part=='edge' for part in cache.parts):
        wav.with_suffix('.mp3').write_bytes(b'mp3-test')
    return result


class ProviderTests(unittest.TestCase):
    def test_edge_default_is_announced_and_uses_edge_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);build=root/'build';(build/'audio').mkdir(parents=True)
            fake=type('Adapter',(),{'synthesize':staticmethod(lambda wav,text,voice:fake_synthesize(wav.parent,build,{'id':1},'synthesized'))})
            out=io.StringIO()
            with patch.dict(os.environ,{},clear=True),patch.dict(sys.modules,{'edge_tts_adapter':fake}):
                with contextlib.redirect_stdout(out):
                    counts=variant.speech(root,build,'ko',[{'id':1,'narration':'문장'}],'Kore','ignored')
            self.assertEqual(counts,{'reused':0,'synthesized':1})
            self.assertIn('defaulting to Edge TTS',out.getvalue())
            self.assertTrue((build/'audio/scene-01.wav').is_file())
            self.assertTrue((build/'audio/scene-01.mp3').is_file())

    def test_explicit_gemini_stays_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);build=root/'build';(build/'audio').mkdir(parents=True)
            def gemini(wav,text,voice,style):
                wav=pathlib.Path(wav);wav.parent.mkdir(parents=True,exist_ok=True)
                if wav.exists() and wav.is_dir():wav.rmdir()
                wav.write_bytes(b'wav-test');wav.with_name(wav.stem+'-metadata.json').write_text('{}')
                return 'reused'
            with patch.dict(os.environ,{'TTS_PROVIDER':'gemini'},clear=True),patch.object(variant.gemini_tts,'synthesize',side_effect=gemini) as call:
                counts=variant.speech(root,build,'ko',[{'id':1,'narration':'문장'}],'Kore','natural')
            call.assert_called_once()
            self.assertEqual(counts,{'reused':1,'synthesized':0})
            self.assertFalse((root/'audio-cache'/'edge').exists())

    def test_invalid_provider_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'TTS_PROVIDER':'other'}):
            with self.assertRaises(ValueError):
                variant.speech(pathlib.Path(tmp),pathlib.Path(tmp)/'build','ko',[],'Kore','style')


if __name__=='__main__':
    unittest.main()
