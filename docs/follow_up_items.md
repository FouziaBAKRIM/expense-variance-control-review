# Follow-Up Items

## H1 2026 Expense Review — Synthetic Educational Dataset

> **Boundary.** Synthetic data; educational exercise. These are requests for
> evidence, not allegations. No item below is a finding of error, fraud or
> misconduct. Each conclusion remains open until evidence is obtained.

| | |
|---|---|
| Version | 1.1 |
| Date | 2026-11-25 |
| Variance threshold | `abs(variance) ≥ €1,000` **and** `abs(variance %) ≥ 10%` (19 included lines) |
| Candidate screen | broader: `abs(variance) ≥ €1,000` **or** unbudgeted **or** credit note **or** outlier (25 rows in `follow_up_candidates.csv`) |
| Selection | three items chosen by judgement to cover different risk types |

---

## Selection summary

| # | Item | Transaction(s) | Amount | Var % | Why selected |
|---|---|---|---:|---:|---|
| 1 | Expedited air freight | TXN-2166 | +15,077.37 | +390.07% | Largest single adverse line; June freight +44.6% |
| 2 | Emergency chiller replacement | TXN-2326 | +12,340.36 | +444.72% | Second-largest adverse line; possible capital/revenue question |
| 3 | Duplicate invoice pair | TXN-2364 / TXN-2451 (and TXN-2348 / TXN-2452) | 7,289.32 | — | Exact business-key duplicate; payment status unknown |

The three items were chosen to cover three different risk types: a large
operational variance, a classification/approval question, and a control failure
in recording. They are not simply the three largest numbers.

Note that item 3 (the duplicate pair) comes from the duplicate-invoice check, not
from the variance candidate screen: the later copies are quarantined and the
originals carry only a small variance. The two-screen logic is documented in
`docs/methodology.md` §13.

---

## Item 1 — Expedited air freight

| | |
|---|---|
| Transaction | TXN-2166 |
| Date | 2026-06-16 |
| Department | Store Operations |
| Category | Freight & Delivery |
| Description | Expedited air freight — unplanned replenishment |
| Budget | €3,865.26 |
| Actual | €18,942.63 |
| Variance | **+€15,077.37 (+390.07%)** |
| Flags | `OUTLIER` |

### Observation

A single freight line is 4.9× its budget and accounts for 71% of the June freight
overspend (+€21,340). Freight is adverse in five of six months, so the underlying
category is already under pressure; this line turns a trend into a spike.

### Why it needs checking

- The size and the word "expedited" suggest a discretionary operational decision
  that may require approval above normal limits.
- The variance could be caused by volume, air-freight rates, a one-off service
  failure, or a coding error. The data cannot distinguish these.
- June freight remains +€6,263 on a €43,938 budget (+14.3%) even after removing
  this line and its budget, so the answer may reveal a broader rate issue.

### Evidence required

1. Carrier invoice and shipment/booking reference.
2. The purchase order or approval for expedited air freight.
3. Contracted rate card or spot quote, and the mode used (air vs road).
4. Reason for the shipment (stock-out, promotion, supplier delay).
5. Proof of delivery and goods-received note.
6. Any budget revision or pre-approval for the overspend.

### What is not being concluded

This is **not** an assertion that the shipment was unnecessary, overpriced or
improperly approved. A genuine stock-out can justify air freight. The question is
whether the decision was authorised and priced as expected.

### Test / question

> Was the expedited shipment approved before dispatch, and was the invoiced amount
> consistent with the contracted or quoted rate?

### Next step

Request the six evidence items from Logistics & Supply and compare the invoice to
the rate card. If the rate is correct, quantify the volume effect and consider a
freight budget review.

---

## Item 2 — Emergency chiller replacement

| | |
|---|---|
| Transaction | TXN-2326 |
| Date | 2026-01-12 |
| Department | Logistics & Supply |
| Category | Maintenance & Repairs |
| Description | Emergency chiller replacement — store 04 |
| Budget | €2,774.89 |
| Actual | €15,115.25 |
| Variance | **+€12,340.36 (+444.72%)** |
| Flags | `OUTLIER` |

### Observation

