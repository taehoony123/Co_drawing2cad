from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import ezdxf

from drawing_compare.dwg import _autocad_to_dxf, _find_accoreconsole


class DwgAdapterTests(unittest.TestCase):
    @unittest.skipUnless(
        os.getenv("RUN_AUTOCAD_INTEGRATION_TESTS") == "1" and _find_accoreconsole(),
        "set RUN_AUTOCAD_INTEGRATION_TESTS=1 to run the AutoCAD integration test",
    )
    def test_autocad_core_console_exports_dxf(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.dxf"
            target = root / "exported" / "target.dxf"
            document = ezdxf.new("R2018")
            document.modelspace().add_line((0, 0), (10, 10))
            document.saveas(source)
            exported = _autocad_to_dxf(source, target)
            self.assertEqual(exported, target)
            self.assertTrue(target.exists())
            self.assertGreater(len(ezdxf.readfile(target).modelspace()), 0)


if __name__ == "__main__":
    unittest.main()
