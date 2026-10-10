# 오픈소스 함수 → 디버거 추적 영상

[English](README.md) | 한국어

[selvage](https://github.com/selvage-lab/selvage)의 `HunkLineCalculator.calculate_actual_change_lines`를
디버거처럼 따라가는 여섯 장면짜리 영상입니다. 함수를 다시 짜서 흉내 내지 않습니다.
고정한 커밋의 원본 파일을 그대로 실행하고, 줄마다 기록한 값만 화면에 띄웁니다.

![삭제 줄을 처리하는 동안 current_line은 그대로이고 first·last_change_line이 3으로 채워지는 장면](preview/ko.gif)

| | 한국어 | 영어 |
|---|---|---|
| 영상 | [ko.mp4](preview/ko.mp4) · 2분 51초 · 4.2MB | [en.mp4](preview/en.mp4) · 2분 45초 · 4.2MB |
| 자막 | [ko.srt](preview/ko.srt) · 40개 | [en.srt](preview/en.srt) · 38개 |
| 대표 화면 | [ko.png](preview/ko.png) | [en.png](preview/en.png) |

selvage는 Apache-2.0 라이선스의 공개 저장소입니다. 이 영상은 비공식 해설입니다.

## 왜 이 함수인가

selvage는 스마트 컨텍스트를 쓸 때 바뀐 줄이 속한 코드 블록만 골라 모델에 보냅니다.
그 출발점이 hunk 안에서 실제로 바뀐 줄의 범위이고, 이 함수가 그 범위를 계산합니다.
외부 의존성이 없는 순수 함수라 가짜 객체 없이 원본을 그대로 실행할 수 있습니다.
삭제 줄은 수정된 파일에 없으므로 줄 번호를 올리지 않는다는 점이 이 함수의 핵심이고,
값이 변하는 모습으로 보여 주기에 알맞습니다.

## 원본과 시나리오 고정

- 저장소 `selvage-lab/selvage`, 커밋 `e82f34a`
- 화면에 보이는 파일: `selvage/src/diff_parser/utils/hunk_line_calculator.py` (blob `8f5adab`)
- 함께 불러오는 파일: `selvage/src/context_extractor/line_range.py` (blob `7c61031`)
- 시나리오: `tests/test_hunk_line_calculator.py`의 `test_modification_with_context` (blob `5446cba`)

`pipeline.py`는 이 세 파일을 해당 커밋에서 받아 blob 해시를 다시 계산합니다. 테스트 파일을 구문
분석해 하네스의 입력과 기대값이 테스트의 값과 글자 하나까지 같은지도 확인합니다.
그다음 selvage를 설치하지 않고 받은 파일만으로 모듈을 불러와 `sys.settrace`로 실행을 기록합니다.

## 장면 구성

| 장면 | 코드 | 보여 주는 것 |
|---|---|---|
| 1 | 44–50행 | 입력을 일곱 줄로 나누고 `current_line=1`인 추적기를 만든다 |
| 2 | 52–59행 | 문맥 줄 두 개를 지나며 `current_line`이 1에서 3이 된다 |
| 3 | 64–71행 | `'-old line'`의 첫 글자가 ADDED와 맞지 않고 DELETED와 맞는다 |
| 4 | 84–90행 | 삭제 줄: 첫·마지막 변경은 3이 되고 `current_line`은 그대로다 |
| 5 | 74–79행 | 추가 줄 두 개: 마지막 변경이 4로, `current_line`이 5로 간다 |
| 6 | 102–108행 | `LineRange(start_line=3, end_line=4)`를 돌려준다 |

화면 아래 WATCH 막대는 강조한 줄을 **실행하기 직전**의 값입니다. 함수가 값을 돌려준 직후라면
그렇게 표시합니다. HUNK 줄은 반복문이 지금 처리하는 diff 줄을 가리킵니다.

## 만드는 방법

```bash
bash example/assets/fetch-font.sh             # 본문 글꼴
bash example/assets/fetch-font.sh mono        # 코드용 고정폭 글꼴
export GEMINI_API_KEY=...                     # 음성이 없는 장면에만 쓴다
export WHISPER_MODEL=/path/to/ggml-small.bin  # 선택: 음성 인식 비교
.venv/bin/python example-debugger/pipeline.py
.venv/bin/python example-debugger/test_trace.py
```

| 파일 | 하는 일 |
|---|---|
| `plan.py` | 고정한 커밋과 blob, 장면과 나레이션(한국어·영어), 강조마다 쓸 이벤트 번호 |
| `harness.py` | 원본 함수를 테스트 입력으로 실행하며 줄 이벤트와 지역 변수를 기록 |
| `pipeline.py` | 원본 확인 → 시나리오 대조 → 추적 기록 → 언어마다 공통 파이프라인 실행 |
| `tracedraw.py` | 화면 폭 전체의 코드 패널과 WATCH 막대, HUNK 표시 |
| `render.py` | 공통 렌더러 위에 디버거 화면을 얹는 어댑터 |
| `trace_check.py` | 화면의 코드와 값이 고정한 원본·기록과 같은지 검사 |
| `test_trace.py` | 지어낸 값, 범위 밖 강조, 바뀐 원본을 정말 거부하는지 확인하는 회귀 테스트 |

## 검사한 것

| 항목 | 결과 |
|---|---|
| 원본 대조 | 화면의 코드 줄이 고정한 blob과 같음 |
| 값 대조 | 강조 26개 모두 기록된 이벤트의 값과 같음. 손으로 입력한 값 없음 |
| 시간 범위 | 모든 강조가 자기 장면, 자기 코드 범위 안에 있음 |
| 배치 | 5프레임마다 한 장과 강조 경계 앞뒤 프레임에서 글자가 패널을 넘지 않음 |
| 영상 형식 | 1280×720, 30fps, H.264 + AAC. 프레임 수 5,143(한국어) · 4,950(영어) 일치, 전체 디코딩 오류 없음 |
| 패키지 재실행 | 압축(63개 파일)을 새 폴더에 풀어 2초 영상을 렌더링하고 RGB 해시 비교 |
| 저장소 테스트 | 같은 커밋에서 `tests/test_hunk_line_calculator.py` 7개 통과 |
| 음성 인식 비교 | whisper.cpp small로 장면별 받아쓰기. 일치도 한국어 0.754~0.891, 영어 0.970~1.0 |

한국어판 점수가 낮은 이유는 `current_line`, `DELETED` 같은 코드 이름을 음성 인식이 "커런트 라인",
"딜리티드"처럼 한글로 받아 적기 때문입니다. 문장이 빠진 곳은 없었습니다. 그래도 사람이 들어
확인할 대상으로 남겨 둡니다.

음성은 Gemini `gemini-3.8-flash-lite-tts`의 `Puck` 목소리로 만들었습니다.

## 하지 않은 검사

- 테스트 시나리오 하나만 실행했습니다. 기호가 맞지 않는 줄(`\ No newline at end of file`),
  변경이 없는 hunk, 시작 줄이 0인 삭제 파일은 코드를 읽었을 뿐 실행하지 않았습니다.
- 사람이 영상 전체를 이어서 들어 보지 않았습니다. 자막 시점은 추정값입니다.
- selvage 관리자나 다른 검토자의 독립 검토는 없었습니다.
