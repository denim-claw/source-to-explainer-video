"""Offline tests for verbatim_check."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import verbatim_check as v  # noqa: E402

SOURCE = '고양이는 아주 조용한 밤에 창문 밖을 오래 바라보고 있었다. 그리고 잠이 들었다.'


class VerbatimTest(unittest.TestCase):
    def test_normalise_drops_space_and_punctuation(self):
        self.assertEqual(v.normalise('가 나, 다!  "라"'), '가나다라')

    def test_finds_run_across_spacing_and_punctuation_changes(self):
        plan = [dict(id=1, narration='이야기에서 고양이는, 아주 조용한 밤에 창문 밖을 오래 바라봅니다.')]
        found = v.check(plan, SOURCE, minimum=15)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['scene'], 1)
        self.assertGreaterEqual(found[0]['length'], 15)
        self.assertIn('창문밖을오래바라', found[0]['run'])

    def test_paraphrase_passes(self):
        plan = [dict(id=1, narration='밤이 되자 고양이가 한참 동안 바깥을 내다봤습니다.')]
        self.assertEqual(v.check(plan, SOURCE, minimum=15), [])

    def test_on_screen_labels_are_checked(self):
        plan = [dict(id=2, narration='짧다', diagram=dict(objects=[
            dict(type='box', label=['아주 조용한 밤에 창문 밖을 오래', '다른 말'])]))]
        found = v.check(plan, SOURCE, minimum=12)
        self.assertEqual([f['field'] for f in found], ['on_screen'])

    def test_allow_list(self):
        plan = [dict(id=1, narration='아주 조용한 밤에 창문 밖을 오래 바라보고')]
        self.assertEqual(v.check(plan, SOURCE, 15, allow=['아주 조용한 밤에 창문 밖을 오래 바라보고']), [])


if __name__ == '__main__':
    unittest.main()
