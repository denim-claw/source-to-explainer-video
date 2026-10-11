"""Scene plan for one book section: Eric S. Raymond, "The Cathedral and the Bazaar",
section "Release Early, Release Often" (version 3.0, Open Publication License 2.0).

Every spoken or displayed string carries a Korean and an English version. The narration
is an independent explanation; the two numbered lessons are paraphrased or quoted under
the source's licence. Positions and counts in the diagrams are illustrative.
"""
T, Y, B, X, FG = '#51dccb', '#f3ce62', '#7caff2', '#f08080', '#edf3f5'

SOURCE = {
    'title': 'The Cathedral and the Bazaar',
    'author': 'Eric Steven Raymond',
    'version': '3.0 (revision 1.57, 11 September 2000)',
    'section': 'Release Early, Release Often (fourth section)',
    'url': 'http://www.catb.org/esr/writings/cathedral-bazaar/cathedral-bazaar/ar01s04.html',
    'license': 'Open Publication License, version 2.0: copy, distribute and/or modify permitted',
    'html_sha256': '04ba19feda1ee98286a3aafec8410ba35dbee81d257a8d3ff3d98d261b6a9bec',
    'range': 'the whole section, from "Early and frequent releases" to the stable/cutting-edge numbering paragraph',
    'next_section': 'How Many Eyeballs Tame Complexity',
}


def L(ko, en):
    return {'ko': ko, 'en': en}


def node(i, x, y, label, col=T, r=26, **kw):
    return dict(type='node', id=i, pos=[x, y], label=label, color=col, r=r, **kw)


def box(x, y, label, col=T, w=330, h=56, **kw):
    return dict(type='box', pos=[x, y], label=label, color=col, w=w, h=h, **kw)


def label(x, y, text, col=FG, size=23, **kw):
    return dict(type='label', pos=[x, y], text=text, color=col, size=size, **kw)


def flow(a, b, col=T, **kw):
    return dict(type='flow', **{'from': a, 'to': b}, color=col, **kw)


CONFIG = {
    'ko': {'header': '책 한 절 → 설명 영상 · 성당과 시장',
           'footer': '에릭 S. 레이먼드 『성당과 시장』 v3.0 · Open Publication License 2.0 · 독립 해설 · Gemini 음성 · 자막 시점은 추정'},
    'en': {'header': 'BOOK SECTION → EXPLAINER · THE CATHEDRAL AND THE BAZAAR',
           'footer': 'Eric S. Raymond, The Cathedral and the Bazaar v3.0 · Open Publication License 2.0 · independent explanation · Gemini speech · estimated caption timing'},
}
VOICE = 'Charon'
STYLE = {
    'ko': '차분하고 또렷한 한국어 다큐멘터리 해설. 서두르지 않고 문장 사이를 짧게 쉰다.',
    'en': 'Calm, clear documentary narrator. Unhurried, with short pauses between sentences.',
}

