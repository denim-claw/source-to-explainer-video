"""Debugger walkthrough of selvage's HunkLineCalculator at a pinned commit.

Each highlight names one recorded trace event by index; the pipeline asserts that the
event's function and line match and copies the displayed values from that event. No
value on screen is typed by hand. Every spoken or displayed string has ko/en versions.
"""
REPO = 'https://github.com/selvage-lab/selvage'
COMMIT = 'e82f34a6f8ea896e5945283ec7815094c802fc21'
SOURCE_PATH = 'selvage/src/diff_parser/utils/hunk_line_calculator.py'
FILES = {
    SOURCE_PATH: '8f5adabb130a77ebb016234d7cd5d14824acbe57',
    'selvage/src/context_extractor/line_range.py': '7c610315c0d6be349a389d09f6577fcb03465d12',
    'tests/test_hunk_line_calculator.py': '5446cba71c727e59adcf0ceeb15f15c51ff8b3d9',
}
TEST_NAME = 'test_modification_with_context'
TESTS = {
    'command': 'python -m pytest tests/test_hunk_line_calculator.py -q',
    'commit': COMMIT, 'python': '3.13 (selvage project venv)', 'platform': 'macOS arm64',
    'result': {'passed': 7, 'failed': 0},
}


def L(ko, en):
    return {'ko': ko, 'en': en}


CONFIG = {
    'ko': {'header': '디버거 추적 · selvage-lab/selvage @ e82f34a',
           'footer': 'Apache-2.0 공개 저장소의 원본 함수를 실행해 기록한 값 · 비공식 해설 · Gemini 음성 · 자막 시점은 추정',
           'trace_labels': {'before': 'WATCH · {function} {line}행 실행 직전',
                            'returned': 'WATCH · {function} 반환 직후',
                            'waiting': 'WATCH · 아직 멈추지 않음', 'empty': '표시할 값 없음', 'hunk': 'HUNK'}},
    'en': {'header': 'DEBUGGER TRACE · selvage-lab/selvage @ e82f34a',
           'footer': 'Values recorded by running the original function from the Apache-2.0 repository · unofficial · Gemini speech · estimated caption timing',
           'trace_labels': {'before': 'WATCH · {function}, before line {line}',
                            'returned': 'WATCH · {function}, just returned',
                            'waiting': 'WATCH · not paused yet', 'empty': 'no values to show', 'hunk': 'HUNK'}},
}
VOICE = 'Puck'
STYLE = {
    'ko': '차분하고 또렷한 한국어 개발 강의 해설. 코드 이름은 또박또박 읽고, 문장 사이를 짧게 쉰다.',
    'en': 'Calm, clear programming instructor. Read code identifiers carefully, with short pauses between sentences.',
}

TRACKER = ['tracker.current_line', 'tracker.first_change_line', 'tracker.last_change_line']


def H(keyword, event, show):
    return {'keyword': keyword, 'event': event, 'show': show}


