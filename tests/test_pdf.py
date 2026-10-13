from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pymupdf

from drawing_compare.compare import compare_files
from drawing_compare.config import CompareConfig
from drawing_compare.pdf_extract import load_pdf


def _save_pdf(path: Path, label_shift: float = 0.0, add_change: bool = False) -> None:
    document = pymupdf.open()
    page = document.new_page(width=300, height=220)
    shape = page.new_shape()
    shape.draw_rect(pymupdf.Rect(20, 20, 280, 200))
    x = 70 + label_shift
    shape.draw_rect(pymupdf.Rect(x, 70, x + 20, 105))
    shape.draw_rect(pymupdf.Rect(x + 30, 70, x + 50, 105))
    if add_change:
        shape.draw_circle(pymupdf.Point(220, 140), 15)
        shape.draw_line(pymupdf.Point(205, 140), pymupdf.Point(235, 140))
    shape.finish(color=(0, 0, 0), width=0.7)
    shape.commit()
    document.save(path)
    document.close()


class PdfCompareTests(unittest.TestCase):
    def test_extracts_vector_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "drawing.pdf"
            _save_pdf(path)
            drawing = load_pdf(path)
            self.assertGreaterEqual(len(drawing.segments), 12)

    def test_pdf_change_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_path, new_path = root / "old.pdf", root / "new.pdf"
            _save_pdf(old_path)
            _save_pdf(new_path, add_change=True)
            result = compare_files(
                old_path,
                new_path,
                root / "result",
                CompareConfig(canvas_size=900, difference_join_px=6),
            )
            self.assertGreaterEqual(len(result.regions), 1)
            self.assertTrue(result.report_path and result.report_path.exists())
            self.assertTrue(result.annotated_pages)
            self.assertTrue((root / "result" / result.annotated_pages[0]).exists())

    def test_pdf_small_label_motion_is_suppressed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_path, new_path = root / "old.pdf", root / "new.pdf"
            _save_pdf(old_path)
            _save_pdf(new_path, label_shift=1.5)
            result = compare_files(
                old_path,
                new_path,
                root / "result",
                CompareConfig(
                    canvas_size=900,
                    difference_join_px=8,
                    local_search_margin_px=35,
                    minor_motion_limit_px=30,
                ),
            )
            self.assertEqual(result.regions, [])
            self.assertGreaterEqual(result.suppressed_minor_regions, 1)


if __name__ == "__main__":
    unittest.main()
