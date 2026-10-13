from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .compare import compare_files


BASE_DIR = Path.cwd() / "comparison_runs"
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
BASE_DIR.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="벡터 PDF 자동 비교")
app.mount("/results", StaticFiles(directory=BASE_DIR), name="results")
app.mount("/assets", StaticFiles(directory=WEB_DIR / "assets"), name="assets")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (WEB_DIR / "index.html").read_text(encoding="utf-8")


def _safe_name(upload: UploadFile, fallback: str) -> str:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix != ".pdf":
        raise HTTPException(400, "벡터 PDF 파일만 사용할 수 있습니다.")
    return fallback + suffix


@app.post("/api/compare")
def compare(old_file: UploadFile = File(...), new_file: UploadFile = File(...)) -> dict[str, object]:
    run_id = uuid.uuid4().hex[:12]
    run_dir = BASE_DIR / run_id
    input_dir = run_dir / "input"
    output_dir = run_dir / "result"
    input_dir.mkdir(parents=True)
    old_path = input_dir / _safe_name(old_file, "old")
    new_path = input_dir / _safe_name(new_file, "new")
    with old_path.open("wb") as destination:
        shutil.copyfileobj(old_file.file, destination)
    with new_path.open("wb") as destination:
        shutil.copyfileobj(new_file.file, destination)
    try:
        result = compare_files(old_path, new_path, output_dir)
    except Exception as error:
        raise HTTPException(422, str(error)) from error
    return {
        "run_id": run_id,
        "change_count": len(result.regions),
        "report_url": f"/results/{run_id}/result/report.html",
        "json_url": f"/results/{run_id}/result/result.json",
    }

