# Coach Questions — Model Answers

## H1 2026 Expense Review — Synthetic Educational Dataset

> **Boundary.** Educational exercise on synthetic data. These answers describe
> professional judgement; they are not an audit opinion or financial advice.

---

## 1. Is a variance automatically an error? What evidence would you request?

**No.** A variance is a *difference between actual and expected*, not a finding.
It tells you where to look, not what happened.

### Why a variance can be legitimate

| Driver | Example from this dataset |
|---|---|
| Timing | Annual software licence billed in May instead of spread over 12 months (TXN-2130, +€9,867) |
| Seasonality / volume | Freight rises with replenishment peaks; June is the largest month (+€21,340) |
| Price or rate | Carrier fuel surcharge or spot air-freight rate above the budgeted rate |
| Mix | More premium or expedited shipments than planned |
| One-off event | Emergency chiller replacement (TXN-2326, +€12,340) |
| Budget error | A budget set too low, or a cost moved between categories mid-year |
| Coding error | A capital item coded to maintenance, or a cost posted to the wrong category |
| Genuine overspend | A real decision to spend more than approved |
| Fraud | Possible, rare, and never assumed from a number alone |

### Evidence to request

Evidence should answer *what happened*, *who approved it*, and *whether the
amount is correct*. For a large adverse line:

1. **Purchase order or approval** — was the commitment authorised, by the right
   person, before the spend?
2. **Contract, rate card or quote** — is the price consistent with the agreed
   terms?
3. **Invoice and credit notes** — is the amount valid and complete?
4. **Goods-received note or delivery evidence** — did the goods or service
   actually arrive?
5. **Budget revision or forecast** — was the budget updated for a known change?
6. **General-ledger detail and coding policy** — is the category correct?
7. **A written explanation from the budget owner** — useful, but *not evidence*
   on its own.

### Worked example

TXN-2166: budget €3,865, actual €18,943, variance +€15,077 (+390%). The variance
is a fact. The *cause* is unknown. Possible causes include an approved emergency
shipment, a rate error, a volume spike, or a duplicate. The evidence request is
the carrier invoice, shipment approval, rate card and proof of delivery. Until
those arrive, the correct statement is: **"unexplained, evidence requested"** —
not "overspend" and not "error".

### The discipline

> A variance is a question, not an answer. Management explanation is a lead, not
> evidence.

---

## 2. What is the difference between control design and evidence it operated?

**Design** is whether the control exists and is capable of preventing or detecting
the risk. **Operating effectiveness** is whether it actually ran, consistently,
across the period and the population.

| | Control design | Operating effectiveness |
|---|---|---|
| Question | Is there a control on paper? | Did it work in practice? |
| Evidence | Policy, approval matrix, system configuration, SOP, delegated limits | Timestamps, logs, signed reviews, exception reports, sample test results |
| Example | "A duplicate-invoice check runs before payment." | Payment log shows the duplicate was blocked; AP reviewer signed the exception report |
| Failure mode | The control is missing or too weak | The control exists but was bypassed, not performed, or not evidenced |

### Why the distinction matters

A company can have a perfect approval policy and still pay an invoice without
approval. A control that is well designed but not operated gives false comfort. A
control that is poorly designed but happens to operate can look fine on a small
sample.

### What this dataset can test

| Area | Design | Operation |
|---|---|---|
| Duplicate invoice | Review the policy | **No** — needs payment and AP logs |
| Approval limits | Review the matrix | **No** — no PO or approval field |
| Category coding | Review the master data | **Partly** — 6 labels corrected, 2 descriptions blank |
| Budget coverage | Review the budget | **Partly** — 3 unbudgeted lines identified |
| Capitalisation | Review the policy | **No** — needs asset register |
| Cut-off | Review the close checklist | **Partly** — 2 out-of-period rows found |

### How to test operation in practice

1. Define the population (all payments above the approval threshold in H1).
2. Select a sample — random, plus all high-risk items (duplicates, new suppliers,
   round amounts, weekend postings).
3. Inspect the evidence for each: approval before commitment, invoice, GRN,
   payment.
4. Record exceptions and their value.
5. Conclude on the *control*, not just the sample: "the control operated for 47 of
   50 items tested; three lacked approval before commitment."

### The trap

Do not say "the control is effective" because you read the policy. That is a
design conclusion. Do not say "the control failed" because you found one
exception. That is a sample observation. State which one you tested.

---

## 3. How do you communicate a variance without making an unsupported accusation?

Use a fixed structure that separates **fact**, **possible cause**, **evidence
requested** and **conclusion status**.

### The four-part structure

1. **Observation** — what the data shows, with amounts and dates.
2. **Possible causes** — plural, neutral, and not ranked as if one is proven.
3. **Evidence requested** — the specific documents that would resolve it.
4. **Conclusion pending** — an explicit statement that no conclusion is drawn yet.

### Bad versus good wording

| Avoid | Use instead |
|---|---|
| "The logistics team overspent by €15k." | "Freight was €15,077 above budget on one line; the driver is not yet evidenced." |
| "This looks like fraud." | "The amount is unexplained; we have requested the invoice, approval and rate card." |
| "The chiller was wrongly capitalised." | "The description says 'replacement'; we have asked whether the capitalisation policy applies." |
| "Payroll savings of €26k." | "Payroll is €26,110 below budget; we have asked whether this reflects vacancies or timing." |
| "Duplicate payment." | "Two identical postings exist; we have asked whether both were paid." |

### Worked example

> **Observation:** TXN-2166, dated 2026-06-16, records €18,942.63 of expedited air
> freight against a budget of €3,865.26, a variance of +€15,077.37 (+390%).
> **Possible causes:** an approved emergency shipment, a rate or mode change, a
> volume spike, or a recording error. **Evidence requested:** carrier invoice,
> shipment approval, contracted rate card, proof of delivery. **Status:** the
> driver is not yet evidenced; no conclusion is drawn.

### Language rules

- Describe the **transaction**, not the person.
- Use "unexplained", "not yet evidenced", "requires confirmation".
- Avoid "fraud", "waste", "incompetence", "overspend by [team]".
- Quantify precisely; vague language invites dispute.
- Separate the **variance** (a fact) from the **cause** (a hypothesis).
- State the boundary: "this is an analytical review, not an audit opinion."

### Why this matters commercially

An unsupported accusation damages trust and can be wrong. A neutral, evidence-led
question gets answered. The goal is to help management fix the process, not to win
an argument.

---

## One-sentence answers

1. **No** — a variance is a signal; request the PO, contract, invoice, delivery
   evidence and coding policy, and treat management's explanation as a lead.
2. **Design** is whether the control exists on paper; **operating effectiveness**
   is whether logs, approvals and samples prove it ran during the period.
3. **Observation → possible causes → evidence requested → conclusion pending**,
   with neutral language and no person blamed.
