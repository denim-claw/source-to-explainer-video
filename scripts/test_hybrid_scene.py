import unittest, tempfile, subprocess, json, wave, sys
from pathlib import Path
from hybrid_scene import Event, TimeGroup, Slot, validate_semantics, composite_checked
from PIL import Image, ImageDraw

class HybridTests(unittest.TestCase):
    def test_group_shift_and_bounds(self):
        g=TimeGroup(48000,96000,(Event('read',0,24000),Event('send',24000,60000)))
        moved=g.moved(192000)
        for name,pair in g.absolute().items():
            self.assertEqual(tuple(x+144000 for x in pair),moved.absolute()[name])
        with self.assertRaises(AssertionError):TimeGroup(0,10,(Event('escape',9,11),))
    def test_layout_independent_motion(self):
        a=Slot(40,300,640,400);b=Slot(20,200,320,200)
        self.assertEqual(a.child(.5,.25),(360,400))
        self.assertEqual(b.child(.5,.25),(180,250))
        self.assertEqual(TimeGroup(100,200,(Event('gesture',1,150),)).absolute()['gesture'],(101,250))
    def test_roles(self):
        actors={'w':{'role':'worker'},'l':{'role':'lead'},'a':{'role':'advisor'}}
        self.assertTrue(validate_semantics(actors,{'note':{'owner':'w'}},[{'prop':'note','from':'w','to':'l','meaning':'summary'}]))
        with self.assertRaises(AssertionError):validate_semantics(actors,{'note':{'owner':'a'}},[{'prop':'note','from':'a','to':'l','meaning':'decision'}])
    def test_alpha_paint_order(self):
        b=Image.new('RGBA',(100,100),'#101820');l=Image.new('RGBA',(20,20));ImageDraw.Draw(l).rectangle((4,4,14,14),fill=(240,240,240,180))
        self.assertEqual(composite_checked(b,l,(20,20),Slot(0,0,100,80))['zero_alpha_changes'],0)
        with self.assertRaises(AssertionError):composite_checked(b,l,(20,20),Slot(0,0,100,80),exclusion=[(25,25,60,60)])

    def test_mp3_padding_regression(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);m=r/'padded.mp3'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:sample_rate=24000:duration=0.217','-c:a','libmp3lame',str(m)],check=True)
            sys.path.insert(0,str(Path(__file__).parent));from build_narration_timing import decode_pcm,probe_seconds
            n=len(decode_pcm(str(m),48000))//2;old=probe_seconds(str(m))
            self.assertGreater(abs(old-n/48000),.005,'fixture must reproduce padding mismatch')
            subprocess.run([sys.executable,str(Path(__file__).with_name('build_narration_timing.py')),'--out',d,'--gap','.123456','--tail','.234567',str(m),str(m)],check=True,capture_output=True)
            rows=json.loads((r/'timing.json').read_text());expected=2*n+round(48000*.123456)+round(48000*.234567)
            with wave.open(str(r/'narration.wav')) as w:self.assertEqual(w.getnframes(),expected)
            self.assertEqual(rows[-1]['boundary_sample'],expected)
            self.assertEqual(rows[1]['start_sample'],n+round(48000*.123456))
            self.assertAlmostEqual(sum(x['dur'] for x in rows),expected/48000,places=12)
            print(json.dumps({'regression':'MP3 padding reproduced, sample-clock fixed','ffprobe_audio_seconds':old,'decoded_samples':n,'decoded_seconds':n/48000,'old_two_clip_drift_seconds':2*(old-n/48000),'assembled_samples':expected,'timeline_samples':rows[-1]['boundary_sample']}))

if __name__=='__main__':unittest.main(verbosity=2)
