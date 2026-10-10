"""Scene plan for an architecture review of yc-software/qm at commit daeb2deb.

The source is the public MIT-licensed repository, pinned by commit and Git blob hashes.
Narration explains behaviour and structure; it does not read the code line by line.
Every spoken or displayed string has a Korean and an English version.
"""
T, Y, B, X, FG, M = '#51dccb', '#f3ce62', '#7caff2', '#f08080', '#edf3f5', '#9cabb8'

REPO = 'https://github.com/yc-software/qm'
COMMIT = 'daeb2deb90383597a21b0a36bd15a45488d321af'
FILES = {
    'README.md': '80b54cab83eef6e61d12ed88d25e96579cf54617',
    'docs/SPEC.md': '970fe32ef3ec69e102a0d9f5484b6d30230765dc',
    'docs/session-tape-spec.md': 'cceb7a296475c86644f45d25f30caee887b603a1',
    'src/runs/run-store.ts': '4286db883b52df02b826cb346bf210d9a32c6c60',
    'src/runs/postgres-run-store.ts': '01d675e66093e4217df0b8d8340cd3903d6b2445',
    'src/runs/worker.ts': 'fb331565480b4e15657b40dd74ca8d80c677391e',
    'src/runs/reaper.ts': '363f4bf7d57170534c1d0b6cb68e48bd8b2d48b2',
}
TESTS = {
    'command': 'node --experimental-test-module-mocks --test test/run-store.test.ts test/run-stale.test.ts '
               'test/lease-keepalive.test.ts test/scope-reach.test.ts test/worker-reaper.test.ts '
               'test/tape-fold.test.ts test/session-tape.test.ts test/sandbox-resources.test.ts',
    'commit': COMMIT, 'node': 'v24.20.0', 'platform': 'macOS (darwin 24.6.0, arm64)',
    'result': {'tests': 170, 'pass': 166, 'fail': 4, 'skipped': 0},
    'failures': 'four scope-reach.test.ts cases: "Connector SDK installation failed (rc=64)" in the local exec sandbox on macOS',
    'stores': 'in-memory run and session stores; no Postgres was started',
}


def L(ko, en):
    return {'ko': ko, 'en': en}


def node(i, x, y, label, col=T, r=26, **kw):
    return dict(type='node', id=i, pos=[x, y], label=label, color=col, r=r, **kw)


def box(x, y, label, col=T, w=330, h=56, **kw):
    return dict(type='box', pos=[x, y], label=label, color=col, w=w, h=h, **kw)


def wbox(x, y, label, keyword, col=T, w=200, h=60):
    return dict(type='wbox', pos=[x, y], label=label, keyword=keyword, color=col, w=w, h=h)


def wlink(a, b, keyword, col=T):
    return dict(type='wlink', **{'from': a, 'to': b}, keyword=keyword, color=col)


def label(x, y, text, col=FG, size=22, **kw):
    return dict(type='label', pos=[x, y], text=text, color=col, size=size, **kw)


def flow(a, b, col=T, **kw):
    return dict(type='flow', **{'from': a, 'to': b}, color=col, **kw)


def chips(x, y, items, col=Y, **kw):
    return dict(type='chips', pos=[x, y], items=items, color=col, **kw)


CONFIG = {
    'ko': {'header': 'QM 아키텍처 리뷰 · yc-software/qm @ daeb2deb',
           'footer': 'MIT 라이선스 공개 저장소 기준 독립 해설 · 비공식 · Gemini 음성 · 자막 시점은 추정'},
    'en': {'header': 'ARCHITECTURE REVIEW · yc-software/qm @ daeb2deb',
           'footer': 'Independent explanation of the MIT-licensed public repository · unofficial · Gemini speech · estimated caption timing'},
}
VOICE = 'Kore'
STYLE = {
    'ko': '차분하고 명확한 한국어 기술 리뷰 해설. 코드 이름은 또박또박, 문장 사이는 짧게 쉰다.',
    'en': 'Calm, precise technical reviewer. Pronounce code identifiers clearly, short pauses between sentences.',
}

