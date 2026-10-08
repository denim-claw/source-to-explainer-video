"""Editorial plan → scenes-draft.json.  The ONLY hand-edited file in the project.

Each scene: source location, the single claim, one visual change that explains it,
narration, and the exception that has to survive. Replace this with your own source
plan; the schema is what render.py/prepare.py expect.
"""
import json
import pathlib

R = pathlib.Path(__file__).parent

BG_LABEL = '#edf3f5'
T = '#51dccb'
Y = '#f3ce62'
B = '#7caff2'
X = '#f08080'


def node(i, x, y, label, col=T, r=28):
    return dict(type='node', id=i, pos=[x, y], label=label, color=col, r=r)


def box(x, y, label, col=T, w=330, h=58):
    return dict(type='box', pos=[x, y], label=label, color=col, w=w, h=h)


def label(x, y, text, col=BG_LABEL, size=24):
    return dict(type='label', pos=[x, y], text=text, color=col, size=size)


def flow(a, b, col=T):
    return dict(type='flow', **{'from': a, 'to': b}, color=col)


def wbox(x, y, label, keyword, col=T, w=380, h=64):
    return dict(type='wbox', pos=[x, y], label=label, keyword=keyword, color=col, w=w, h=h)


def wlink(a, b, keyword, col=T):
    return dict(type='wlink', **{'from': a, 'to': b}, keyword=keyword, color=col)


S = []


def scene(title, section, claim, narration, transition, cues, objects, visual, exceptions):
    S.append(dict(
        id=len(S) + 1, title=title, section=section, claim=claim, narration=narration,
        transition_keyword=transition,
        cue_definitions=[dict(keyword=k, text=t) for k, t in cues],
        diagram=dict(objects=objects), visual=visual, exceptions=exceptions,
        metaphor='Coordinates, counts and lengths in this diagram are a metaphor, not measured data.'))


scene(
    '읽었는데 검토를 못 한다', 'Why: comprehension gap',
    '자료를 읽는 시간보다, 나온 결과물을 이해하고 검토하는 시간이 더 중요해졌다.',
    '이 파이프라인은 검증된 하나의 출처를 음성 해설 영상으로 바꿉니다. 요약을 더 길게 쓰는 것이 목적이 아닙니다. '
    '출처의 주장과 조건을 먼저 고정하고, 그 주장이 화면에서 어떻게 바뀌는지로 설명합니다. '
    '그래서 결과물은 읽어야 하는 문서가 아니라, 걸으면서 들을 수 있는 설명이 됩니다.',
    '그래서 결과물은',
    [('이 파이프라인은', '하나의 검증된 출처 → 해설 영상'),
     ('출처의 주장과', '주장과 조건을 먼저 고정')],
    [box(640, 240, ['긴 요약 문서', '이해·검토 가능한 출력'], X, w=620),
     node('src', 210, 380, '검증된 출처', Y),
     node('mid', 640, 380, ['요약만 쌓기', '주장을 화면으로'], [X, T], r=32),
     node('out', 1080, 380, '검토 가능한 결과', T),
     flow('src', 'mid', Y), flow('mid', 'out', T),
     dict(type='gate', pos=[905, 380], h=[150, 24], color=[X, T]),
     label(640, 500, '검증 없이 그럴듯한 요약이 가장 위험하다', X, 24)],
    '요약만 쌓는 상태가 주장을 화면으로 바꾸는 상태로 바뀌고, 막힌 경로가 열린다.',
    '문서를 폐기하라는 뜻이 아니다. 검토 가능성의 기준을 올리자는 뜻이다.')

scene(
    '같은 사실, 다른 해석', 'Core idea: one shape, two interpretations',
    '같은 자료도 정답표로 읽으면 복제되어야 하고, 생각 도구로 읽으면 판단이 필요해진다.',
    '좋은 출처도 정답표로 다루면 사람을 지웁니다. 반대로 생각 도구로 다루면 판단할 여지가 남습니다. '
    '화면에서 같은 도형이 사각형에서 원으로 변하는 이유입니다. 같은 사실, 다른 해석입니다.',
    '화면에서 같은 도형이',
    [('좋은 출처도', '정답표로 다루면 사람을 지운다'),
     ('화면에서 같은 도형이', '같은 사실 · 다른 해석')],
    [dict(type='morph', rect=[340, 290, 940, 470], circle=[640, 380, 105], color=[X, T],
          label_before='정답표: 그대로 복제해야 한다',
          label_after='생각 도구: 판단이 필요하다'),
     label(640, 520, '주장은 그대로, 해석은 내 몫', T, 25)],
    '하나의 도형이 사각형에서 원으로 변하며 해석의 전환을 보여준다. 꼭짓점 대응은 유지된다.',
    '사각형·원은 자체 비유이며 원저자의 공식 모델이 아니다.')

scene(
    '무엇을 검증하고, 무엇을 주장하지 않는가', 'Checklist: what to verify',
    '영상이 재생되는 것과 설명이 맞는 것은 다른 검사다.',
    '마지막 점검입니다. 인코딩된 파일을 실제로 열어 프레임 수와 디코딩을 확인했는가? '
    '자막 타이밍을 정확한 동기화라고 주장하지 않았는가? 듣지 않은 구간을 검수했다고 말하지 않았는가? '
    '이 네 가지를 순서대로 확인합니다.',
    '마지막 점검입니다',
    [('인코딩된 파일을', '프레임 수·전체 디코딩 검사'),
     ('자막 타이밍을', '추정임을 명시'),
     ('듣지 않은 구간을', '미수행으로 표시'),
     ('이 네 가지를', '주장과 검증을 분리')],
    [wbox(400, 250, '프레임 수 · 전체 디코딩', '인코딩된 파일을', T, 420, 62),
     wbox(880, 250, '출처 주장 · 조건 대조', '자막 타이밍을', Y, 420, 62),
     wlink([400, 281], [400, 339], '자막 타이밍을', T),
     wlink([880, 281], [880, 339], '자막 타이밍을', Y),
     wbox(400, 370, '자막은 추정이라고 명시', '듣지 않은 구간을', Y, 420, 62),
     wbox(880, 370, '미수행 검사는 미수행으로', '이 네 가지를', X, 420, 62),
     dict(type='checks', cols=4, y0=486, dy=120,
          labels=['프레임 검사', '출처 대조', '한계 명시', '미수행 구분'],
          keywords=['인코딩된 파일을', '자막 타이밍을', '듣지 않은 구간을', '이 네 가지를'])],
    '네 점검이 발화 순서대로 활성화된다.',
    '자동 검사는 발음 품질이나 독립 내용 검수를 대신하지 않는다.')

(R / 'scenes-draft.json').write_text(json.dumps(S, ensure_ascii=False, indent=2))
print('planned', len(S), 'scenes')