PLAN = [
    dict(
        title=L('바뀐 줄의 범위를 찾는 함수', 'The function that finds changed lines'),
        section=L('calculate_actual_change_lines · 44–50행', 'calculate_actual_change_lines · lines 44–50'),
        function='calculate_actual_change_lines', code_range=[44, 50],
        source='hunk_line_calculator.py lines 44-50; caller hunk.py from_hunk_text; prompt_generator.py smart context',
        claim=L('입력 hunk를 줄로 나누고, 시작 줄에서 출발하는 추적기를 만든다.',
                'The hunk is split into lines and a tracker starts at the first modified line.'),
        narration=L(
            'selvage는 스마트 컨텍스트를 쓸 때, 바뀐 줄이 속한 코드 블록만 골라 모델에 보냅니다. '
            '그러려면 hunk 안에서 실제로 바뀐 줄의 범위부터 알아야 합니다. 그 계산을 맡은 함수를 디버거로 따라가 봅니다. '
            '입력은 저장소 테스트에 있는 hunk 하나이고, 수정된 파일의 시작 줄은 1입니다. '
            '먼저 내용을 줄 단위로 나눕니다. 모두 일곱 줄입니다. '
            '다음으로 current_line이 1인 추적기를 만듭니다. 이제 줄을 하나씩 꺼냅니다.',
            'When selvage uses smart context, it sends the model only the code blocks that contain changed lines. '
            'For that it first needs the range of lines a hunk actually changed. Let us follow the function that computes it, in a debugger. '
            'The input is one hunk from the repository test, and the modified file starts at line 1. '
            'First, the content is split into lines. There are seven. '
            'Next, a tracker is created with current_line set to 1. Now the lines are taken one by one.'),
        transition=L('먼저 내용을', 'First, the content'),
        highlights=[H(L('입력은 저장소', 'The input is'), 0, ['start_line_modified']),
                    H(L('먼저 내용을', 'First, the content'), 1, ['start_line_modified', 'lines']),
                    H(L('다음으로', 'Next, a tracker'), 2, TRACKER),
                    H(L('이제 줄을', 'Now the lines'), 3, ['line', 'tracker.current_line'])],
        visual=L('입력 줄 수와 추적기의 초깃값이 값 막대에 나타난다.', 'The line count and the tracker defaults appear in the watch bar.'),
        exceptions=L('스마트 컨텍스트를 쓰지 않는 파일은 전체 내용을 보낼 수 있다.',
                     'Files that do not use smart context may be sent in full.'),
    ),
    dict(
        title=L('문맥 줄은 번호만 넘긴다', 'Context lines only advance the counter'),
        section=L('calculate_actual_change_lines · 52–59행', 'calculate_actual_change_lines · lines 52–59'),
        function='calculate_actual_change_lines', code_range=[52, 59],
        source='hunk_line_calculator.py lines 52-59 and 93-95',
        claim=L('문맥 줄은 수정된 파일에도 있으므로 current_line만 하나 올린다.',
                'A context line exists in the modified file, so only current_line advances.'),
        narration=L(
            '첫 줄은 공백으로 시작합니다. 문맥 줄입니다. '
            '분기는 ADDED와 DELETED를 지나 CONTEXT에 닿습니다. '
            '문맥 줄은 수정된 파일에도 있는 줄이라, current_line만 하나 올립니다. '
            '두 번째 문맥 줄도 똑같이 처리합니다. '
            '그래서 세 번째 줄을 볼 때 current_line은 3입니다.',
            'The first line starts with a space, so it is a context line. '
            'The branch passes ADDED and DELETED and reaches CONTEXT. '
            'A context line also exists in the modified file, so only current_line moves up by one. '
            'The second context line is handled the same way. '
            'So when the third line arrives, current_line is 3.'),
        transition=L('분기는', 'The branch passes'),
        highlights=[H(L('첫 줄은', 'The first line'), 15, ['line', 'line_type', 'tracker.current_line']),
                    H(L('분기는', 'The branch passes'), 17, ['line', 'line_type', 'tracker.current_line']),
                    H(L('문맥 줄은 수정된', 'A context line also'), 18, ['line', 'line_type', 'tracker.current_line']),
                    H(L('두 번째 문맥', 'The second context'), 37, ['line', 'line_type', 'tracker.current_line']),
                    H(L('그래서 세 번째', 'So when the third'), 51, ['line', 'line_type', 'tracker.current_line'])],
        visual=L('강조가 분기를 따라 내려가고, current_line이 1에서 3으로 바뀐다.',
                 'The highlight walks down the branch while current_line goes from 1 to 3.'),
        exceptions=L('줄 52의 값은 실행 직전 상태다. 증가는 _process_context_line 안에서 일어난다.',
                     'Values at line 52 are before execution; the increment happens inside _process_context_line.'),
    ),
    dict(
        title=L('줄의 종류를 가린다', 'Classifying a diff line'),
        section=L('_parse_diff_line · 64–71행', '_parse_diff_line · lines 64–71'),
        function='_parse_diff_line', code_range=[64, 71],
        source='hunk_line_calculator.py lines 62-71',
        claim=L('첫 글자를 LineType 값과 차례로 비교해, 맞는 타입을 돌려준다.',
                'The first character is compared with each LineType value, and the match is returned.'),
        narration=L(
            "세 번째 줄은 빼기 기호로 시작하는 'old line'입니다. "
            '빈 줄이면 곧바로 None을 돌려줍니다. '
            '그렇지 않으면 첫 글자를 prefix로 꺼냅니다. '
            '그다음 LineType을 순서대로 돌며 비교합니다. '
            'ADDED의 더하기 기호와는 맞지 않습니다. '
            '두 번째인 DELETED의 빼기 기호와 맞습니다. '
            '일치하면 그 타입을 돌려줍니다. 어느 기호와도 맞지 않는 줄은 None이 되어 반복문에서 건너뜁니다.',
            "The third line, 'old line', starts with a minus sign. "
            'An empty line would return None right away. '
            'Otherwise the first character is taken as prefix. '
            'Then the loop compares it with each LineType in order. '
            "ADDED's plus sign does not match. "
            "The second one, DELETED's minus sign, does. "
            'On a match the type is returned. A line that matches no sign becomes None, and the loop skips it.'),
        transition=L('그렇지 않으면', 'Otherwise the first'),
        highlights=[H(L('빈 줄이면', 'An empty line'), 42, ['line']),
                    H(L('그렇지 않으면', 'Otherwise the first'), 43, ['line']),
                    H(L('그다음 LineType을', 'Then the loop'), 44, ['line', 'prefix']),
                    H(L('ADDED의', "ADDED's plus"), 45, ['prefix', 'line_type']),
                    H(L('두 번째인', 'The second one'), 47, ['prefix', 'line_type']),
                    H(L('일치하면', 'On a match'), 49, ['return'])],
        visual=L('prefix가 빼기 기호로 채워지고, line_type이 ADDED에서 DELETED로 넘어간다.',
                 'prefix fills with a minus sign and line_type moves from ADDED to DELETED.'),
        exceptions=L('일치하지 않는 줄이 None이 된다는 마지막 문장은 코드를 읽은 내용이며, 이 실행에는 그런 줄이 없다.',
                     'The final sentence about unmatched lines is read from the code; this run has no such line.'),
    ),
    dict(
        title=L('삭제 줄은 번호를 올리지 않는다', 'A deleted line does not advance'),
        section=L('_process_deleted_line · 84–90행', '_process_deleted_line · lines 84–90'),
        function='_process_deleted_line', code_range=[84, 90],
        source='hunk_line_calculator.py lines 82-90',
        claim=L('삭제는 범위에 기록되지만, 수정된 파일에 없으므로 current_line은 그대로다.',
                'A deletion is recorded in the range, but current_line stays because the line is gone.'),
        narration=L(
            'DELETED는 _process_deleted_line으로 갑니다. '
            '아직 기록된 변경이 없으므로, first_change_line은 지금 줄인 3이 됩니다. '
            'last_change_line도 비어 있으니 3이 됩니다. '
            '그리고 current_line은 3에 그대로 머뭅니다. 지운 줄은 수정된 파일에 없기 때문입니다. '
            '삭제는 다음 줄이 들어올 자리인 3번 줄에 표시됩니다.',
            'DELETED goes to _process_deleted_line. '
            'No change has been recorded yet, so first_change_line becomes the current line, 3. '
            'last_change_line is also empty, so it becomes 3 as well. '
            'And current_line stays at 3, because a deleted line does not exist in the modified file. '
            'The deletion is marked at line 3, where the next line will land.'),
        transition=L('아직 기록된', 'No change has'),
        highlights=[H(L('DELETED는', 'DELETED goes'), 54, TRACKER),
                    H(L('아직 기록된', 'No change has'), 55, TRACKER),
                    H(L('last_change_line도', 'last_change_line is also'), 57, TRACKER),
                    H(L('그리고 current_line은', 'And current_line stays'), 58, TRACKER)],
        visual=L('first_change_line과 last_change_line이 3으로 채워지고 current_line은 바뀌지 않는다.',
                 'first_change_line and last_change_line fill with 3 while current_line does not move.'),
        exceptions=L('86–89행 조건은 이미 기록된 마지막 변경보다 뒤일 때만 last_change_line을 바꾼다.',
                     'The condition on lines 86-89 only moves last_change_line forward.'),
    ),
    dict(
        title=L('추가 줄은 범위를 넓힌다', 'Added lines extend the range'),
        section=L('_process_added_line · 74–79행', '_process_added_line · lines 74–79'),
        function='_process_added_line', code_range=[74, 79],
        source='hunk_line_calculator.py lines 73-79',
        claim=L('추가 줄은 마지막 변경 줄을 옮기고, 수정된 파일에 있으므로 current_line도 올린다.',
                'An added line moves the last change and, being in the modified file, advances current_line.'),
        narration=L(
            '다음 두 줄은 더하기로 시작하는 추가 줄입니다. '
            'first_change_line은 이미 3이라 그대로 둡니다. '
            'last_change_line은 지금 줄인 3으로 맞춥니다. '
            '추가된 줄은 수정된 파일에 실제로 있으니, current_line을 4로 올립니다. '
            '두 번째 추가 줄에서는 last_change_line이 4가 되고, current_line은 5로 올라갑니다.',
            'The next two lines start with a plus sign; they are added lines. '
            'first_change_line is already 3, so it stays. '
            'last_change_line is set to the current line, 3. '
            'An added line really exists in the modified file, so current_line moves up to 4. '
            'On the second added line, last_change_line becomes 4 and current_line moves up to 5.'),
        transition=L('last_change_line은 지금', 'last_change_line is set'),
        highlights=[H(L('first_change_line은 이미', 'first_change_line is already'), 70, TRACKER),
                    H(L('last_change_line은 지금', 'last_change_line is set'), 71, TRACKER),
                    H(L('추가된 줄은', 'An added line'), 73, TRACKER),
                    H(L('두 번째 추가', 'On the second added'), 88, TRACKER)],
        visual=L('last_change_line이 3에서 4로, current_line이 3에서 5로 바뀐다.',
                 'last_change_line goes from 3 to 4 and current_line from 3 to 5.'),
        exceptions=L('반환 직후 값은 함수 안의 증가가 반영된 상태다.',
                     'Values shown just after return include the increment made inside the function.'),
    ),
    dict(
        title=L('범위를 확정한다', 'Finalizing the range'),
        section=L('_finalize_change_range · 102–108행', '_finalize_change_range · lines 102–108'),
        function='_finalize_change_range', code_range=[102, 108],
        source='hunk_line_calculator.py lines 97-108; tests/test_hunk_line_calculator.py test_modification_with_context',
        claim=L('기록된 첫 변경과 마지막 변경으로 3–4행 범위를 돌려주며, 이는 저장소 테스트의 기대값과 같다.',
                'The recorded first and last changes give lines 3-4, matching the repository test.'),
        narration=L(
            '남은 문맥 줄 두 개는 current_line만 7까지 올립니다. '
            '반복이 끝나면 범위를 확정합니다. '
            '기록된 첫 변경 3과 마지막 변경 4를 꺼냅니다. 기록이 없었다면 시작 줄로, 1보다 작다면 1로 대신합니다. '
            '결과는 3번부터 4번 줄입니다. 저장소 테스트가 기대한 값과 같습니다. '
            'selvage는 이 범위를 감싼 코드 블록을 리뷰 맥락으로 고릅니다.',
            'The two remaining context lines only move current_line up to 7. '
            'When the loop ends, the range is finalized. '
            'The recorded first change, 3, and last change, 4, are read. Without a record it would fall back to the start line, and anything below 1 becomes 1. '
            'The result is lines 3 to 4. That matches what the repository test expects. '
            'selvage then picks the code blocks around this range as review context.'),
        transition=L('기록된 첫', 'The recorded first'),
        highlights=[H(L('반복이 끝나면', 'When the loop ends'), 129, ['start_line_modified'] + TRACKER),
                    H(L('기록된 첫', 'The recorded first'), 131, ['first_change', 'last_change']),
                    H(L('결과는', 'The result is'), 135, ['return'])],
        visual=L('first_change와 last_change가 채워지고 LineRange(3, 4)가 반환된다.',
                 'first_change and last_change fill in and LineRange(3, 4) is returned.'),
        exceptions=L('기록이 없거나 1보다 작을 때의 대체 규칙은 코드를 읽은 내용이며, 이 실행에서는 쓰이지 않았다.',
                     'The fallbacks for no record or values below 1 are read from the code; this run does not use them.'),
    ),
]

