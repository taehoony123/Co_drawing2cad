# 벡터 PDF 비교 웹

이 폴더를 VS Code에서 열면 바로 실행할 수 있습니다.

## 1. 의존성 설치

VS Code 터미널에서:

```powershell
python -m pip install -r requirements.txt
```

또는 `터미널 > 작업 실행 > 의존성 설치`를 선택합니다.

## 2. 실행

다음 방법 중 하나를 사용합니다.

- `F5`를 누르고 `PDF 비교 웹 실행` 선택
- `start.ps1` 실행
- `start.bat` 실행
- VS Code 작업 `PDF 비교 웹 실행` 선택

브라우저 주소:

```text
http://127.0.0.1:8765
```

## 폴더 구성

```text
web/
├─ app.py                 # 개발 서버 진입점
├─ index.html             # 업로드 화면
├─ assets/
│  ├─ styles.css
│  └─ app.js
├─ requirements.txt
├─ start.ps1
├─ start.bat
└─ .vscode/               # F5 실행 설정
```

비교 엔진은 상위 폴더의 `drawing_compare` 패키지를 사용합니다. 결과는 상위 폴더의 `comparison_runs`에 생성됩니다.