A single maintenance line is 5.4× budget and drives 88% of the January
maintenance overspend (+€14,081). It is also the second-largest adverse line in
the half-year.

### Why it needs checking

- "Replacement" may be capital expenditure rather than a repair. If so, it should
  not sit in an operating maintenance budget, and the variance is a classification
  issue as much as a cost issue.
- Emergency purchases often bypass normal competitive quoting and approval.
- The amount is large enough that its treatment affects the maintenance category
  and potentially the capital budget.

### Evidence required

1. Work order and fault report.
2. Supplier quote, invoice and proof of payment.
3. Approval record and delegated authority limit.
4. Asset register entry and capitalisation policy.
5. Whether the unit was replaced or repaired, and the expected useful life.
6. Any insurance recovery or warranty claim.

### What is not being concluded

This is **not** a claim that the item was misclassified or unnecessary. Emergency
replacement of a failed chiller can be both legitimate and urgent. The question is
whether it was approved and recorded in the right category.

### Test / question

> Was the chiller replaced or repaired, who approved the spend, and does the
> capitalisation policy require it to be treated as capital expenditure?

### Next step

Request the work order, approval and asset-register evidence. If capital, propose
a reclassification and a budget-transfer entry; if revenue, confirm the emergency
approval route.

---

## Item 3 — Duplicate invoice pair

| | |
|---|---|
| Transactions | TXN-2364 (original) / TXN-2451 (duplicate); TXN-2348 / TXN-2452 |
| Dates | 2026-05-03 and 2026-01-16 |
| Departments | Logistics & Supply; IT & Systems |
| Categories | Payroll & Overtime; Office & Supplies |
| Amounts | €6,394.95 and €894.37 |
| Total at risk | **€7,289.32** |
| Flags | `EXACT_DUPLICATE` |

### Observation

Two pairs of rows share the same date, department, category, description, budget
and actual amount, with different transaction IDs. Both later copies were
quarantined, so the clean ledger includes one of each. The recording duplicate is
confirmed; whether the payment was also duplicated is unknown.

### Why it needs checking

- A duplicate posting can become a duplicate payment if the payment run is not
  matched to invoices.
- Exact duplicates with the same date and amount are unusual for genuine separate
  transactions, but not impossible (for example, two identical uniform orders).
- The control question is whether a duplicate-invoice check exists and whether it
  operated during the period.

### Evidence required

1. Invoice image or PDF for each transaction.
2. Payment record and bank statement line for each.
3. Supplier statement for the period.
4. Goods-received note or delivery evidence for the second item.
5. Accounts-payable posting log and approval trail.

### What is not being concluded

This is **not** an allegation of double payment. It may be a single invoice
recorded twice and paid once, or two genuine identical purchases. The evidence
decides which.

### Test / question

> Were both transactions paid, and if so, do two separate invoices and two
> separate deliveries exist?

### Next step

Match each pair to the payment run. If only one payment exists, remove the
duplicate from the ledger and confirm the correction. If two payments exist,
obtain the second invoice and delivery evidence, and test the duplicate-invoice
control.

---

## Watch list (not one of the three)

These items are below the selection cut or are better handled as a group. They
remain in the ledger and should be reviewed if capacity allows.

| Item | Transactions | Amount | Why watch |
|---|---|---:|---|
| Utilities credit notes | TXN-2108, TXN-2142 | 4,161.90 credit | Large favourable swing; match to original invoices and period |
| Freight credit notes | TXN-2368, TXN-2346 | 1,131.79 credit | Same |
| Unbudgeted office spend | TXN-2040, TXN-2248 | 7,055.09 | No budget cover; budget process question |
| Unbudgeted software | TXN-2336 | 3,366.52 | Same |
| Annual software licence | TXN-2130 | +9,866.75 | Timing/accrual question; may be valid but badly phased |
| Near duplicates | TXN-2009/2453, TXN-2023/2454 | 7,229.70 | Two identical amounts one to two days apart; confirm deliveries |

---

## Communication standard

Every item above is written as **observation → possible causes → evidence
requested → conclusion pending**. None uses the words "fraud", "waste" or
"overspend by [person]". That is deliberate: the data supports a question, not an
accusation.
