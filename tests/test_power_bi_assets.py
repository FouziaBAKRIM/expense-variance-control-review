#!/usr/bin/env python3
"""Integrity tests for the Power BI layer.

These do not open Power BI. They check that the assets the build guide depends on
exist, parse, and carry the verified figures — so a later edit cannot silently
break the guide or the mockup.

Run with the rest of the suite::

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import csv
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PBI = ROOT / "power_bi"
DATA = PBI / "data"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class PowerBIAssetTests(unittest.TestCase):
    # -- files exist --------------------------------------------------------
    def test_build_assets_exist(self):
        for path in [
            PBI / "POWER_BI_BUILD_GUIDE.md",
            PBI / "DAX_MEASURES.md",
            PBI / "theme_expense_review.json",
            PBI / "screenshots" / "README.md",
            PBI / "screenshots" / "dashboard_mockup.html",
            PBI / "screenshots" / "dashboard_mockup.png",
        ]:
            self.assertTrue(path.exists(), f"missing {path.relative_to(ROOT)}")

    # -- control tests ------------------------------------------------------
    def test_control_tests_shape(self):
        rows = read_csv("control_tests.csv")
        self.assertEqual(len(rows), 9)
        self.assertEqual([r["test_id"] for r in rows], [f"T0{i}" for i in range(1, 10)])
        self.assertEqual(rows[-1]["outcome"], "Clean")
        self.assertEqual(rows[0]["exception_amount_eur"], "7289.32")

    # -- risk matrix --------------------------------------------------------
    def test_risk_matrix_shape(self):
        rows = read_csv("risk_matrix.csv")
        self.assertEqual(len(rows), 9)
        self.assertEqual(sorted(int(r["priority_rank"]) for r in rows), list(range(1, 10)))
        for row in rows:
            self.assertIn(row["design_testable"], {"Yes", "No", "Partly"})
            self.assertIn(row["operating_testable"], {"Yes", "No", "Partly"})

    # -- follow-ups ---------------------------------------------------------
    def test_follow_up_total_and_status(self):
        rows = read_csv("selected_follow_ups.csv")
        self.assertEqual(len(rows), 3)
        total = sum(float(r["at_risk_eur"]) for r in rows)
        self.assertAlmostEqual(total, 34707.05, places=2)
        self.assertTrue(all(r["status"] == "Evidence requested" for r in rows))

    # -- guide content ------------------------------------------------------
    def test_guide_carries_verified_figures_and_boundary(self):
        text = (PBI / "POWER_BI_BUILD_GUIDE.md").read_text(encoding="utf-8")
        for expected in [
            "2,027,057.54",
            "2,086,437.42",
            "59,379.88",
            "37",
            "39",
            "Reconciliation Gap",
            "statutory audit",
        ]:
            self.assertIn(expected, text)
        self.assertIn("synthetic", text.lower())
        self.assertNotIn("TODO", text)
        self.assertNotIn("TBD", text)

    def test_theme_is_valid_json(self):
        theme = json.loads((PBI / "theme_expense_review.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(theme["dataColors"]), 8)
        self.assertEqual(theme["good"], "#2E7D32")
        self.assertEqual(theme["bad"], "#C0392B")

    # -- mockup -------------------------------------------------------------
    def test_mockup_png_is_1600x900(self):
        raw = (PBI / "screenshots" / "dashboard_mockup.png").read_bytes()
        width, height = struct.unpack(">II", raw[16:24])
        self.assertEqual((width, height), (1600, 900))

    def test_mockup_is_labelled_as_a_mockup(self):
        html = (PBI / "screenshots" / "dashboard_mockup.html").read_text(encoding="utf-8")
        self.assertIn("not a Power BI render", html)
        self.assertIn("Synthetic", html)
        self.assertIn("€0.00", html)


if __name__ == "__main__":
    unittest.main()
