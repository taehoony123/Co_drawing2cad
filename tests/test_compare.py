from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ezdxf

from drawing_compare.compare import compare_files
from drawing_compare.config import CompareConfig


def _save_drawing(
    path: Path,
    shifted_label: float = 0.0,
    add_change: bool = False,
    global_shift: float = 0.0,
) -> None:
    document = ezdxf.new("R2018")
    model = document.modelspace()
    sx = global_shift
    model.add_lwpolyline([(sx, 0), (100 + sx, 0), (100 + sx, 80), (sx, 80), (sx, 0)])
    x = 20 + shifted_label + sx
    model.add_lwpolyline([(x, 20), (x + 8, 20), (x + 8, 32), (x, 32), (x, 20)])
    model.add_lwpolyline([(x + 12, 20), (x + 20, 20), (x + 20, 32), (x + 12, 32), (x + 12, 20)])
    if add_change:
        model.add_circle((72 + sx, 52), 6)
        model.add_line((72 + sx, 46), (72 + sx, 58))
    document.saveas(path)


class CompareTests(unittest.TestCase):
    def test_detects_added_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_path, new_path = root / "old.dxf", root / "new.dxf"
            _save_drawing(old_path)
            _save_drawing(new_path, add_change=True)
            result = compare_files(
                old_path,
                new_path,
                root / "result",
                CompareConfig(canvas_size=900, difference_join_px=6),
            )
            self.assertGreaterEqual(len(result.regions), 1)
            self.assertTrue(result.overlay_path.exists())
            self.assertTrue(result.report_path and result.report_path.exists())

    def test_identical_files_have_no_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_path, new_path = root / "old.dxf", root / "new.dxf"
            _save_drawing(old_path)
            _save_drawing(new_path)
            result = compare_files(old_path, new_path, root / "result", CompareConfig(canvas_size=900))
            self.assertEqual(result.regions, [])

    def test_small_local_label_motion_is_suppressed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_path, new_path = root / "old.dxf", root / "new.dxf"
            _save_drawing(old_path)
            _save_drawing(new_path, shifted_label=0.7)
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

    def test_whole_drawing_translation_is_aligned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_path, new_path = root / "old.dxf", root / "new.dxf"
            _save_drawing(old_path)
            _save_drawing(new_path, global_shift=4.0)
            result = compare_files(
                old_path,
                new_path,
                root / "result",
                CompareConfig(canvas_size=900, global_shift_limit_ratio=0.12),
            )
            self.assertEqual(result.regions, [])
            self.assertAlmostEqual(result.global_shift_drawing[0], 4.0, delta=0.6)


if __name__ == "__main__":
    unittest.main()

