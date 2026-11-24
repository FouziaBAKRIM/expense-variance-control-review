# Risk-and-Control Matrix

## H1 2026 Expense Review — Synthetic Educational Dataset

> **Boundary.** Synthetic data; educational exercise. This matrix is a design and
> evidence plan, not an audit opinion. "Result" describes what the synthetic
> ledger can and cannot show; it is not a conclusion on management performance.

| | |
|---|---|
| Version | 1.0 |
| Date | 2026-11-22 |
| Scope | Expense recording, approval, coding, budgeting and cut-off |
| Evidence base | 454 synthetic transactions, H1 2026 |

---

## How to read the matrix

- **Risk** — what could go wrong.
- **Possible cause** — plausible drivers, stated without asserting one.
- **Proposed control** — the control that should prevent or detect the risk.
- **Evidence needed** — what a reviewer would inspect.
- **Test / question** — the specific procedure or question.
- **Result in this dataset** — what the ledger shows, and whether the control can
  be tested with the data available.

---

## Matrix

| # | Risk | Possible cause | Proposed control | Evidence needed | Test / question | Result in this dataset |
|---|---|---|---|---|---|---|
| 1 | Supplier paid twice / invoice recorded twice | Manual keying, re-submitted invoice, no duplicate check | Duplicate-invoice check before payment; unique invoice reference; three-way match | Invoice number, supplier, amount, payment record, bank statement | Are duplicate invoice numbers or identical amounts flagged before payment? | **Recording test possible:** 2 exact duplicate pairs found (€7,289.32). **Payment test not possible:** no payment or bank records. |
| 2 | Purchase without approval | Limit exceeded, emergency purchase, approval bypassed | Delegated approval matrix; PO required above threshold; system-enforced limits | Purchase order, approval record, workflow log, invoice | Was approval obtained *before* the purchase, and by the right authority? | **Not testable:** no PO or approval field. The three unbudgeted lines (€10,421.61) are a prompt for the question, not proof of a bypass. |
| 3 | Incorrect expense coding | Free-text categories, unclear taxonomy, manual coding | Defined category list; mandatory pick-list; periodic coding review | Ledger description, coding policy, category master | Is the category consistent with the policy and the description? | **Partly testable:** 6 non-canonical labels corrected, 0 unmapped after mapping. Two blank descriptions (€19,040.17) cannot be coded from the data. |
| 4 | Unbudgeted spend | No budget line, mid-year initiative, budget moved elsewhere | Budget coverage check before commitment; supplementary budget process | Budget approval, revised budget, PO | Was a budget approved, and if not, who authorised the spend? | **Testable:** 3 unbudgeted lines, €10,421.61 (TXN-2040, TXN-2248, TXN-2336). Indicates a budget-coverage gap. |
| 5 | Capital expenditure treated as repairs | "Replacement" coded as maintenance; no capitalisation review | Capitalisation policy; capex threshold; asset-register check | Work order, asset register, capitalisation policy, approval | Is the chiller replacement capital or revenue, and who decided? | **Not testable from the ledger alone:** TXN-2326 (€15,115.25) is the candidate. Needs asset-register and policy evidence. |
| 6 | Freight cost overrun / rate leakage | Spot rates, fuel surcharge, expedited mode, volume spike | Contracted rate card; shipment approval; monthly freight review | Carrier contract, rate card, shipment log, invoice | Was the invoiced rate consistent with the contract, and was expedited mode approved? | **Testable at total level:** freight +€30,829 (+16.7%); June +44.6%; one line +€15,077. Rate-card evidence required. |
| 7 | Credit notes unmatched or mis-periodised | Credit received without original invoice; prior-period credit | Credit-note matching; supplier statement reconciliation; period allocation rule | Credit note, original invoice, supplier statement, accrual schedule | Is each credit matched to an original invoice and allocated to the right period? | **Not testable:** 4 credit notes (€5,293.69) but no invoice reference field. Match to supplier statements required. |
| 8 | Period cut-off error | Late posting, accrual missed, manual journal | Close checklist; date validation; accrual and prepayment review | Ledger date, GRN date, accrual schedule, close checklist | Are there transactions dated outside the period, and were they accrued in the right month? | **Testable:** 2 out-of-period rows (€23,288.60): 2025-12-28 and 2026-07-03. Suggests a cut-off control gap. |
| 9 | Poor data quality in reporting | Manual uploads, free-text fields, no validation | Upload validation rules; mandatory fields; DQ exception review | DQ log, upload specification, review sign-off | Are exceptions identified, reviewed and resolved before reporting? | **Testable:** 35 defects, 10 quarantined, 2 out-of-period, 18 flagged. A DQ log exists in this project; whether one exists in the business is unknown. |

---

## Design versus operating effectiveness

This distinction matters more than the matrix itself.

| Question | What it means | Example here |
|---|---|---|
| **Is the control designed well?** | Does a policy, limit, system rule or checklist exist on paper? | "A duplicate-invoice check exists before payment." |
| **Did the control operate?** | Is there evidence it actually ran for the period and the population? | Payment log showing the duplicate was blocked, or a reviewer's sign-off. |

A well-designed control can operate badly. A badly designed control can look fine
on a small sample. The ledger can test **recording** and **detect anomalies**; it
cannot prove **operation** without logs, approvals and payment records.

| Control area | Design testable? | Operating effectiveness testable? |
|---|---|---|
| Duplicate invoice | Yes, by policy review | No — needs payment and AP logs |
| Approval limits | Yes, by policy review | No — needs PO and approval records |
| Category coding | Yes, by master-data review | Partly — 6 labels corrected, 2 blanks |
| Budget coverage | Yes, by budget review | Partly — 3 unbudgeted lines identified |
| Capitalisation | Yes, by policy review | No — needs asset register |
| Freight rates | Yes, by contract review | No — needs shipment and invoice matching |
| Credit notes | Yes, by policy review | No — needs supplier statements |
| Cut-off | Yes, by close checklist | Partly — 2 out-of-period rows found |
| DQ review | Yes, by procedure review | Partly — 35 defects identified in this project |

---

## Priority actions

1. **Payment-match the two duplicate pairs** (€7,289.32). Highest immediate value;
   determines whether this is a recording issue or a cash issue.
2. **Obtain the freight rate card and shipment approval** for TXN-2166
   (€15,077.37). Confirm rate and mode before treating the variance as a cost
   problem.
3. **Confirm the capital/revenue treatment** of the chiller (TXN-2326,
   €12,340.36) against the asset register and policy.
4. **Close the budget-coverage gap** for the three unbudgeted lines
   (€10,421.61) and the two tiny-budget lines.
5. **Add master-data validation** at upload: canonical category list, mandatory
   description, date format, non-negative budget.
6. **Add a period close checklist** and a pre-close date scan; two out-of-period
   items (€23,288.60) were only found by analysis.
7. **Introduce credit-note matching** to original invoices; four credits
   (€5,293.69) cannot be matched in the current data.
8. **Review payroll underspend** (−€26,110) for vacancy/timing effects before it
   is presented as a saving.

---

## What this matrix is not

It is not an assertion that these controls are absent or failing. It is a
structured list of the questions a reviewer would ask, the evidence that would
answer them, and an honest note on which questions this dataset can and cannot
answer.