PLAN = [
    dict(
        title=L('성당을 짓듯 배포하던 시절', 'When releases were built like cathedrals'),
        section=L('믿음 · 초기 버전은 버그가 많다', 'Belief · early versions are buggy'),
        source='paragraphs 1-2: the belief behind infrequent releases',
        claim=L('사용자에게 버그를 덜 보이려는 목표가 긴 배포 주기로 이어졌다.',
                'The goal of showing users few bugs led to long release intervals.'),
        narration=L(
            "에릭 레이먼드의 글 「성당과 시장」에서 '일찍 내고, 자주 내라' 절을 살펴봅니다. "
            '예전에는 개발자 대부분이 이렇게 믿었습니다. 초기 버전은 버그가 많기 마련이고, 버그가 많으면 사용자가 지친다. '
            '목표가 사용자에게 버그를 덜 보여 주는 것이라면, 배포는 반년에 한 번 이하로 줄어듭니다. '
            '배포와 배포 사이에는 디버깅에 매달립니다. 레이먼드는 이것을 성당을 짓는 방식이라고 부릅니다.',
            "This video explains one section of Eric Raymond's essay, The Cathedral and the Bazaar. "
            'The section is called Release Early, Release Often. '
            "Most developers once believed that early versions are buggy versions, and that buggy versions wear out users' patience. "
            'If the goal is to show users as few bugs as possible, releases slow to one every six months or less. '
            'Between releases, developers debug hard. Raymond calls this the cathedral-building style.'),
        transition=L('목표가 사용자에게', 'If the goal is'),
        cues=[(L('예전에는', 'Most developers'), L('믿음: 초기 버전은 버그가 많다', 'Belief: early versions are buggy')),
              (L('목표가 사용자에게', 'If the goal is'), L('배포 간격이 반년 이상으로 늘어난다', 'Releases slow to one every six months or less')),
              (L('레이먼드는 이것을', 'Raymond calls this'), L('성당을 짓는 방식', 'The cathedral-building style'))],
        objects=[
            label(640, 212, L('목표: 사용자가 버그를 적게 보게 한다', 'Goal: users see as few bugs as possible'), Y, 24),
            dict(type='timeline', x=[150, 1130], y=330, count=[6, 2], color=[B, X]),
            label(640, 380, [L('배포가 잦다', 'Frequent releases'), L('배포 간격: 6개월 이상', 'Release gap: six months or more')], [B, X], 23),
            box(640, 478, L('성당 짓기: 소수가 오래 다듬어 한 번에 낸다', 'Cathedral: a few people polish for months'), B, w=700),
        ],
        visual=L('배포 눈금 여섯 개가 두 개로 줄며 간격이 벌어진다.', 'Six release ticks thin out to two, widening the gap.'),
        exceptions=L('저자 자신도 이 믿음을 공유했다고 밝힌다. 6개월은 예시 주기다.',
                     'The author says he shared this belief. Six months is the example interval.'),
    ),
    dict(
        title=L('일찍 내라, 자주 내라', 'Release early, release often'),
        section=L('교훈 7 · 리눅스의 배포 강도', 'Lesson 7 · the intensity of Linux releases'),
        source='paragraphs 3-5 and lesson 7',
        claim=L('리누스의 혁신은 빠른 배포 자체가 아니라, 복잡도에 맞춰 끌어올린 강도였다.',
                "Linus's innovation was not quick releases but scaling their intensity to the complexity."),
        narration=L(
            '리누스 토르발스는 정반대로 움직였습니다. 레이먼드는 이것을 일곱 번째 교훈으로 정리합니다. '
            '일찍 내라. 자주 내라. 그리고 고객의 말을 들어라. '
            '빠른 배포와 사용자 피드백 자체는 새롭지 않았습니다. 유닉스 세계의 오랜 전통이었습니다. '
            '새로운 것은 강도였습니다. 1991년 무렵에는 하루에 커널을 한 번 넘게 낸 날도 있었습니다.',
            'Linus Torvalds did the opposite. Raymond turns this into his seventh lesson. '
            'Release early. Release often. And listen to your customers. '
            'Quick releases with user feedback were not new. They had long been a Unix tradition. '
            'What was new was the intensity. Around 1991, Linus sometimes released a new kernel more than once a day.'),
        transition=L('새로운 것은', 'What was new'),
        cues=[(L('일찍 내라', 'Release early'), L('교훈 7: 일찍, 자주, 고객의 말을 듣기', 'Lesson 7: early, often, and listen')),
              (L('빠른 배포와', 'Quick releases'), L('빠른 배포와 피드백은 유닉스의 전통', 'Quick releases were a Unix tradition')),
              (L('새로운 것은', 'What was new'), L('새로운 것: 복잡도에 맞춘 강도', 'New: intensity matched to complexity'))],
        objects=[
            box(640, 228, L('교훈 7 · 일찍 내라. 자주 내라. 고객의 말을 들어라.', 'Lesson 7 · Release early. Release often. Listen to your customers.'), Y, w=900),
            dict(type='timeline', x=[150, 1130], y=330, count=[2, 18], color=[X, T]),
            label(640, 380, [L('유닉스의 전통: 빠른 배포 + 피드백', 'Unix tradition: quick releases + feedback'),
                             L('리눅스: 같은 방법, 훨씬 높은 강도', 'Linux: the same method at far higher intensity')], [B, T], 23),
            label(640, 470, L('1991년 무렵: 하루에 커널을 한 번 넘게 낸 날도 있었다', 'Around 1991: sometimes more than one kernel a day'), T, 22, show='after'),
        ],
        visual=L('배포 눈금이 두 개에서 열여덟 개로 촘촘해진다.', 'Release ticks multiply from two to eighteen.'),
        exceptions=L('빠른 배포와 피드백은 유닉스의 오랜 전통이었다. 눈금 수는 예시다.',
                     'Quick releases with feedback were already a Unix tradition. Tick counts are illustrative.'),
    ),
    dict(
        title=L('무엇을 최대로 끌어올렸나', 'What was Linus maximizing?'),
        section=L('사람의 시간 · 자극과 보상', 'Person-hours · stimulus and reward'),
        source='paragraphs 6-9: what rapid releases maximize, and at what cost',
        claim=L('잦은 배포는 디버깅과 개발에 쓰이는 사람의 시간을 최대로 늘렸고, 대가로 불안정과 소진 위험을 졌다.',
                'Frequent releases maximized person-hours on debugging and development, at the risk of instability and burnout.'),
        narration=L(
            '그렇다면 리누스는 무엇을 최대로 끌어올렸을까요? '
            '사용자는 자기 몫이 생긴다는 기대에 자극받았습니다. '
            '그리고 꾸준히, 때로는 매일 나아지는 결과로 보상받았습니다. '
            '그 결과 디버깅과 개발에 들어가는 사람의 시간이 최대가 됩니다. '
            '대가도 있습니다. 코드가 불안정해질 수 있고, 풀리지 않는 버그가 생기면 사용자가 지칠 수 있습니다.',
            'So what was Linus maximizing? '
            'Users were stimulated by the prospect of a piece of the action. '
            'They were rewarded by constant, sometimes daily, improvement in their work. '
            'As a result, the person-hours spent on debugging and development were maximized. '
            'There was a price. The code could become unstable, and an intractable bug could burn out the user base.'),
        transition=L('그 결과', 'As a result'),
        cues=[(L('사용자는 자기', 'Users were stimulated'), L('자극: 내 몫이 생긴다는 기대', 'Stimulus: a piece of the action')),
              (L('그리고 꾸준히', 'They were rewarded'), L('보상: 꾸준히, 때로는 매일 나아지는 결과', 'Reward: constant, sometimes daily, improvement')),
              (L('그 결과', 'As a result'), L('최대가 되는 것: 디버깅과 개발에 쓰는 사람의 시간', 'Maximized: person-hours on debugging and development')),
              (L('대가도', 'There was a price'), L('대가: 불안정과 사용자 소진의 위험', 'Price: instability and user burnout'))],
        objects=[
            node('u', 220, 300, L('사용자 · 공동 개발자', 'Users · co-developers'), Y),
            node('r', 640, 300, L('잦은 릴리스', 'Frequent releases'), T),
            node('f', 1060, 300, L('눈에 보이는 개선', 'Visible improvement'), B),
            flow('u', 'r', Y), flow('r', 'f', T),
            dict(type='curve', points=[[1060, 268], [900, 214], [380, 214], [220, 268]], color=B, count=5),
            box(640, 470, [L('사람의 시간', 'Person-hours'),
                           L('최대화: 디버깅과 개발에 쓰는 사람의 시간', 'Maximized: person-hours on debugging and development')],
                [Y, T], w=760, h=[56, 64]),
        ],
        visual=L('사용자-릴리스-개선 순환이 돌고, 사람의 시간 상자가 최대화 대상으로 바뀐다.',
                 'The user-release-improvement loop runs, and the person-hours box turns into the maximized quantity.'),
        exceptions=L('불안정과 사용자 소진이라는 대가를 함께 말한다.',
                     'The instability and burnout cost is stated alongside the gain.'),
    ),
    dict(
        title=L('리누스의 법칙', "Linus's Law"),
        section=L('교훈 8 · 보는 눈이 충분하면', 'Lesson 8 · given enough eyeballs'),
        source='lesson 8, "Linus\'s Law", and Linus\'s correction about finding versus fixing',
        claim=L('공동 개발자가 충분히 많으면 버그는 누군가에게 얕아진다. 다만 찾는 사람과 고치는 사람은 다르다.',
                'With enough co-developers a bug becomes shallow to someone; the finder and the fixer differ.'),
        narration=L(
            '여덟 번째 교훈은 이렇습니다. 베타 테스터와 공동 개발자가 충분히 많으면, 거의 모든 문제가 빨리 드러나고 누군가에게는 해법이 뻔히 보인다. '
            '짧게 줄이면, 보는 눈이 충분하면 모든 버그는 얕다. 레이먼드는 이것을 리누스의 법칙이라고 부릅니다. '
            '리누스는 이 표현에서 한 가지를 고쳤습니다. 문제를 찾는 사람과 이해하고 고치는 사람은 대개 다르며, 찾는 일이 더 어렵다는 것입니다.',
            'The eighth lesson reads like this. Given a large enough beta-tester and co-developer base, almost every problem will be characterized quickly, and the fix will be obvious to someone. '
            "Put shortly, given enough eyeballs, all bugs are shallow. Raymond calls this Linus's Law. "
            'Linus corrected one point. The person who finds a problem is usually not the person who understands and fixes it, and finding it is the bigger challenge.'),
        transition=L('짧게 줄이면', 'Put shortly'),
        cues=[(L('여덟 번째', 'The eighth lesson'), L('교훈 8: 공동 개발자가 많으면 문제가 빨리 드러난다', 'Lesson 8: many co-developers characterize problems fast')),
              (L('짧게 줄이면', 'Put shortly'), L('리누스의 법칙: 보는 눈이 충분하면 버그는 얕다', "Linus's Law: enough eyeballs make bugs shallow")),
              (L('리누스는 이', 'Linus corrected'), L('찾는 사람과 고치는 사람은 다르다. 찾는 일이 더 어렵다', 'Finder and fixer differ; finding is harder'))],
        objects=[
            dict(type='line', **{'from': [120, 300], 'to': [1160, 300]}, color='#395466', width=2),
            label(1080, 266, L('표면', 'surface'), '#9cabb8', 18),
            *[node(f'e{k}', 220 + k * 120, 222, '', Y, r=9) for k in range(8)],
            dict(type='node', id='bug', pos=[640, 472, 640, 330], r=20, color=[X, T], label=[L('깊은 버그: 소수가 몇 달을 살핀다', 'Deep bug: a few people search for months'),
                                              L('얕은 버그: 누군가에게는 뻔하다', 'Shallow bug: obvious to someone')]),
            *[flow(f'e{k}', 'bug', Y, count=1, rate=.12, offset=k / 8, show='after') for k in range(8)],
            label(640, 500, L('찾는 사람 ≠ 고치는 사람', 'Finder ≠ fixer'), B, 23, show='after'),
        ],
        visual=L('여러 눈이 연결되자 깊이 있던 버그가 표면으로 올라온다.',
                 'As many eyes connect, the deep bug rises to the surface.'),
        exceptions=L('리누스의 수정: 찾는 사람과 고치는 사람은 대개 다르고, 찾기가 더 어렵다.',
                     "Linus's correction: the finder is usually not the fixer, and finding is harder."),
    ),
    dict(
        title=L('디버깅은 나눌 수 있다', 'Debugging is parallelizable'),
        section=L('조정 비용 · 델파이 효과', 'Coordination cost · the Delphi effect'),
        source='"Debugging is parallelizable" paragraph and the Brooks quotation',
        claim=L('디버거는 조정자 한 명과만 소통하므로, 개발자 추가처럼 조정 비용이 제곱으로 늘지 않는다.',
                'Debuggers talk to one coordinator, so their cost does not grow quadratically like adding developers.'),
        narration=L(
            '리누스의 법칙은 이렇게 바꿔 말할 수도 있습니다. 디버깅은 병렬로 나눌 수 있다. '
            '디버거들은 조정하는 개발자 한 명과 소통하면 되고, 서로 맞출 일은 거의 없습니다. '
            '그래서 개발자를 늘릴 때처럼 조정 비용이 제곱으로 불어나지 않습니다. '
            '사용자마다 프로그램을 시험하는 방식이 다릅니다. 사용자가 많을수록 버그를 더 많이 찾는 이유입니다.',
            "Linus's Law can be rephrased: debugging is parallelizable. "
            'Debuggers need to talk to one coordinating developer, but hardly to each other. '
            'So debugging avoids the quadratic coordination cost that makes adding developers a problem. '
            'Each user stresses the program in a different way. That is why more users find more bugs.'),
        transition=L('디버거들은', 'Debuggers need'),
        cues=[(L('리누스의 법칙은', "Linus's Law can"), L('디버깅은 병렬로 나눌 수 있다', 'Debugging is parallelizable')),
              (L('그래서 개발자를', 'So debugging avoids'), L('조정 비용이 제곱으로 늘지 않는다', 'No quadratic coordination cost')),
              (L('사용자마다', 'Each user'), L('사용자가 많을수록 버그를 더 찾는다 (브룩스)', 'More users find more bugs (Brooks)'))],
        objects=[
            label(640, 206, [L('모두가 서로 맞춘다: 비용이 제곱으로 는다', 'Everyone syncs with everyone: cost grows quadratically'),
                             L('디버거는 조정자 한 명과만 소통한다', 'Each debugger talks to one coordinator')], [X, T], 23),
            dict(type='mesh', center=[640, 390], radius=125, n=8, color=T),
            label(250, 375, L('디버거 8명 (예시)', '8 debuggers (example)'), Y, 22),
            label(1030, 375, [L('연결 28개', '28 links'), L('연결 8개', '8 links')], [X, T], 24),
        ],
        visual=L('여덟 명이 모두 연결된 망이 조정자 하나를 향한 별 모양으로 바뀐다.',
                 'An all-pairs mesh of eight becomes a star around one coordinator.'),
        exceptions=L('중복 작업이 문제가 되지 않는다는 말은 리눅스 세계의 관찰이다. 8명은 예시다.',
                     'That duplicated effort rarely matters is an observation about the Linux world. Eight is illustrative.'),
    ),
    dict(
        title=L('논증과 안전장치', 'The argument and the hedge'),
        section=L('경험적 논증 · 안정판과 최신판', 'Argument from experience · stable and cutting edge'),
        source='"If Linus\'s Law is false" paragraph and the final paragraph on version numbering',
        claim=L('이 법칙은 리눅스의 경험에서 나온 논증이며, 리누스는 버전 번호로 위험을 나눴다.',
                'The law is argued from the Linux experience, and Linus split risk through version numbers.'),
        narration=L(
            '레이먼드의 논증은 이렇습니다. 이 법칙이 틀렸다면, 리눅스 커널처럼 복잡한 시스템은 드러나지 않은 깊은 버그에 눌려 무너졌어야 합니다. '
            '무너지지 않은 것은 이 법칙으로 충분히 설명된다는 것입니다. '
            '이것은 통제된 실험이 아니라 리눅스의 경험에서 나온 논증입니다. '
            '리누스는 안전장치도 두었습니다. 버전 번호로 안정판과 최신판을 나눠, 사용자가 위험을 직접 고르게 했습니다.',
            "Raymond argues like this. If Linus's Law were false, a system as complex as the Linux kernel should have collapsed under undiscovered deep bugs. "
            'That it did not, he says, is explained by the law. '
            'This is an argument from the Linux experience, not a controlled experiment. '
            'Linus also hedged his bets. Kernel version numbers separate stable releases from the cutting edge, so users choose their own risk.'),
        transition=L('리누스는 안전장치도', 'Linus also hedged'),
        cues=[(L('레이먼드의 논증은', 'Raymond argues'), L('논증: 틀렸다면 리눅스는 무너졌어야 한다', 'Argument: if false, Linux should have collapsed')),
              (L('이것은 통제된', 'This is an argument'), L('통제된 실험이 아닌, 경험에서 나온 논증', 'An argument from experience, not an experiment')),
              (L('리누스는 안전장치도', 'Linus also hedged'), L('버전 번호로 안정판과 최신판을 나눈다', 'Version numbers split stable from cutting edge'))],
        objects=[
            box(640, 226, L('법칙이 틀렸다면 → 리눅스는 깊은 버그에 무너졌어야 한다', 'If the law were false → Linux should have collapsed'), Y, w=900),
            label(640, 282, L('통제된 실험이 아닌 경험적 논증', 'An argument from experience, not a controlled experiment'), X, 21),
            node('v', 230, 410, L('새 커널 버전', 'New kernel version'), B),
            node('one', 1000, 410, L('모두가 같은 버전', 'Everyone runs one version'), FG, show='before'),
            flow('v', 'one', B, show='before'),
            node('s', 1000, 350, L('안정판', 'Stable'), T, show='after'),
            node('e', 1000, 465, L('최신판: 새 기능, 더 큰 위험', 'Cutting edge: features, more risk'), Y, show='after'),
            flow('v', 's', T, show='after'), flow('v', 'e', Y, show='after'),
        ],
        visual=L('하나의 배포 경로가 안정판과 최신판 두 갈래로 나뉜다.',
                 'One release path forks into stable and cutting-edge branches.'),
        exceptions=L('저자 스스로 법칙이 맞다면 충분히 설명된다고 말할 뿐, 측정으로 증명하지 않는다.',
                     'The author argues the law is sufficient to explain the result; he does not measure it.'),
    ),
]

