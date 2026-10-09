# 가상 코드 추적 예제

[English](README.md) | 한국어

`inventory.py`에서 재고 5개 중 2개를 예약하고 3개가 남는 과정을 따라갑니다.
인증·저장소 읽기와 쓰기·시계는 가짜 의존성을 주입합니다. 하네스는 원래 함수를
실행하며 각 줄 실행 직전의 지역 변수와 저장 함수에 넘긴 인자를 기록합니다.
실제 서비스에 접속하거나 비공개 앱 코드를 사용하지 않습니다.

## 결과 예시

![코드 줄 강조와 남은 재고 3 표시](preview/demo.gif)

[18초 예제 영상 재생 또는 다운로드](preview/demo.mp4)

GIF는 소리가 없는 반복 재생 예시입니다. MP4에는 임시 로컬 영어 음성이 있습니다.
자막과 강조 타이밍은 음성 길이에 비례해 추정한 값입니다.

검증된 영상을 만든 뒤 MP4·GIF·대표 화면을 다시 내보낼 수 있습니다.

```bash
/tmp/code-trace-venv/bin/python example-code-trace/pipeline.py --export-preview
```

## 실행 방법

저장소 루트에서 실행합니다. Python 3.11 이상, Git, FFmpeg/ffprobe와 루트의 고정 버전
의존성이 필요합니다. 임시 영어 음성은 macOS의 `say`(Samantha 음성) 또는 Linux의
`espeak`로 만듭니다.

```bash
python3 -m venv /tmp/code-trace-venv
/tmp/code-trace-venv/bin/pip install -r requirements.txt
PATH="/tmp/code-trace-venv/bin:$PATH" bash example/assets/fetch-font.sh
/tmp/code-trace-venv/bin/python example-code-trace/pipeline.py
# 코드 줄 중심 방식: 값은 설명용 입력값으로 표시
/tmp/code-trace-venv/bin/python example-code-trace/pipeline.py --mode lines
```

| 방식 | 화면과 근거 |
|---|---|
| `debugger`(기본) | 원래 함수를 가짜 의존성과 함께 실행하고 기록된 값을 표시 |
| `lines` | 코드 줄을 나레이션에 맞춰 강조하고 설명용 입력값을 표시 |

어댑터는 기존 예제의 `prepare.py`, 렌더러·인코더, `qa.py`, 그리기 라이브러리,
`package.py`를 Git에서 제외한 `build/` 폴더로 복사해 재사용합니다.
코드 패널과 강조 시점을 추가한 뒤 공통 파이프라인을 실행합니다. 유료 TTS 호출은
없으며, 나레이션과 일치하는 기존 로컬 음성이 있으면 재사용합니다.

`build/master.mp4`는 1280×720·30fps H.264 + 모노 48kHz AAC 영상입니다.
`build/player.html`은 서버 없이 상대 경로의 MP4 두 파트를 재생합니다.
각 파트의 프레임 수와 전체 디코딩을 따로 검사합니다.

기본 파일 크기 제한은 **15,000,000바이트**입니다. 제한을 넘는 장면 묶음은 장면 경계에서
나눕니다. 장면 하나만으로도 제한을 넘으면 오류를 내므로, 장면을 줄이거나 인코딩 설정을
조정해야 합니다. 작은 예제에서도 여러 파트 플레이어를 확인할 수 있게 기본 묶음은
2장면으로 설정했습니다.

기본 `debugger` 빌드 후 회귀 검사를 실행합니다.

```bash
/tmp/code-trace-venv/bin/python example-code-trace/test_invariants.py
```

## 검사 결과와 패키지 재실행

| 파일 | 내용 |
|---|---|
| `build/qa/code-trace.json` | Git 원본 대조, 강조·패널 시간 범위, 모든 프레임의 실제 글꼴 배치 검사 |
| `build/qa/qa.json` | 인코딩된 영상·움직임·음성·장면 전환·탐색 검사 |
| `build/source-fidelity-review.json` | 성공 경로에서 설명한 내용과 확인하지 않은 분기 |
| `build/parts.json` | 파트별 크기·해시·길이·프레임 수·원본 장면 범위 |
| `build/source.zip` | 다시 렌더링할 코드, 공통 스크립트, 글꼴·라이선스, 음성 |
| `build/qa/package-rerender.json` | 새 폴더에 압축을 풀어 2초 영상을 렌더링한 결과와 대표 시점의 RGB 비교 |

압축을 푼 폴더에서 고정 버전 의존성을 설치하고 `render.py`, `qa.py` 순서로 실행하면
됩니다. 준비된 데이터와 음성이 들어 있어 저장소의 `pipeline.py` 없이 재실행할 수
있습니다. 이 패키지는 전체 영상 렌더러용이며 파트 영상과 플레이어는 로컬 파생 파일입니다.

빌드 결과는 기본적으로 Git에서 제외됩니다. `preview/`에는 검토용으로 선택한 가상 예제의
MP4·GIF·대표 화면·검증 메타데이터만 들어 있습니다.

## 예제가 확인하는 범위

줄 이벤트는 **강조한 줄을 실행하기 전**의 값입니다. 해당 줄의 계산 결과는 다음 이벤트에
나옵니다. 자막과 키워드 타이밍은 측정된 음성 길이를 바탕으로 한 비례 추정이며,
정밀 음성 정렬을 수행한 결과가 아닙니다.

임시 음성으로 파이프라인을 검증한 예제입니다. 전체 청취, 음성 인식, 독립적인 내용
검토를 수행했다고 주장하지 않습니다. 성공 경로 하나를 실행한 결과만으로 실제 인증·저장소
연동이나 모든 오류 분기가 검증되지는 않습니다.
