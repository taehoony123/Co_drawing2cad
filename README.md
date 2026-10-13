# 벡터 PDF 자동 비교 MVP

두 벡터 PDF 도면을 중첩하고 기존 도면 전용 벡터는 빨강, 신규 도면 전용 벡터는 초록, 공통 벡터는 회색으로 표시합니다. 지역별 작은 이동은 다시 정렬해 제거하고, 남은 중요 변경을 HTML과 JSON으로 정리합니다. 선택적으로 멀티모달 LLM이 변경 후보를 한국어로 설명할 수 있습니다.

## 설치

Python 3.11 이상이 필요합니다. 프로젝트 루트에서 가상환경을 만들고 패키지를 설치합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## 실행

```powershell
python -m drawing_compare serve
```

브라우저에서 `http://127.0.0.1:8000`을 열고 기존/신규 벡터 PDF를 선택합니다.

Windows에서는 아래 실행 파일을 사용할 수도 있습니다. 이 경우 주소는 `http://127.0.0.1:8765`입니다.

```powershell
.\web\start.ps1
```

CLI로 직접 비교할 수도 있습니다.

```powershell
python -m drawing_compare compare old.pdf new.pdf --out comparison_result
```

결과물:

- `report.html`: 색상 오버레이와 변경 목록
- `result.json`: 외부 시스템 연동용 구조화 결과
- `overlay.png`: 전체 비교 이미지
- `regions/*.png`: 변경 후보별 이미지

## PDF 입력

PDF 내부의 직선, 사각형, 쿼드, Bézier path를 직접 추출합니다. 글자가 선으로 변환된 PDF도 path로 비교합니다. 여러 페이지는 페이지별 좌표를 분리해 한 번에 처리합니다.

스캔 이미지로만 구성된 PDF에는 벡터가 없으므로 현재 버전에서는 오류를 표시합니다.

## 기존 DWG/DXF 엔진

CLI 비교 엔진에는 기존 DWG/DXF 어댑터도 남아 있습니다. DXF는 바로 읽고 DWG는 다음 변환기 중 하나를 자동으로 사용합니다.

1. 설치된 AutoCAD의 `accoreconsole.exe`
2. ODA File Converter
3. LibreDWG의 `dwg2dxf`

이 PC에서는 설치된 AutoCAD 2027 Core Console이 자동 탐지됩니다. 다른 위치의 AutoCAD를 사용하려면 다음처럼 지정합니다.

```powershell
$env:ACCORECONSOLE = 'C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe'
```

ODA를 자동으로 찾지 못하면 다음 환경변수를 지정합니다.

```powershell
$env:ODA_FILE_CONVERTER = 'C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe'
```

DWG 파싱은 별도 SDK가 필요한 영역이므로 변환기를 어댑터로 분리했습니다.

## 선택적 LLM 설명

설정하지 않으면 기하 통계에 기반한 보수적인 설명을 생성합니다. OpenAI 호환 멀티모달 Chat Completions 엔드포인트를 사용하려면 다음 값을 지정합니다.

```powershell
$env:DRAWING_COMPARE_LLM_URL = 'https://provider.example/v1/chat/completions'
$env:DRAWING_COMPARE_LLM_API_KEY = '...'
$env:DRAWING_COMPARE_LLM_MODEL = 'vision-model-name'
```

LLM은 변경 위치를 찾지 않습니다. 기하 엔진이 확정한 변경 후보 이미지와 수치를 받아 설명만 생성합니다. 호출이 실패하면 자동으로 규칙 기반 설명으로 전환합니다.

저장소의 `.env.example`에는 필요한 변수 이름만 들어 있습니다. 실제 API 키가 포함된 `.env` 파일과 실행 중 업로드된 도면은 Git에서 제외됩니다. 현재 프로그램은 `.env` 파일을 자동으로 읽지 않으므로 실행 전에 위 예시처럼 환경변수를 설정해야 합니다.

## 자동 판정 원칙

- 전체 좌표 차이는 전역 정렬로 제거합니다.
- 색상 차이 영역은 지역별로 다시 정렬합니다.
- 정렬 후 잔차가 작으면 글자나 도형의 작은 위치 이동으로 보고 제외합니다.
- 정렬 후에도 남는 빨강·초록 벡터만 변경 목록에 포함합니다.
- 모호한 형상을 구체적인 문자나 부품명으로 추측하지 않습니다.

## 테스트

```powershell
python -m unittest discover -s tests -v
```

AutoCAD Core Console을 실제로 실행하는 통합 테스트는 기본 테스트에서 제외됩니다. 해당 환경에서만 다음처럼 별도로 실행할 수 있습니다.

```powershell
$env:RUN_AUTOCAD_INTEGRATION_TESTS = '1'
python -m unittest tests.test_dwg -v
```

## 업로드 전 확인

- `.env`, `comparison_runs`, `comparison_result`, `ErrorReports`는 업로드하지 않습니다. 이 폴더에는 실제 도면이나 분석 결과가 포함될 수 있습니다.
- `.env.example`에는 예시 값만 유지하고 실제 API 키를 넣지 않습니다.
- GitHub 웹 화면에서 직접 올릴 때는 숨김 파일인 `.gitignore`, `.gitattributes`, `.env.example`도 함께 선택합니다.
- 배포 라이선스를 정했다면 루트에 `LICENSE` 파일을 추가합니다. 라이선스가 정해지지 않은 현재 상태에서는 임의로 추가하지 않았습니다.

실제 도면을 적용하기 전 `drawing_compare/config.py`의 허용오차를 대표 PDF 쌍으로 조정해야 합니다.
