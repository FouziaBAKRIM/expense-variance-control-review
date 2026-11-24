#!/usr/bin/env python3
"""Build the formula-driven expense review workbook.

Output: deliverables/expense_review_workbook.xlsx

The Transactions sheet uses live formulas for variance and variance %.
Summary sheets use SUMIFS/COUNTIF against the Transactions sheet, so the
workbook recalculates when a line is edited. Educational synthetic data only.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED = BASE_DIR / "data" / "processed"
OUT = BASE_DIR / "deliverables" / "expense_review_workbook.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(bold=True, size=16, color="1F4E79")
SUBTITLE_FONT = Font(italic=True, size=10, color="595959")
BODY_FONT = Font(size=10)
BOLD = Font(bold=True, size=10)
WARN_FILL = PatternFill("solid", fgColor="FFF2CC")
TOTAL_FILL = PatternFill("solid", fgColor="D9E1F2")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

MONEY = "#,##0.00"
PCT = "0.00%"
INT = "#,##0"


def header_row(ws, row: int, headers: list[str]) -> None:
    for col, text in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=text)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def set_widths(ws, widths: dict[str, float]) -> None:
    for col, width in widths.items():
        ws.column_dimensions[col].width = width


def style_body(ws, first_row: int, last_row: int, last_col: int) -> None:
    for row in ws.iter_rows(min_row=first_row, max_row=last_row, max_col=last_col):
        for cell in row:
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=False)


def main() -> None:
    clean = pd.read_csv(PROCESSED / "expenses_clean.csv")
    exceptions = pd.read_csv(PROCESSED / "dq_exceptions_log.csv")
    dq_summary = pd.read_csv(PROCESSED / "dq_summary.csv")
    by_category = pd.read_csv(PROCESSED / "summary_by_category.csv")
    by_month = pd.read_csv(PROCESSED / "summary_by_month.csv")
    reconciliation = pd.read_csv(PROCESSED / "reconciliation.csv")

    wb = Workbook()

    # ------------------------------------------------------------------ README
    ws = wb.active
    ws.title = "README"
    ws["A1"] = "H1 2026 Expense Variance Review"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:F1")
    ws["A2"] = "Synthetic educational dataset — not an audit, assurance engagement or financial advice"
    ws["A2"].font = SUBTITLE_FONT
    ws.merge_cells("A2:F2")

    ws["A4"] = "PURPOSE"
    ws["A4"].font = BOLD
    ws["A5"] = (
        "First-pass review of budget-versus-actual expense performance for a fictional retailer, "
        "with data-quality exceptions, variance commentary and three follow-up items."
    )
    ws.merge_cells("A5:F5")
    ws["A5"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[5].height = 32

    ws["A7"] = "KEY FIGURES (clean ledger)"
    ws["A7"].font = BOLD
    figures = [
        ("Rows reviewed (raw)", 454, INT),
        ("Rows in clean ledger", 442, INT),
        ("Budget (EUR)", 2_027_057.54, MONEY),
        ("Actual (EUR)", 2_086_437.42, MONEY),
        ("Variance (EUR)", 59_379.88, MONEY),
        ("Variance %", 0.0293, PCT),
    ]
    for i, (label, value, fmt) in enumerate(figures, start=8):
        ws.cell(row=i, column=1, value=label).font = BODY_FONT
        cell = ws.cell(row=i, column=2, value=value)
        cell.font = BODY_FONT
        cell.number_format = fmt

    ws["A15"] = "SHEETS"
    ws["A15"].font = BOLD
    sheets = [
        ("Transactions", "Clean ledger, one row per transaction, live variance formulas."),
        ("Summary_Category", "SUMIFS by category; variance and variance % are formulas."),
        ("Summary_Month", "SUMIFS by month; variance and variance % are formulas."),
        ("DQ_Summary", "All 17 data-quality checks with rows and amounts affected."),
        ("DQ_Log", "Every flagged, corrected or quarantined row with its reason."),
        ("Follow_Ups", "Three items selected for evidence-based follow-up."),
        ("Reconciliation", "Raw to clean bridge; the check row is a live formula."),
        ("Assumptions", "A01–A14 assumptions register."),
    ]
    for i, (name, desc) in enumerate(sheets, start=16):
        ws.cell(row=i, column=1, value=name).font = BOLD
        ws.cell(row=i, column=2, value=desc).font = BODY_FONT
        ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=6)

    ws["A26"] = "FORMULAS"
    ws["A26"].font = BOLD
    ws["A27"] = (
        "Transactions!I = actual - budget. Transactions!J = variance / budget only when "
        "budget >= 100, otherwise 'n/a'. Summary sheets use COUNTIF/SUMIFS against Transactions."
    )
    ws.merge_cells("A27:F27")
    ws["A27"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[27].height = 32

    ws["A29"] = "BOUNDARY"
    ws["A29"].font = BOLD
    ws["A30"] = (
        "All data is synthetic. No real employer, client, bank, payroll or personal data is used. "
        "Nothing here is an audit opinion or financial advice."
    )
    ws.merge_cells("A30:F30")
    ws["A30"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["A30"].fill = WARN_FILL
    ws.row_dimensions[30].height = 32

    set_widths(ws, {"A": 26, "B": 22, "C": 18, "D": 18, "E": 18, "F": 30})

    # ------------------------------------------------------------- Transactions
    ws = wb.create_sheet("Transactions")
    headers = [
        "Txn ID", "Month", "Date", "Department", "Category", "Description",
        "Budget (EUR)", "Actual (EUR)", "Variance (EUR)", "Variance %",
        "Disposition", "DQ Flags",
    ]
    header_row(ws, 1, headers)

    for i, row in clean.iterrows():
        r = i + 2
        ws.cell(row=r, column=1, value=row["txn_id"])
        ws.cell(row=r, column=2, value=row["month"])
        ws.cell(row=r, column=3, value=row["date"])
        ws.cell(row=r, column=4, value=row["department"])
        ws.cell(row=r, column=5, value=row["category"])
        ws.cell(row=r, column=6, value=row["description"])
        ws.cell(row=r, column=7, value=float(row["budget"]))
        ws.cell(row=r, column=8, value=float(row["actual_amount"]))
        ws.cell(row=r, column=9, value=f"=H{r}-G{r}")
        ws.cell(row=r, column=10, value=f'=IF(AND(G{r}>=100,H{r}<>0),I{r}/G{r},"n/a")')
        ws.cell(row=r, column=11, value=row["disposition"])
        ws.cell(row=r, column=12, value=row["dq_flags"])

    last = len(clean) + 1
    style_body(ws, 2, last, len(headers))
    for r in range(2, last + 1):
        ws.cell(row=r, column=7).number_format = MONEY
        ws.cell(row=r, column=8).number_format = MONEY
        ws.cell(row=r, column=9).number_format = MONEY
        ws.cell(row=r, column=10).number_format = PCT
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:L{last}"
    set_widths(ws, {"A": 12, "B": 9, "C": 11, "D": 18, "E": 22, "F": 52, "G": 14, "H": 14, "I": 14, "J": 11, "K": 20, "L": 26})
    ws.conditional_formatting.add(
        f"I2:I{last}",
        CellIsRule(operator="greaterThan", formula=["0"], fill=PatternFill("solid", fgColor="FCE4D6")),
    )
    ws.conditional_formatting.add(
        f"I2:I{last}",
        CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor="E2EFDA")),
    )

    # ---------------------------------------------------------- Summary_Category
    ws = wb.create_sheet("Summary_Category")
    ws["A1"] = "Budget vs Actual by Category"
    ws["A1"].font = TITLE_FONT
    header_row(ws, 3, ["Category", "Transactions", "Budget (EUR)", "Actual (EUR)", "Variance (EUR)", "Variance %"])
    for i, row in by_category.reset_index(drop=True).iterrows():
        r = i + 4
        ws.cell(row=r, column=1, value=row["category"])
        ws.cell(row=r, column=2, value=f"=COUNTIF(Transactions!$E:$E,$A{r})")
        ws.cell(row=r, column=3, value=f"=SUMIFS(Transactions!$G:$G,Transactions!$E:$E,$A{r})")
        ws.cell(row=r, column=4, value=f"=SUMIFS(Transactions!$H:$H,Transactions!$E:$E,$A{r})")
        ws.cell(row=r, column=5, value=f"=D{r}-C{r}")
        ws.cell(row=r, column=6, value=f'=IF(C{r}>=100,E{r}/C{r},"n/a")')
    total = len(by_category) + 4
    ws.cell(row=total, column=1, value="Total")
    ws.cell(row=total, column=2, value=f"=SUM(B4:B{total-1})")
    ws.cell(row=total, column=3, value=f"=SUM(C4:C{total-1})")
    ws.cell(row=total, column=4, value=f"=SUM(D4:D{total-1})")
    ws.cell(row=total, column=5, value=f"=D{total}-C{total}")
    ws.cell(row=total, column=6, value=f'=IF(C{total}>=100,E{total}/C{total},"n/a")')
    style_body(ws, 4, total, 6)
    for r in range(4, total + 1):
        ws.cell(row=r, column=3).number_format = MONEY
        ws.cell(row=r, column=4).number_format = MONEY
        ws.cell(row=r, column=5).number_format = MONEY
        ws.cell(row=r, column=6).number_format = PCT
        ws.cell(row=r, column=2).number_format = INT
    for c in range(1, 7):
        ws.cell(row=total, column=c).font = BOLD
        ws.cell(row=total, column=c).fill = TOTAL_FILL
    ws.freeze_panes = "A4"
    set_widths(ws, {"A": 26, "B": 14, "C": 16, "D": 16, "E": 16, "F": 12})

    # ------------------------------------------------------------- Summary_Month
    ws = wb.create_sheet("Summary_Month")
    ws["A1"] = "Budget vs Actual by Month"
    ws["A1"].font = TITLE_FONT
    header_row(ws, 3, ["Month", "Transactions", "Budget (EUR)", "Actual (EUR)", "Variance (EUR)", "Variance %"])
    months = by_month.sort_values("month").reset_index(drop=True)
    for i, row in months.iterrows():
        r = i + 4
        ws.cell(row=r, column=1, value=row["month"])
        ws.cell(row=r, column=2, value=f"=COUNTIF(Transactions!$B:$B,$A{r})")
        ws.cell(row=r, column=3, value=f"=SUMIFS(Transactions!$G:$G,Transactions!$B:$B,$A{r})")
        ws.cell(row=r, column=4, value=f"=SUMIFS(Transactions!$H:$H,Transactions!$B:$B,$A{r})")
        ws.cell(row=r, column=5, value=f"=D{r}-C{r}")
        ws.cell(row=r, column=6, value=f'=IF(C{r}>=100,E{r}/C{r},"n/a")')
    total = len(months) + 4
    ws.cell(row=total, column=1, value="Total")
    ws.cell(row=total, column=2, value=f"=SUM(B4:B{total-1})")
    ws.cell(row=total, column=3, value=f"=SUM(C4:C{total-1})")
    ws.cell(row=total, column=4, value=f"=SUM(D4:D{total-1})")
    ws.cell(row=total, column=5, value=f"=D{total}-C{total}")
    ws.cell(row=total, column=6, value=f'=IF(C{total}>=100,E{total}/C{total},"n/a")')
    style_body(ws, 4, total, 6)
    for r in range(4, total + 1):
        ws.cell(row=r, column=3).number_format = MONEY
        ws.cell(row=r, column=4).number_format = MONEY
        ws.cell(row=r, column=5).number_format = MONEY
        ws.cell(row=r, column=6).number_format = PCT
        ws.cell(row=r, column=2).number_format = INT
    for c in range(1, 7):
        ws.cell(row=total, column=c).font = BOLD
        ws.cell(row=total, column=c).fill = TOTAL_FILL
    ws.freeze_panes = "A4"
    set_widths(ws, {"A": 12, "B": 14, "C": 16, "D": 16, "E": 16, "F": 12})

    # ---------------------------------------------------------------- DQ_Summary
    ws = wb.create_sheet("DQ_Summary")
    ws["A1"] = "Data-Quality Checks"
    ws["A1"].font = TITLE_FONT
    dq_headers = ["ID", "Check", "Rule", "Rows", "Amount (EUR)", "Basis", "Disposition"]
    header_row(ws, 3, dq_headers)
    for i, row in dq_summary.iterrows():
        r = i + 4
        ws.cell(row=r, column=1, value=row["check_id"])
        ws.cell(row=r, column=2, value=row["check_name"])
        ws.cell(row=r, column=3, value=row["rule"])
        ws.cell(row=r, column=4, value=int(row["rows_affected"]))
        ws.cell(row=r, column=5, value=float(row["amount_affected_eur"]))
        ws.cell(row=r, column=6, value=row["amount_basis"])
        ws.cell(row=r, column=7, value=row["disposition"])
    last = len(dq_summary) + 3
    style_body(ws, 4, last, 7)
    for r in range(4, last + 1):
        ws.cell(row=r, column=4).number_format = INT
        ws.cell(row=r, column=5).number_format = MONEY
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:G{last}"
    set_widths(ws, {"A": 7, "B": 26, "C": 62, "D": 8, "E": 14, "F": 16, "G": 22})

    # -------------------------------------------------------------------- DQ_Log
    ws = wb.create_sheet("DQ_Log")
    ws["A1"] = "Data-Quality Exception Log"
    ws["A1"].font = TITLE_FONT
    log_headers = [
        "Txn ID", "Date", "Month", "Department", "Category", "Category (raw)",
        "Description", "Budget (EUR)", "Actual (EUR)", "Variance (EUR)",
        "Variance %", "Disposition", "DQ Flags",
    ]
    header_row(ws, 3, log_headers)
    for i, row in exceptions.iterrows():
        r = i + 4
        ws.cell(row=r, column=1, value=row["txn_id"])
        ws.cell(row=r, column=2, value=row["date"] if pd.notna(row["date"]) else "")
        ws.cell(row=r, column=3, value=row["month"])
        ws.cell(row=r, column=4, value=row["department"])
        ws.cell(row=r, column=5, value=row["category"])
        ws.cell(row=r, column=6, value=row["category_raw"])
        ws.cell(row=r, column=7, value=row["description"])
        ws.cell(row=r, column=8, value=float(row["budget"]))
        ws.cell(row=r, column=9, value=float(row["actual_amount"]))
        ws.cell(row=r, column=10, value=float(row["variance_eur"]))
        if pd.notna(row["variance_pct"]):
            ws.cell(row=r, column=11, value=float(row["variance_pct"]) / 100)
        ws.cell(row=r, column=12, value=row["disposition"])
        ws.cell(row=r, column=13, value=row["dq_flags"])
    last = len(exceptions) + 3
    style_body(ws, 4, last, len(log_headers))
    for r in range(4, last + 1):
        ws.cell(row=r, column=8).number_format = MONEY
        ws.cell(row=r, column=9).number_format = MONEY
        ws.cell(row=r, column=10).number_format = MONEY
        ws.cell(row=r, column=11).number_format = PCT
    ws.freeze_panes = "B4"
    ws.auto_filter.ref = f"A3:M{last}"
    set_widths(ws, {"A": 12, "B": 11, "C": 9, "D": 18, "E": 22, "F": 22, "G": 48, "H": 13, "I": 13, "J": 13, "K": 10, "L": 20, "M": 28})

    # ---------------------------------------------------------------- Follow_Ups
    ws = wb.create_sheet("Follow_Ups")
    ws["A1"] = "Three Items Selected for Follow-Up"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = "Requests for evidence, not allegations. No conclusion is drawn until evidence is obtained."
    ws["A2"].font = SUBTITLE_FONT
    ws.merge_cells("A2:H2")
    header_row(ws, 4, ["#", "Item", "Transaction(s)", "Amount at risk (EUR)", "Observation", "Why it needs checking", "Evidence required", "Status"])
    follow_ups = [
        (
            1,
            "Expedited air freight",
            "TXN-2166",
            15077.37,
            "EUR 18,942.63 actual vs EUR 3,865.26 budget (+390.07%); June freight +44.64%.",
            "Largest single adverse line; may reflect an approved emergency shipment, a rate change or a coding error.",
            "Carrier invoice, shipment approval, rate card, proof of delivery, reason for air mode.",
            "Evidence requested",
        ),
        (
            2,
            "Emergency chiller replacement",
            "TXN-2326",
            12340.36,
            "EUR 15,115.25 actual vs EUR 2,774.89 budget (+444.72%); January maintenance +61.74%.",
            "Possible capital-versus-revenue classification; emergency purchase may bypass normal quoting.",
            "Work order, quote, approval, asset register, capitalisation policy, invoice.",
            "Evidence requested",
        ),
        (
            3,
            "Duplicate invoice pair",
            "TXN-2364 / TXN-2451; TXN-2348 / TXN-2452",
            7289.32,
            "Two exact business-key duplicate pairs; later copies quarantined.",
            "A recording duplicate may or may not have been paid twice; control operation unknown.",
            "Invoices, payment records, bank statements, supplier statements, delivery evidence.",
            "Evidence requested",
        ),
    ]
    for i, item in enumerate(follow_ups):
        r = i + 5
        for col, value in enumerate(item, start=1):
            ws.cell(row=r, column=col, value=value)
    style_body(ws, 5, 7, 8)
    for r in range(5, 8):
        ws.cell(row=r, column=4).number_format = MONEY
        ws.row_dimensions[r].height = 60
        for c in range(5, 9):
            ws.cell(row=r, column=c).alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A5"
    set_widths(ws, {"A": 5, "B": 26, "C": 26, "D": 16, "E": 42, "F": 42, "G": 42, "H": 18})

    # ------------------------------------------------------------- Reconciliation
    ws = wb.create_sheet("Reconciliation")
    ws["A1"] = "Raw-to-Clean Reconciliation"
    ws["A1"].font = TITLE_FONT
    header_row(ws, 3, ["Step", "Rows", "Budget (EUR)", "Actual (EUR)", "Variance (EUR)"])
    for i, row in reconciliation.iterrows():
        r = i + 4
        ws.cell(row=r, column=1, value=row["bucket"])
        ws.cell(row=r, column=2, value=int(row["rows"]))
        ws.cell(row=r, column=3, value=float(row["budget_eur"]))
        ws.cell(row=r, column=4, value=float(row["actual_eur"]))
        ws.cell(row=r, column=5, value=f"=D{r}-C{r}")
    last = len(reconciliation) + 3
    # The final row is the check row: replace values with live formulas.
    ws.cell(row=last, column=1, value="CHECK (must be 0.00)")
    ws.cell(row=last, column=2, value=0)
    ws.cell(row=last, column=3, value=f"=SUM(C4:C{last-2})-C{last-1}")
    ws.cell(row=last, column=4, value=f"=SUM(D4:D{last-2})-D{last-1}")
    ws.cell(row=last, column=5, value=f"=D{last}-C{last}")
    style_body(ws, 4, last, 5)
    for r in range(4, last + 1):
        ws.cell(row=r, column=3).number_format = MONEY
        ws.cell(row=r, column=4).number_format = MONEY
        ws.cell(row=r, column=5).number_format = MONEY
        ws.cell(row=r, column=2).number_format = INT
    for c in range(1, 6):
        ws.cell(row=last, column=c).font = BOLD
        ws.cell(row=last, column=c).fill = TOTAL_FILL
    ws.freeze_panes = "A4"
    set_widths(ws, {"A": 30, "B": 10, "C": 16, "D": 16, "E": 16})

    # ----------------------------------------------------------------- Assumptions
    ws = wb.create_sheet("Assumptions")
    ws["A1"] = "Assumptions Register"
    ws["A1"].font = TITLE_FONT
    header_row(ws, 3, ["ID", "Assumption", "Value adopted", "Status"])
    assumptions = [
        ("A01", "Reporting period", "2026-01-01 to 2026-06-30 inclusive", "Given by brief"),
        ("A02", "Currency", "EUR; no FX translation", "Given by design"),
        ("A03", "Tax treatment", "VAT-exclusive (net)", "Assumed - confirm with Finance"),
        ("A04", "Categories", "8 canonical categories", "Defined in methodology"),
        ("A05", "Budget grain", "One budget per transaction line", "Design choice"),
        ("A06", "Variance sign", "Actual - budget; positive = adverse", "Definition"),
        ("A07", "Variance % guard", "Only when budget >= EUR 100", "Analytical judgement"),
        ("A08", "Review threshold", ">= EUR 1,000 and >= 10%", "Prioritisation rule"),
        ("A09", "Rounding", "2 decimal places", "Convention"),
        ("A10", "Duplicate rule", "Keep earliest txn_id", "Judgement"),
        ("A11", "Negative actual", "Credit note; include", "Judgement"),
        ("A12", "Negative budget", "Quarantine", "Judgement"),
        ("A13", "Outliers", "Flag; never auto-exclude", "Judgement"),
        ("A14", "Data source", "Synthetic educational data", "Given"),
    ]
    for i, row in enumerate(assumptions, start=4):
        for col, value in enumerate(row, start=1):
            ws.cell(row=i, column=col, value=value)
    style_body(ws, 4, 3 + len(assumptions), 4)
    for r in range(4, 4 + len(assumptions)):
        for c in range(1, 5):
            ws.cell(row=r, column=c).alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A4"
    set_widths(ws, {"A": 7, "B": 24, "C": 40, "D": 30})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"Wrote {OUT}")
    print(f"Sheets: {', '.join(wb.sheetnames)}")


if __name__ == "__main__":
    main()
