#!/usr/bin/env python3
"""Integrity tests for the generated Excel workbook.

Run after ``python scripts/build_workbook.py``::

    python -m unittest discover -s tests -v

Checks the sheet inventory, the live variance formulas and the reconciliation
check formula. It does not recalculate the workbook (Excel/LibreOffice does that);
it asserts the formulas are the ones the methodology specifies.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
WORKBOOK = ROOT / "deliverables" / "expense_review_workbook.xlsx"

EXPECTED_SHEETS = [
    "README",
    "Transactions",
    "Summary_Category",
    "Summary_Month",
    "DQ_Summary",
    "DQ_Log",
    "Follow_Ups",
    "Reconciliation",
    "Assumptions",
]


class WorkbookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not WORKBOOK.exists():
            raise unittest.SkipTest(f"workbook not found: {WORKBOOK}")
        cls.wb = openpyxl.load_workbook(WORKBOOK, data_only=False)

    def test_sheet_inventory(self):
        self.assertEqual(self.wb.sheetnames, EXPECTED_SHEETS)

    def test_transactions_row_count(self):
        ws = self.wb["Transactions"]
        # Header row 1 + 442 clean rows.
        self.assertEqual(ws.max_row, 443)

    def test_variance_formulas(self):
        ws = self.wb["Transactions"]
        self.assertEqual(ws["I2"].value, "=H2-G2")
        # Guard matches methodology/ETL/SQL: budget >= 100 only.
        self.assertEqual(ws["J2"].value, '=IF(G2>=100,I2/G2,"n/a")')

    def test_category_summary_uses_sumifs(self):
        ws = self.wb["Summary_Category"]
        self.assertIn("SUMIFS(Transactions!$G:$G", ws["C4"].value)
        self.assertIn("SUMIFS(Transactions!$H:$H", ws["D4"].value)

    def test_reconciliation_check_is_live(self):
        ws = self.wb["Reconciliation"]
        self.assertEqual(ws["C10"].value, "=SUM(C4:C8)-C9")
        self.assertEqual(ws["D10"].value, "=SUM(D4:D8)-D9")

    def test_dq_summary_has_seventeen_checks(self):
        ws = self.wb["DQ_Summary"]
        self.assertEqual(ws.cell(row=4, column=1).value, "DQ01")
        self.assertEqual(ws.cell(row=20, column=1).value, "DQ17")

    def test_boundary_statement_present(self):
        ws = self.wb["README"]
        text = " ".join(
            str(c.value) for row in ws.iter_rows() for c in row if c.value is not None
        )
        self.assertIn("synthetic", text.lower())
        self.assertIn("not an audit", text.lower())


if __name__ == "__main__":
    unittest.main()
