#!/usr/bin/env python3
"""Regression tests for the data-quality and variance pipeline.

Runs with the standard library only::

    python -m unittest discover -s tests -v

The suite rebuilds the pipeline in memory from the canonical synthetic CSV, so it
does not depend on, and does not overwrite, ``data/processed/``.

Educational synthetic data only. Not an audit opinion.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import etl_review  # noqa: E402  (import after sys.path tweak)


def build_frame():
    """Reproduce ``main()`` up to (but excluding) the file writes."""
    df = etl_review.load_raw()
    df = etl_review.add_checks(df)
    df["dq_flags"] = df.apply(etl_review.build_flags, axis=1)
    df["disposition"] = df.apply(etl_review.assign_disposition, axis=1)
    df["exclusion_bucket"] = df.apply(etl_review.exclusion_bucket, axis=1)
    df["needs_review"] = df["disposition"] == "INCLUDE_FLAGGED"
    df["included"] = df["disposition"].isin(etl_review.INCLUDED_DISPOSITIONS)
    return etl_review.add_variance(df)


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = build_frame()
        cls.clean = cls.df[cls.df["included"]]

    # -- population ---------------------------------------------------------
    def test_raw_row_count(self):
        self.assertEqual(len(self.df), 454)

    def test_clean_row_count(self):
        self.assertEqual(len(self.clean), 442)

    def test_excluded_row_count(self):
        self.assertEqual(int((~self.df["included"]).sum()), 12)

    # -- totals -------------------------------------------------------------
    def test_clean_totals(self):
        self.assertAlmostEqual(float(self.clean["budget"].sum()), 2027057.54, places=2)
        self.assertAlmostEqual(float(self.clean["actual_amount"].sum()), 2086437.42, places=2)
        self.assertAlmostEqual(float(self.clean["variance_eur"].sum()), 59379.88, places=2)

    def test_variance_identity(self):
        valid = self.df["variance_eur"].notna()
        diff = (
            self.df.loc[valid, "actual_amount"]
            - self.df.loc[valid, "budget"]
            - self.df.loc[valid, "variance_eur"]
        ).abs()
        self.assertTrue((diff < 0.005).all())

    def test_variance_pct_guard(self):
        has_pct = self.df["variance_pct"].notna()
        eligible = (
            self.df["budget"].notna()
            & self.df["actual_amount"].notna()
            & (self.df["budget"] >= etl_review.BUDGET_PCT_FLOOR)
        )
        self.assertTrue((has_pct == eligible).all())

    # -- dispositions -------------------------------------------------------
    def test_disposition_counts(self):
        counts = self.df["disposition"].value_counts().to_dict()
        self.assertEqual(counts.get("INCLUDE"), 417)
        self.assertEqual(counts.get("CORRECT_AND_INCLUDE"), 7)
        self.assertEqual(counts.get("INCLUDE_FLAGGED"), 18)
        self.assertEqual(counts.get("QUARANTINE"), 10)
        self.assertEqual(counts.get("EXCLUDE_OUT_OF_PERIOD"), 2)
        self.assertEqual(sum(counts.values()), 454)

    # -- reconciliation -----------------------------------------------------
    def test_reconciliation_balances(self):
        excluded = self.df.loc[~self.df["included"]]
        self.assertAlmostEqual(
            float(self.df["budget"].sum() - excluded["budget"].sum() - self.clean["budget"].sum()),
            0.0,
            places=2,
        )
        self.assertAlmostEqual(
            float(
                self.df["actual_amount"].sum()
                - excluded["actual_amount"].sum()
                - self.clean["actual_amount"].sum()
            ),
            0.0,
            places=2,
        )

    # -- specific planted defects ------------------------------------------
    def test_exact_duplicates_quarantined(self):
        dups = self.df[self.df["exact_duplicate"]]
        self.assertEqual(len(dups), 2)
        self.assertTrue((dups["disposition"] == "QUARANTINE").all())

    def test_near_duplicates_flagged(self):
        near = self.df[self.df["near_duplicate"]]
        self.assertEqual(len(near), 4)
        self.assertTrue((near["disposition"] == "INCLUDE_FLAGGED").all())

    def test_out_of_period_excluded(self):
        oop = self.df[self.df["out_of_period"]]
        self.assertEqual(len(oop), 2)
        self.assertTrue((oop["disposition"] == "EXCLUDE_OUT_OF_PERIOD").all())

    def test_clean_ledger_has_no_unmapped_labels(self):
        self.assertFalse(bool(self.clean["invalid_category"].any()))
        self.assertFalse(bool(self.clean["invalid_department"].any()))

    # -- 17 checks ----------------------------------------------------------
    def test_dq_summary_counts(self):
        masks = {
            "DQ01": self.df["exact_duplicate"],
            "DQ02": self.df["near_duplicate"],
            "DQ03": self.df["date_issue"] == "MISSING_DATE",
            "DQ04": self.df["date_issue"] == "INVALID_DATE",
            "DQ05": self.df["date_issue"] == "DATE_FORMAT_NORMALISED",
            "DQ06": self.df["out_of_period"],
            "DQ07": self.df["category_corrected"],
            "DQ08": self.df["invalid_category"],
            "DQ09": self.df["invalid_department"],
            "DQ10": self.df["invalid_amount"],
            "DQ11": self.df["negative_budget"],
            "DQ12": self.df["credit_note"],
            "DQ13": self.df["unbudgeted"],
            "DQ14": self.df["tiny_budget"],
            "DQ15": self.df["outlier"],
            "DQ16": self.df["blank_description"],
            "DQ17": self.df["zero_activity"],
        }
        expected = {
            "DQ01": 2, "DQ02": 4, "DQ03": 4, "DQ04": 3, "DQ05": 1,
            "DQ06": 2, "DQ07": 6, "DQ08": 0, "DQ09": 0, "DQ10": 0,
            "DQ11": 1, "DQ12": 4, "DQ13": 3, "DQ14": 2, "DQ15": 5,
            "DQ16": 2, "DQ17": 0,
        }
        for check_id, mask in masks.items():
            self.assertEqual(int(mask.sum()), expected[check_id], check_id)

    # -- selection logic ----------------------------------------------------
    def test_narrow_threshold_and_broad_screen(self):
        narrow = self.clean[
            (self.clean["variance_eur"].abs() >= 1000)
            & (self.clean["variance_pct"].abs() >= 10)
        ]
        self.assertEqual(len(narrow), 19)

        flags = self.clean["dq_flags"].fillna("")
        broad = self.clean[
            (self.clean["variance_eur"].abs() >= 1000)
            | flags.str.contains("UNBUDGETED")
            | flags.str.contains("CREDIT_NOTE")
            | flags.str.contains("OUTLIER")
        ]
        self.assertEqual(len(broad), 25)

    def test_follow_up_transactions_exist(self):
        ids = set(self.df["txn_id"])
        for txn in [
            "TXN-2166", "TXN-2326",
            "TXN-2364", "TXN-2451",
            "TXN-2348", "TXN-2452",
        ]:
            self.assertIn(txn, ids)


if __name__ == "__main__":
    unittest.main()