for row in PLAN:
    # The shared prepare step anchors cues on these keywords; the pipeline turns them into highlights.
    row['cues'] = [(h['keyword'], L('', '')) for h in row['highlights']]
    row['objects'] = [dict(type='label', pos=[640, 300], text='', color='#edf3f5', size=20)]

REVIEW = {
    'reviewer': 'author second pass: every highlight re-checked against the recorded event and the pinned source',
    'review_scope': 'Not an independent reviewer and not a full human listen; an unofficial explanation',
    'inventory': [
        {'id': 'split_and_tracker', 'source': 'lines 44-47', 'scenes': [1], 'status': 'traced'},
        {'id': 'dispatch_context', 'source': 'lines 52-57, 93-95', 'scenes': [2], 'status': 'traced'},
        {'id': 'parse_prefix', 'source': 'lines 62-71', 'scenes': [3], 'status': 'traced; the None path is read only'},
        {'id': 'deleted_line', 'source': 'lines 82-90', 'scenes': [4], 'status': 'traced'},
        {'id': 'added_line', 'source': 'lines 73-79', 'scenes': [5], 'status': 'traced'},
        {'id': 'finalize', 'source': 'lines 97-108', 'scenes': [6], 'status': 'traced; fallbacks read only'},
        {'id': 'why_it_matters', 'source': 'hunk.py from_hunk_text, prompt_generator.py', 'scenes': [1, 6],
         'status': 'read: change_line feeds ContextExtractor.extract_contexts when smart context is used'},
    ],
    'tests': TESTS,
    'not_traced': ['unmatched prefixes such as "\\ No newline at end of file"', 'hunks without any change',
                   'start_line_modified of 0 (deleted files)'],
}