PLAN = [
    dict(
        title=L('한 장의 지도', 'One map of the system'),
        section=L('README · How it works / SPEC · Agent turns', 'README · How it works / SPEC · Agent turns'),
        source='README.md lines 89-92; docs/SPEC.md line 15',
        claim=L('모든 턴은 하나의 코어와 작업 큐를 거쳐 실행되고, 상태는 Postgres에 남는다.',
                'Every turn passes through one core and a run queue, and state lives in Postgres.'),
        narration=L(
            'YC 소프트웨어 팀이 공개한 QM을 아키텍처 관점에서 리뷰합니다. '
            'QM은 회사 사람들이 슬랙과 웹에서 함께 쓰는 에이전트 실행 환경입니다. '
            '요청은 슬랙이나 웹에서 들어옵니다. 모든 턴은 하나의 코어를 거칩니다. '
            '턴은 실행 한 건이 되어 작업 큐에 들어갑니다. '
            '워커가 실행을 가져가 오케스트레이터를 돌리고, 오케스트레이터는 하네스와 모델을 부릅니다. '
            '대화와 실행 상태는 모두 Postgres에 남습니다.',
            'This video reviews the architecture of QM, the agent harness published by YC Software. '
            'QM is an agent runtime that people in a company share from Slack and the web. '
            'Requests arrive from Slack or the web. Every turn passes through one core. '
            'The turn becomes one run in the run queue. '
            'A worker takes the run and drives the orchestrator, which calls a harness and a model. '
            'Conversations and run state all live in Postgres.'),
        transition=L('모든 턴은', 'Every turn'),
        cues=[(L('QM은 회사', 'QM is an agent'), L('회사가 함께 쓰는 멀티플레이어 에이전트 실행 환경', 'A multiplayer agent runtime shared by a company')),
              (L('워커가 실행을', 'A worker takes'), L('워커 → 오케스트레이터 → 하네스 → 모델', 'Worker → orchestrator → harness → model')),
              (L('대화와 실행', 'Conversations and run'), L('상태는 Postgres에 남는다', 'State lives in Postgres'))],
        objects=[
            wbox(150, 280, L('Slack · 웹', 'Slack · Web'), L('요청은 슬랙이나', 'Requests arrive'), Y),
            wbox(390, 280, L('코어 HTTP API', 'Core HTTP API'), L('모든 턴은', 'Every turn'), T),
            wbox(630, 280, L('작업 큐 runs', 'Run queue'), L('작업 큐에', 'the run queue'), B),
            wbox(870, 280, L('워커', 'Worker'), L('워커가 실행을', 'A worker takes'), T),
            wbox(1110, 280, L('오케스트레이터', 'Orchestrator'), L('워커가 실행을', 'A worker takes'), T),
            wbox(1110, 395, L('하네스 → 모델', 'Harness → model'), L('오케스트레이터는 하네스와', 'which calls a harness'), Y, w=230),
            wbox(520, 470, L('Postgres: 세션 테이프 · 실행 · 상태', 'Postgres: session tape · runs · state'), L('대화와 실행', 'Conversations and run'), B, w=760),
            wlink([250, 280], [290, 280], L('모든 턴은', 'Every turn'), T),
            wlink([490, 280], [530, 280], L('작업 큐에', 'the run queue'), B),
            wlink([730, 280], [770, 280], L('워커가 실행을', 'A worker takes'), T),
            wlink([970, 280], [1010, 280], L('워커가 실행을', 'A worker takes'), T),
            wlink([1110, 310], [1110, 365], L('오케스트레이터는 하네스와', 'which calls a harness'), Y),
            wlink([630, 310], [630, 440], L('대화와 실행', 'Conversations and run'), B),
        ],
        visual=L('요청 경로가 슬랙에서 모델까지 한 칸씩 그려지고, 마지막에 Postgres가 아래에 놓인다.',
                 'The request path draws box by box from Slack to the model, then Postgres settles underneath.'),
        exceptions=L('Slack은 선택 플러그인이며, 웹 UI와 포털은 별도 서비스로 코어 HTTP API를 쓴다.',
                     'Slack is an optional plugin; the web UI and portal are separate services that call the core HTTP API.'),
    ),
    dict(
        title=L('작업 큐와 리스', 'The run queue and the lease'),
        section=L('src/runs/postgres-run-store.ts · claim / worker.ts · heartbeat', 'src/runs/postgres-run-store.ts · claim / worker.ts · heartbeat'),
        source='src/runs/postgres-run-store.ts lines 252-271; src/runs/worker.ts line 34',
        claim=L('워커는 세션마다 하나씩, 오래된 pending 실행부터 잠금 없이 집어 가고 리스로 소유를 표시한다.',
                'Workers claim the oldest pending run per session without blocking each other, and mark ownership with a lease.'),
        narration=L(
            '요청 하나는 runs 테이블의 실행 한 건이 됩니다. 처음 상태는 pending입니다. '
            '워커는 가장 먼저 들어온 pending 실행을 FOR UPDATE SKIP LOCKED로 집어 갑니다. '
            '같은 세션에 이미 도는 실행이나 먼저 들어온 실행이 있으면 건너뜁니다. '
            '집어 간 실행은 running이 되고, 만료 시각이 붙은 리스를 받습니다. '
            '워커는 리스 기간의 3분의 1마다 하트비트를 보내 리스를 늘립니다.',
            'One request becomes one run in the runs table. It starts as pending. '
            'A worker claims the oldest pending run with FOR UPDATE SKIP LOCKED. '
            'It skips a run if the same session already has a running run, or an earlier one waiting. '
            'The claimed run becomes running and receives a lease with an expiry time. '
            'The worker heartbeats every third of the lease period to extend it.'),
        transition=L('집어 간 실행은', 'The claimed run'),
        cues=[(L('처음 상태는', 'It starts as'), L('status = pending', 'status = pending')),
              (L('워커는 가장', 'A worker claims'), L('오래된 것부터, 잠긴 행은 건너뛰며', 'Oldest first, skipping locked rows')),
              (L('같은 세션에', 'It skips a run'), L('세션마다 한 번에 하나씩', 'One run at a time per session')),
              (L('워커는 리스', 'The worker heartbeats'), L('하트비트: 리스 기간의 1/3마다 연장', 'Heartbeat: extend every third of the lease'))],
        objects=[
            chips(360, 290, [['run 4', 'run 3', 'run 2', 'run 1'], ['run 4', 'run 3', 'run 2']], Y),
            label(360, 340, 'status = pending', Y, 21),
            label(360, 470, L('오래된 것부터 · 잠긴 행은 건너뜀 · 세션당 하나', 'oldest first · skip locked rows · one per session'), M, 20),
            node('w', 960, 290, [L('워커: 대기', 'Worker: idle'), L('워커: run 1 실행 중', 'Worker: running run 1')], [M, T], r=30),
            flow([600, 290], 'w', T, show='after'),
            label(960, 420, 'status = running · lease_expires_at = now + ttl', T, 20, show='after'),
        ],
        visual=L('큐의 맨 앞 run 1이 빠지고 워커가 실행 중으로 바뀐다.',
                 'run 1 leaves the head of the queue and the worker switches to running.'),
        exceptions=L('retry_after가 지나지 않은 실행도 건너뛴다. run 번호는 예시다.',
                     'Runs whose retry_after has not passed are also skipped. Run numbers are illustrative.'),
    ),
    dict(
        title=L('끊겨도 이어진다', 'Interrupted, then resumed'),
        section=L('리퍼 · 펜스 토큰 · 재시도', 'Reaper · fence token · retry'),
        source='src/runs/postgres-run-store.ts lines 218-249, 340-345, 527-563',
        claim=L('만료된 리스는 토큰 교체로 펜스를 친 뒤 다시 큐에 넣거나 실패로 마치므로, 늦게 깨어난 워커는 결과를 확정할 수 없다.',
                'Expired leases are fenced by a new token, then requeued or failed, so a late worker cannot commit.'),
        narration=L(
            '워커가 죽으면 하트비트가 멈추고, 리스는 결국 만료됩니다. '
            '리퍼는 만료된 running 실행을 주기적으로 찾습니다. '
            '먼저 리스 토큰을 새 값으로 바꿔 펜스를 칩니다. '
            '그러면 뒤늦게 깨어난 옛 워커는 옛 토큰으로 결과를 확정할 수 없습니다. '
            '완료 처리도 토큰이 맞아야만 되기 때문입니다. '
            '그다음 실행을 다시 pending으로 돌리거나, 재시도 한도를 넘었으면 failed로 마칩니다.',
            'If a worker dies, its heartbeat stops and the lease eventually expires. '
            'The reaper periodically looks for running runs with expired leases. '
            'It first fences the run by replacing its lease token. '
            'A stale worker that wakes up late can no longer commit a result with its old token. '
            'Completing a run also requires the matching token. '
            'Then the reaper returns the run to pending, or marks it failed once the retry budget is spent.'),
        transition=L('리퍼는 만료된', 'The reaper periodically'),
        cues=[(L('워커가 죽으면', 'If a worker dies'), L('하트비트가 멈추면 리스가 만료된다', 'No heartbeat, so the lease expires')),
              (L('먼저 리스 토큰을', 'It first fences'), L('펜스: 리스 토큰을 새 값으로 교체', 'Fence: replace the lease token')),
              (L('완료 처리도', 'Completing a run'), L('complete도 토큰이 맞을 때만 성공', 'complete succeeds only with the matching token')),
              (L('그다음 실행을', 'Then the reaper'), L('다시 pending, 또는 한도를 넘으면 failed', 'Back to pending, or failed past the budget'))],
        objects=[
            box(260, 290, L('작업 큐', 'Run queue'), B, w=220),
            node('wk', 1010, 270, [L('워커 A: 하트비트 중', 'Worker A: heartbeating'), L('워커 A: 응답 없음', 'Worker A: silent')], [T, X], r=28),
            dict(type='node', id='run', pos=[1010, 410, 260, 410], label='run 1', color=Y, r=22),
            label(640, 498, [L('lease token: 워커 A의 토큰', 'lease token: held by worker A'),
                             L('lease token: 리퍼가 새 토큰으로 교체', 'lease token: replaced by the reaper')], [T, Y], 21),
        ],
        visual=L('워커가 응답 없음으로 바뀌고, run 1이 큐로 돌아가며 토큰이 교체된다.',
                 'The worker goes silent, run 1 travels back to the queue, and the token is replaced.'),
        exceptions=L('최대 나이를 넘긴 실행은 재시도 없이 실패로 마친다. 이동 경로는 비유다.',
                     'A run past its maximum age is failed without retry. The motion path is a metaphor.'),
    ),
    dict(
        title=L('세션 테이프', 'The session tape'),
        section=L('docs/session-tape-spec.md · The invariant', 'docs/session-tape-spec.md · The invariant'),
        source='docs/session-tape-spec.md lines 5-60',
        claim=L('모델은 테이프에 있는 것만 읽고, 테이프에는 모델이 읽은 것이 모두 남는다.',
                'The model reads only what the tape contains, and the tape contains everything the model read.'),
        narration=L(
            '대화는 세션 테이프에 쌓입니다. 테이프는 대화마다 덧붙이기만 하는 Postgres 테이블입니다. '
            '기록은 세 종류입니다. 모델이 읽거나 만든 메시지, 압축이나 수정 같은 명시적 편집, 그리고 모델이 보지 않는 부기입니다. '
            '원칙은 하나입니다. 모델은 테이프에 있는 것만 읽고, 테이프에는 모델이 읽은 것이 읽은 순서대로 모두 남습니다. '
            '예외도 밝혀 둡니다. 시스템 프롬프트와 도구 목록은 턴마다 새로 정하고, 듣는 사람에 따라 걸러지는 기록도 있습니다.',
            'Conversations accumulate on the session tape. The tape is an append-only Postgres table for each conversation stream. '
            'Records come in three kinds. Messages the model read or produced, explicit context edits such as compaction or redaction, and annotations the model never sees. '
            'There is one invariant. The model reads only what the tape contains, and the tape contains everything the model read, in the order it read it. '
            'The exceptions are stated too. The system prompt and tool schemas are resolved fresh each turn, and some records are filtered by audience.'),
        transition=L('원칙은 하나', 'There is one invariant'),
        cues=[(L('테이프는 대화마다', 'The tape is'), L('대화마다 덧붙이기만 하는 테이블', 'One append-only table per conversation')),
              (L('기록은 세', 'Records come'), L('message · context_event · annotation', 'message · context_event · annotation')),
              (L('원칙은 하나', 'There is one invariant'), L('모델이 읽은 것 = 테이프에 있는 것', 'What the model read = what the tape holds')),
              (L('예외도', 'The exceptions'), L('예외: 시스템 프롬프트와 도구는 턴마다, 청중별 필터', 'Exceptions: prompt and tools per turn, audience filter'))],
        objects=[
            dict(type='timeline', x=[150, 1130], y=262, count=[3, 12], color=T),
            chips(640, 360, ['message', 'context_event', 'annotation'], T, colors={'context_event': Y, 'annotation': M}),
            box(640, 468, [L('이전: 모델의 기억을 기록에서 다시 추정했다', 'Before: the model view was re-derived'),
                           'context = fold(tape, audience)'], [X, T], w=720),
        ],
        visual=L('테이프에 기록이 하나씩 쌓이고, 아래 상자가 재구성에서 fold로 바뀐다.',
                 'Records append to the tape, and the box below changes from re-derivation to a fold.'),
        exceptions=L('시스템 프롬프트와 도구 스키마는 테이프 밖에 있고, 청중 필터가 맥락을 거른다.',
                     'The system prompt and tool schemas sit outside the tape, and an audience filter applies.'),
    ),
    dict(
        title=L('갈아 끼우는 하네스', 'Swappable harnesses'),
        section=L('docs/SPEC.md · Swappable harnesses and models', 'docs/SPEC.md · Swappable harnesses and models'),
        source='docs/SPEC.md line 17; docs/session-tape-spec.md record kinds',
        claim=L('도구 목록은 하나이고, 턴을 돌리는 하네스와 모델은 바꿀 수 있으며, 바뀐 사실은 테이프에 남는다.',
                'There is one tool catalog; the harness and model are swappable, and a switch is recorded on the tape.'),
        narration=L(
            '에이전트가 쓰는 도구 목록은 하나뿐입니다. '
            '그 턴을 실제로 돌리는 하네스는 Pi, Codex, Claude Code, OpenCode 가운데 고를 수 있습니다. '
            '하네스와 모델, 추론 강도, 속도의 조합을 런타임이라고 부릅니다. '
            '테이프의 메시지 행에는 그것을 쓴 하네스가 찍힙니다. '
            '하네스가 바뀌면 harness_change 이벤트를 남기고, 앞선 기록을 명시적으로 변환합니다. '
            '이 변환에는 손실이 있을 수 있다는 표시입니다.',
            'Agents have a single tool catalog. '
            'The harness that actually runs a turn can be Pi, Codex, Claude Code or OpenCode. '
            'A selection of harness, model, effort level and speed is called the runtime. '
            'Each message row on the tape is stamped with the harness that wrote it. '
            'When the harness changes, QM records a harness_change event and converts the earlier history explicitly. '
            'The event marks that the conversion may be lossy.'),
        transition=L('하네스가 바뀌면', 'When the harness changes'),
        cues=[(L('그 턴을', 'The harness that'), L('하네스: Pi · Codex · Claude Code · OpenCode', 'Harness: Pi · Codex · Claude Code · OpenCode')),
              (L('하네스와 모델', 'A selection of'), L('런타임 = 하네스 + 모델 + 추론 강도 + 속도', 'Runtime = harness + model + effort + speed')),
              (L('하네스가 바뀌면', 'When the harness changes'), L('harness_change: 손실 가능성을 기록한다', 'harness_change records a possibly lossy conversion'))],
        objects=[
            chips(640, 222, ['Pi', 'Codex', 'Claude Code', 'OpenCode'], M),
            node('cat', 220, 330, L('도구 목록 1개', 'One tool catalog'), Y),
            node('h', 640, 330, [L('하네스: Pi', 'Harness: Pi'), L('하네스: Codex', 'Harness: Codex')], [Y, B], r=30),
            node('m', 1060, 330, L('모델 카탈로그', 'Model catalog'), T),
            flow('cat', 'h', Y), flow('h', 'm', T),
            label(640, 470, L('harness_change 이벤트: 손실 가능한 변환을 표시', 'harness_change event: marks a possibly lossy conversion'), Y, 21, show='after'),
        ],
        visual=L('가운데 하네스가 Pi에서 Codex로 바뀌고, 그 사실이 이벤트로 남는다.',
                 'The middle harness switches from Pi to Codex, and the switch is recorded as an event.'),
        exceptions=L('하네스 전환은 무손실을 보장하지 않으며, 이를 명시적 이벤트로 표시한다. Pi→Codex는 예시다.',
                     'A harness switch is not guaranteed lossless; it is marked by an explicit event. Pi→Codex is an example.'),
    ),
    dict(
        title=L('스코프와 샌드박스', 'Scopes and sandboxes'),
        section=L('docs/SPEC.md · Scopes / Sandboxes', 'docs/SPEC.md · Scopes / Sandboxes'),
        source='docs/SPEC.md lines 19-21; README.md lines 91-92',
        claim=L('사람과 채널마다 격리된 스코프가 있고, 격리를 넘으려면 명시적 grant가 필요하며, 샌드박스는 버려도 되는 자원이다.',
                'Each person and channel has an isolated scope; crossing it needs an explicit grant; sandboxes are disposable.'),
        narration=L(
            '사람마다, 채널마다 스코프가 따로 있습니다. '
            '스코프마다 메모리, 파일, 크론, 그리고 자기 샌드박스 컴퓨터를 가집니다. '
            '에이전트의 execute 도구는 그 스코프의 샌드박스에서 명령을 실행합니다. '
            '이 격리를 넘으려면 명시적이고 감사 가능한 grant가 필요합니다. '
            '그리고 어떤 샌드박스도 소중하지 않습니다. 오래 남길 상태는 가능하면 Postgres나 오브젝트 스토리지에 씁니다.',
            'Each person and each channel has its own scope. '
            'Each scope has its own memory, files, crons and sandbox computer. '
            "The agent's execute tool runs commands in that scope's sandbox. "
            'Crossing this isolation requires an explicit, auditable grant. '
            'And no sandbox is precious. Durable state is written to Postgres or object storage wherever possible.'),
        transition=L('이 격리를', 'Crossing this'),
        cues=[(L('스코프마다', 'Each scope has'), L('스코프마다 메모리 · 파일 · 크론 · 샌드박스', 'Per scope: memory · files · crons · sandbox')),
              (L('에이전트의 execute', "The agent's execute"), L('execute는 그 스코프의 샌드박스에서 실행', "execute runs in that scope's sandbox")),
              (L('이 격리를', 'Crossing this'), L('격리를 넘으려면 명시적 grant', 'Crossing isolation needs an explicit grant')),
              (L('그리고 어떤', 'And no sandbox'), L('어떤 샌드박스도 소중하지 않다', 'No sandbox is precious'))],
        objects=[
            box(300, 255, L('개인 스코프 (DM)', 'Personal scope (DM)'), T, w=440),
            box(980, 255, L('채널 스코프 (#room)', 'Channel scope (#room)'), Y, w=440),
            chips(300, 335, [L('메모리', 'memory'), L('파일', 'files'), L('크론', 'crons'), L('샌드박스', 'sandbox')], T, size=19),
            chips(980, 335, [L('메모리', 'memory'), L('파일', 'files'), L('크론', 'crons'), L('샌드박스', 'sandbox')], Y, size=19),
            dict(type='gate', pos=[640, 300], h=[170, 26], color=[X, T]),
            label(640, 412, [L('격리가 기본값', 'Isolation by default'), L('명시적이고 감사되는 grant로만 넘는다', 'Crossed only by an explicit, audited grant')], [X, T], 22),
            box(640, 498, L('Postgres · 오브젝트 스토리지: 오래 남길 상태', 'Postgres · object storage: durable state'), B, w=720),
        ],
        visual=L('두 스코프 사이 벽이 grant로 낮아지고, 오래 남을 상태는 아래 저장소로 간다.',
                 'The wall between two scopes lowers for a grant, and durable state sits in storage below.'),
        exceptions=L('공유 설정이 Open이면 조건부로 개인 자원을 공유 방에서 읽을 수 있다. 벽은 비유다.',
                     'Under the Open sharing posture some personal resources can be read in shared rooms. The wall is a metaphor.'),
    ),
    dict(
        title=L('리뷰어 메모', 'Reviewer notes'),
        section=L('직접 실행한 테스트 · 확인하지 않은 것', 'Tests actually run · what was not verified'),
        source='local test run at the pinned commit (see source-verification.json)',
        claim=L('확인한 것과 확인하지 않은 것을 나눠 적는다.',
                'What was verified is kept apart from what was not.'),
        narration=L(
            '리뷰어로서 확인한 것과 남은 것을 나눕니다. '
            '실행 큐, 리퍼, 세션 테이프, 스코프, 샌드박스에 관한 테스트 파일 여덟 개를 이 커밋에서 직접 돌렸습니다. '
            '170개 중 166개가 통과했습니다. '
            '실패한 4개는 이 맥에서 로컬 샌드박스 설치가 실패한 경우라, 해당 동작은 확인하지 못한 것으로 둡니다. '
            '테스트는 메모리 저장소로 돌았고, Postgres SQL 경로는 코드만 읽었습니다. '
            '수백만 에이전트 규모는 설계 목표일 뿐, 여기서 측정하지 않았습니다.',
            'As a reviewer, I separate what was checked from what remains. '
            'I ran eight test files on runs, the reaper, the session tape, scopes and sandboxes at this commit. '
            '166 of 170 tests passed. '
            'The 4 failures came from a local sandbox install that fails on this Mac, so that behavior stays unverified. '
            'The tests used in-memory stores, and the Postgres SQL paths were only read, not executed. '
            'Scale to millions of agents is a design goal, not something measured here.'),
        transition=L('리뷰어로서', 'As a reviewer'),
        cues=[(L('170개 중', '166 of 170'), L('테스트 166/170 통과 (파일 8개)', '166/170 tests passed (8 files)')),
              (L('실패한 4개는', 'The 4 failures'), L('실패 4개: 로컬 샌드박스 설치 문제, 미확인', '4 failures: local sandbox install, unverified')),
              (L('테스트는 메모리', 'The tests used'), L('메모리 저장소로 실행, SQL은 읽기만', 'In-memory stores; SQL only read')),
              (L('수백만', 'Scale to millions'), L('규모는 설계 목표, 측정하지 않음', 'Scale is a goal, not measured'))],
        objects=[
            dict(type='checks', cols=4, y0=300, dy=120,
                 labels=[L('166/170 통과', '166/170 passed'), L('4개: 환경 실패', '4 env failures'),
                         L('SQL: 읽기만', 'SQL: read only'), L('규모: 미측정', 'Scale: unmeasured')],
                 keywords=[L('170개 중', '166 of 170'), L('실패한 4개는', 'The 4 failures'),
                           L('테스트는 메모리', 'The tests used'), L('수백만', 'Scale to millions')],
                 colors=[T, Y, Y, X]),
            label(640, 420, L('확인한 것 · 확인하지 않은 것', 'Verified · not verified'), M, 22),
            label(640, 470, 'node --test · 8 files · commit daeb2deb', B, 20),
        ],
        visual=L('네 점검 칸이 발화 순서대로 켜지며, 확인과 미확인이 색으로 나뉜다.',
                 'Four check cells light up in spoken order, colour-coded verified versus unverified.'),
        exceptions=L('테스트 통과는 운영 환경의 Postgres, 클라우드 샌드박스, 규모를 증명하지 않는다.',
                     'Passing tests do not prove production Postgres, cloud sandboxes or scale.'),
    ),
]

