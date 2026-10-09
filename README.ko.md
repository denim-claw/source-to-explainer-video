# source-to-explainer-video

[English](README.md) | 한국어

**확인된 원본 자료** — 책의 한 장, 논문, 명세, 코드 변경 — 를 나레이션·다이어그램·자막이
있는 설명 영상으로 만듭니다. 원본과 설명이 일치하는지 확인하고, 완성된 영상 파일을
검사한 뒤 다시 렌더링할 수 있는 소스 패키지도 생성합니다.

요청에 따라 영상 대신, 또는 영상과 함께 다이어그램 파일이나 모바일 HTML 페이지를
만들 수 있습니다.

이 저장소에는 **Hermes Agent 스킬**과 **실행 가능한 예제**가 들어 있습니다.
기존 스킬 세 개의 기능을 통합했습니다.

| 기존 스킬 | 통합한 기능 |
|---|---|
| `karpathy-output-understanding` | 명료한 글, 다이어그램, 인터랙티브 페이지, 사람이 결과를 검토하는 흐름 |
| `book-concept-video` | 장면 기획, 장면별 음성 생성과 출처 기록, 측정된 길이에 따른 타이밍, 시간만으로 결정되는 렌더링, 원본 대조 |
| `video-deliverable-qa` | 인코딩된 파일 검사, 장면 전환 샘플, 파생 파일 생성, 압축 패키지 재실행 |

## 설명 방식

| 보고 싶은 내용 | 방식 |
|---|---|
| 책·논문·명세의 개념 | 나레이션과 도형 애니메이션으로 설명 |
| 코드 변경 전후의 동작 | 흐름도로 변경과 영향 설명 |
| 코드의 실행 순서와 값 변화 | 코드 줄 추적 또는 기록된 디버거 추적 |

![가상 재고 함수의 코드 강조와 값 변화](example-code-trace/preview/demo.gif)

[음성이 있는 18초 예제 영상](example-code-trace/preview/demo.mp4) ·
[코드 추적 예제 실행 방법](example-code-trace/README.ko.md)

GIF에는 소리가 없습니다. MP4는 임시 로컬 영어 음성을 사용합니다. 화면의 코드와 값은
직접 만든 가상 재고 예제이며 실제 서비스 데이터가 아닙니다.

## 영상이 기본 출력인 이유

나레이션이 있는 설명은 이동 중에도 들을 수 있습니다. 자료의 구조, 동작 경로,
조건과 아직 확인하지 못한 부분을 먼저 이해하고 코드를 검토할 수 있도록, 기본 출력은
영상으로 정했습니다. 글과 HTML은 요청할 때 추가합니다.

## 저장소 구조

```text
SKILL.md                        스킬 진입점: 작업 흐름, 출력 조건, 주의점
references/
  pipeline.md                   명령 실행 순서와 유지해야 할 조건
  renderer-notes.md             화면 배치, 애니메이션, 장면 전환 규칙
  tts.md                        장면별 음성 생성, 출처 기록, 재사용, 자막
  video-qa.md                   인코딩된 영상 검사 목록
  source-fidelity.md            원본 항목·조건·예외 대조
  from-code-review.md           코드 변경이나 PR의 동작 설명
  code-trace.md                 코드 줄 추적과 디버거 추적
  asd-ste-80.md                 ASD-STE에서 착안한 명료한 글 작성
example/                        실행 가능한 3장면 설명 영상 예제
example-code-trace/             가상 코드·값 추적 및 여러 파트 플레이어
requirements.txt                버전을 고정한 Python 의존성
```

## 빠르게 시작하기

저장소 루트에서 실행합니다.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd example
bash assets/fetch-font.sh          # 또는 EXPLAINER_FONT에 폰트 절대 경로 지정
bash make_demo_audio.sh            # 말소리가 없는 임시 배경음 생성
../.venv/bin/python design.py
../.venv/bin/python prepare.py
../.venv/bin/python render.py --samples
../.venv/bin/python render.py --determinism
../.venv/bin/python render.py      # → master.mp4
../.venv/bin/python qa.py
../.venv/bin/python fidelity.py
../.venv/bin/python package.py
```

이 예제는 1280×720, 30fps, H.264 + AAC MP4를 실제로 렌더링합니다. 완성된 파일을 검사하고,
허용한 파일만 담은 압축 패키지를 만듭니다. 패키지를 새 폴더에 풀어 2초짜리 영상을
다시 렌더링하고, 전체 타임라인의 대표 시점에서 RGB 해시를 비교합니다.

기본 예제의 임시 음성 파일은 **말소리가 없는 배경음**입니다. 실제 나레이션이 있는
결과물로 제공하려면 음성을 교체해야 합니다. 자세한 내용은 [기본 예제 안내](example/README.md),
임시 로컬 말소리를 사용하는 버전은 [코드 추적 예제 안내](example-code-trace/README.ko.md)를 보세요.

## 필요한 도구

- Python 3.11 이상
- `ffmpeg`와 `ffprobe`
- Pillow, NumPy, fontTools: `requirements.txt`의 고정 버전 사용
- 선택 사항: SVG 주석을 위한 시스템 Cairo 라이브러리와 `cairosvg`
- 재배포 가능한 라이선스의 한·중·일 글꼴: 별도 다운로드하며 글꼴 파일은 커밋하지 않음

## 핵심 제작 규칙

1. **원본부터 확정합니다.** 정확한 범위·판본·해시를 기록하며 비슷한 자료로 대체하지 않습니다.
2. **장면 하나에 주장 하나, 주장 하나에 시각적 변화 하나를 둡니다.** 경로가 열리거나
   상태가 교체되는 변화가 설명을 전달하게 합니다.
3. **설명을 위해 만든 비유를 표시합니다.** 좌표·개수·길이가 측정값이 아니라면 명시합니다.
4. **최종 인코딩 파일을 검사합니다.** 프레임 수를 확인하고 전체 디코딩을 수행하며,
   장면 전환과 전환 후 0.08·0.17·0.4초 시점을 추출합니다.
5. **원본 대조와 영상 검사를 구분합니다.** 영상이 정상 재생돼도 설명의 정확성이 입증되지는 않습니다.
6. **하지 않은 검사를 밝힙니다.** 전체 청취, 음성 인식, 정밀 자막 정렬, 독립 검토 여부를 기록합니다.
7. **공개와 업로드는 별도 요청이 필요합니다.** 영상 제작 요청이 배포 허락을 뜻하지 않습니다.

## 라이선스와 자료 취급

- 스킬 문서와 예제 코드는 MIT 라이선스입니다. [LICENSE](LICENSE)를 확인하세요.
- 글꼴은 별도로 받으며 라이선스 파일을 함께 보관합니다. [글꼴 안내](example/assets/README.md)를 참고하세요.
- 설명 대상인 책·논문·코드의 권리는 원저작자에게 있습니다. 설명을 만든다고 원본을
  재배포할 권한이 생기지는 않습니다.
- 비공개 스캔, 전체 OCR 텍스트, 인증 정보, 고객 데이터를 커밋하지 않습니다.