REVIEW = {
    'reviewer': 'author second pass: each scene compared with the fetched section text',
    'review_scope': 'Not an independent reviewer and not a full human listen',
    'source': SOURCE,
    'inventory': [
        {'id': 'cathedral_belief', 'source': 'paragraph 1', 'scenes': [1], 'status': 'covered'},
        {'id': 'emacs_lisp_archive_history', 'source': 'paragraphs 2-3', 'scenes': [],
         'status': 'condensed: the Emacs/Ohio archive anecdote is omitted; it motivates but does not change the claim'},
        {'id': 'lesson_7', 'source': 'lesson 7', 'scenes': [2], 'status': 'covered'},
        {'id': 'intensity_not_novelty', 'source': 'paragraph after lesson 7', 'scenes': [2], 'status': 'covered'},
        {'id': 'linus_engineering_genius', 'source': 'paragraph 6', 'scenes': [],
         'status': 'condensed: the comparison with Stallman and Gosling is omitted'},
        {'id': 'maximize_person_hours', 'source': 'paragraphs 7-8', 'scenes': [3], 'status': 'covered with its cost'},
        {'id': 'lesson_8_linus_law', 'source': 'lesson 8', 'scenes': [4], 'status': 'covered'},
        {'id': 'finder_vs_fixer', 'source': 'paragraph after lesson 8', 'scenes': [4], 'status': 'covered'},
        {'id': 'cathedral_vs_bazaar_view_of_bugs', 'source': 'two paragraphs', 'scenes': [1, 4], 'status': 'covered'},
        {'id': 'argument_if_false', 'source': '"And that\'s it" paragraph', 'scenes': [6], 'status': 'covered as an argument'},
        {'id': 'delphi_effect_self_selection', 'source': 'Delphi paragraphs', 'scenes': [5],
         'status': 'condensed into the different-ways-of-stressing point; self-selection omitted'},
        {'id': 'debugging_parallelizable', 'source': 'rephrasing paragraph', 'scenes': [5], 'status': 'covered'},
        {'id': 'brooks_more_users', 'source': 'Brooks quotation', 'scenes': [5], 'status': 'covered'},
        {'id': 'stable_vs_cutting_edge', 'source': 'final paragraph', 'scenes': [6], 'status': 'covered'},
    ],
    'invented_metaphors': ['release tick counts', 'eight debuggers', 'surface/depth of a bug as vertical position'],
}