REVIEW = {
    'reviewer': 'author second pass: every scene re-read against the pinned files',
    'review_scope': 'Not an independent reviewer and not a full human listen; an unofficial explanation',
    'inventory': [
        {'id': 'one_core_run_queue_postgres', 'source': 'README.md 89-92, SPEC.md 15', 'scenes': [1], 'status': 'covered'},
        {'id': 'claim_skip_locked_per_session', 'source': 'postgres-run-store.ts 252-271', 'scenes': [2], 'status': 'covered'},
        {'id': 'heartbeat_third_of_ttl', 'source': 'worker.ts 34', 'scenes': [2], 'status': 'covered'},
        {'id': 'reaper_fence_requeue_or_fail', 'source': 'postgres-run-store.ts 218-249, 527-563', 'scenes': [3], 'status': 'covered'},
        {'id': 'complete_requires_token', 'source': 'postgres-run-store.ts 340-345', 'scenes': [3], 'status': 'covered'},
        {'id': 'tape_invariant_and_exceptions', 'source': 'session-tape-spec.md 17-60', 'scenes': [4], 'status': 'covered'},
        {'id': 'swappable_harness_runtime', 'source': 'SPEC.md 17', 'scenes': [5], 'status': 'covered'},
        {'id': 'scopes_grants_sandboxes', 'source': 'SPEC.md 19-21, README.md 91-92', 'scenes': [6], 'status': 'covered'},
        {'id': 'security_postures', 'source': 'README.md Security and secrets', 'scenes': [],
         'status': 'omitted: Strict/Auto/Dangerous postures and content screening deserve their own episode'},
        {'id': 'credentials_background_work_surfaces', 'source': 'SPEC.md 23-29', 'scenes': [],
         'status': 'omitted for length'},
        {'id': 'tests_actually_run', 'source': 'local run', 'scenes': [7], 'status': 'covered with failures named'},
    ],
    'tests': TESTS,
    'invented_metaphors': ['run numbers', 'the wall between scopes', 'the motion of a run back to the queue', 'Pi→Codex as the example switch'],
}
