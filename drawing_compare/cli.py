from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from .compare import compare_files


def main() -> None:
    parser = argparse.ArgumentParser(description="벡터 PDF 도면 변경 비교")
    subparsers = parser.add_subparsers(dest="command", required=True)
    compare_parser = subparsers.add_parser("compare", help="두 도면 비교")
    compare_parser.add_argument("old_file", type=Path)
    compare_parser.add_argument("new_file", type=Path)
    compare_parser.add_argument("--out", type=Path, default=Path("comparison_result"))
    serve_parser = subparsers.add_parser("serve", help="웹 업로드 화면 실행")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "compare":
        result = compare_files(args.old_file, args.new_file, args.out)
        print(f"변경 영역: {len(result.regions)}")
        print(f"보고서: {result.report_path.resolve()}")
    else:
        uvicorn.run("drawing_compare.web:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()

