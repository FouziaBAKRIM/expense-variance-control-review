# Budget-versus-Actual Summary and Variance Commentary

## H1 2026 Expense Review — Synthetic Educational Dataset

> **Boundary.** Synthetic data; educational exercise. Not an audit, assurance
> engagement or financial advice. Variances are signals for follow-up, not
> findings of error or fraud.

| | |
|---|---|
| Version | 1.0 |
| Date | 2026-11-22 |
| Basis | Clean ledger: 442 rows, `included = TRUE` |
| Currency | EUR, VAT-exclusive (assumed) |
| Sign convention | **Positive variance = adverse** (actual above budget) |

---

## 1. Definitions

```
variance_eur = actual_amount − budget
variance_pct = (variance_eur / budget) × 100    only when budget ≥ €100
```

`variance_pct` is blank where the budget is zero (unbudgeted), below €100 (tiny
budget) or negative (quarantined). Positive = adverse; negative = favourable.

---

## 2. Headline

| Measure | EUR |
|---|---:|
| Budget | 2,027,057.54 |
| Actual | 2,086,437.42 |
| **Variance** | **+59,379.88** |
| **Variance %** | **+2.93%** |

Spend is **€59.4k (2.9%) above budget** for the half-year. The overspend is
concentrated in three categories and three one-off items; it is partly offset by
payroll and by credit notes in utilities.

---

## 3. By category

| Category | Txns | Budget | Actual | Variance | Var % | Direction |
|---|---:|---:|---:|---:|---:|---|
| Freight & Delivery | 45 | 184,255.56 | 215,084.80 | +30,829.24 | +16.73% | Adverse |
| Maintenance & Repairs | 67 | 156,463.29 | 182,238.82 | +25,775.53 | +16.47% | Adverse |
| Software & Cloud | 46 | 136,628.40 | 157,817.11 | +21,188.71 | +15.51% | Adverse |
| Professional Services | 33 | 150,614.20 | 165,957.96 | +15,343.76 | +10.19% | Adverse |
| Office & Supplies | 84 | 71,945.14 | 78,967.82 | +7,022.68 | +9.76% | Adverse |
| Digital Ads & Promo | 14 | 55,088.23 | 52,490.58 | −2,597.65 | −4.72% | Favourable |
| Utilities & Rent | 67 | 427,608.28 | 415,536.36 | −12,071.92 | −2.82% | Favourable |
| Payroll & Overtime | 86 | 844,454.44 | 818,343.97 | −26,110.47 | −3.09% | Favourable |
| **Total** | **442** | **2,027,057.54** | **2,086,437.42** | **+59,379.88** | **+2.93%** | **Adverse** |

**Largest adverse category:** Freight & Delivery, +€30,829 (+16.7%).
**Largest favourable category:** Payroll & Overtime, −€26,110 (−3.1%).

### Commentary

- **Freight** is adverse in five of six months and accelerates sharply in June
  (+€21,340, +44.6%). One expedited air-freight line (TXN-2166, +€15,077)
  accounts for most of the June spike; even excluding that line and its budget,
  June freight is +€6,263 on a €43,938 budget (+14.3%). This looks like a
  rate/volume issue plus one operational event, not a single coding error.
- **Maintenance** is driven by January (+€14,081, +61.7%), where the emergency
  chiller replacement (TXN-2326, +€12,340) sits. Excluding that line, January
  maintenance is +€1,740. The remaining +€13.4k is spread across the half-year.
- **Software** is driven by May (+€13,754, +43.5%), where an annual licence was
  billed in one month (TXN-2130, +€9,867). This is a timing profile question:
  the cost may be valid but should be accrued or budgeted across the year.
- **Professional Services** is broad-based (+€15,344, +10.2%) with no single
  dominant line; the largest is recruitment fees at +€1,193. This needs a
  category-level explanation rather than one invoice.
- **Office & Supplies** is almost entirely unbudgeted spend: the three unbudgeted
  lines total €10,422, while the category is only +€7,023 net because other
  lines were slightly favourable. The issue is budget coverage, not price.
- **Digital Ads** is favourable (−€2,598, −4.7%) and small in absolute terms.
- **Utilities** looks favourable (−€12,072), but part of that is **credit-note
  driven**: −€2,417 and −€1,745 of utilities credits sit in the category. Add
  those back and utilities is still favourable, but only −€7,910 (−1.9%). The
  headline saving is therefore about one-third credit note, two-thirds other
  factors. Do not read it as lower consumption without evidence.
- **Payroll** is the largest favourable category (−€26,110, −3.1%) and is
  consistently below budget every month. That pattern is more consistent with
  vacancies, timing or under-recruitment than with a genuine saving; it needs a
  headcount/vacancy explanation before being treated as a benefit.

---

## 4. By month

| Month | Txns | Budget | Actual | Variance | Var % |
|---|---:|---:|---:|---:|---:|
| 2026-01 | 70 | 307,107.47 | 325,485.51 | +18,378.04 | +5.98% |
| 2026-02 | 76 | 352,875.59 | 356,185.52 | +3,309.93 | +0.94% |
| 2026-03 | 71 | 311,717.82 | 309,809.76 | −1,908.06 | −0.61% |
| 2026-04 | 64 | 347,575.79 | 352,971.10 | +5,395.31 | +1.55% |
| 2026-05 | 71 | 308,654.02 | 325,838.81 | +17,184.79 | +5.57% |
| 2026-06 | 90 | 399,126.85 | 416,146.72 | +17,019.87 | +4.26% |
| **Total** | **442** | **2,027,057.54** | **2,086,437.42** | **+59,379.88** | **+2.93%** |

### Commentary

- **January** (+€18.4k) is the chiller month: maintenance alone contributes
  +€14.1k, with freight adding +€3.7k.
- **February** (+€3.3k) is close to budget and broadly neutral.
- **March** (−€1.9k) is the only favourable month, and only because a €2.4k
  utilities credit note plus lower payroll offset adverse freight and
  professional services.
- **April** (+€5.4k) is a freight month (+€3.6k) with no other large driver.
- **May** (+€17.2k) is the software renewal month (+€13.8k), with professional
  services and office supplies adding smaller amounts.
- **June** (+€17.0k) is the freight month (+€21.3k), partly offset by utilities
  (−€8.2k) and payroll.

Three months (Jan, May, Jun) carry €52.6k of the €59.4k total. Each is associated
with a different one-off item, which is why a single "monthly overspend" narrative
would be misleading.

---

## 5. Month × category highlights

### Largest adverse cells

| Month | Category | Budget | Actual | Variance | Var % |
|---|---|---:|---:|---:|---:|
| 2026-06 | Freight & Delivery | 47,803.64 | 69,143.81 | +21,340.17 | +44.64% |
| 2026-01 | Maintenance & Repairs | 22,805.86 | 36,886.60 | +14,080.74 | +61.74% |
| 2026-05 | Software & Cloud | 31,637.31 | 45,391.80 | +13,754.49 | +43.48% |
| 2026-01 | Freight & Delivery | 28,120.08 | 31,785.65 | +3,665.57 | +13.04% |
| 2026-04 | Freight & Delivery | 21,839.17 | 25,464.32 | +3,625.15 | +16.60% |
| 2026-02 | Freight & Delivery | 23,603.03 | 27,099.54 | +3,496.51 | +14.81% |
| 2026-03 | Freight & Delivery | 26,296.52 | 29,670.95 | +3,374.43 | +12.83% |
| 2026-05 | Professional Services | 34,802.37 | 38,112.23 | +3,309.86 | +9.51% |

### Largest favourable cells

| Month | Category | Budget | Actual | Variance | Var % |
|---|---|---:|---:|---:|---:|
| 2026-03 | Utilities & Rent | 37,002.79 | 26,781.82 | −10,220.97 | −27.62% |
| 2026-06 | Utilities & Rent | 69,756.30 | 61,514.35 | −8,241.95 | −11.82% |
| 2026-01 | Payroll & Overtime | 149,698.93 | 142,179.43 | −7,519.50 | −5.02% |
| 2026-02 | Payroll & Overtime | 135,909.84 | 130,267.02 | −5,642.82 | −4.15% |
| 2026-04 | Payroll & Overtime | 169,827.45 | 164,671.65 | −5,155.80 | −3.04% |
| 2026-05 | Freight & Delivery | 36,593.12 | 31,920.53 | −4,672.59 | −12.77% |

The March and June utilities cells are partly credit-note effects: March contains
a −€2,417 credit (excluding it, the cell is −€7,804, −21.1%) and June contains
−€1,745 (excluding it, −€6,497, −9.3%). They remain favourable, but smaller than
the headline. The May freight cell is the one month where freight was below
budget.

---

## 6. Largest line items

### Adverse

| Transaction | Date | Category | Budget | Actual | Variance | Var % |
|---|---|---|---|---:|---:|---:|---:|
| TXN-2166 | 2026-06-16 | Freight & Delivery | 3,865.26 | 18,942.63 | +15,077.37 | +390.07% |
| TXN-2326 | 2026-01-12 | Maintenance & Repairs | 2,774.89 | 15,115.25 | +12,340.36 | +444.72% |
| TXN-2130 | 2026-05-13 | Software & Cloud | 3,847.19 | 13,713.94 | +9,866.75 | +256.47% |
| TXN-2040 | 2026-05-07 | Office & Supplies | 0.00 | 3,705.08 | +3,705.08 | n/a |
| TXN-2336 | 2026-05-16 | Software & Cloud | 0.00 | 3,366.52 | +3,366.52 | n/a |
| TXN-2248 | 2026-01-08 | Office & Supplies | 0.00 | 3,350.01 | +3,350.01 | n/a |
| TXN-2194 | 2026-03-04 | Office & Supplies | 1.00 | 1,668.60 | +1,667.60 | n/a |
| TXN-2235 | 2026-06-01 | Freight & Delivery | 6,292.06 | 7,544.87 | +1,252.81 | +19.91% |
| TXN-2221 | 2026-06-06 | Professional Services | 6,729.33 | 7,922.47 | +1,193.14 | +17.73% |
| TXN-2021 | 2026-06-10 | Payroll & Overtime | 1.00 | 1,145.39 | +1,144.39 | n/a |

### Favourable

| Transaction | Date | Category | Budget | Actual | Variance | Var % |
|---|---|---|---|---:|---:|---:|---:|
| TXN-2108 | 2026-03-04 | Utilities & Rent | 8,129.18 | −2,416.53 | −10,545.71 | −129.73% |
| TXN-2142 | 2026-06-02 | Utilities & Rent | 8,264.89 | −1,745.37 | −10,010.26 | −121.12% |
| TXN-2368 | 2026-05-27 | Freight & Delivery | 5,353.70 | −481.48 | −5,835.18 | −108.99% |
| TXN-2346 | 2026-05-18 | Freight & Delivery | 2,490.03 | −650.31 | −3,140.34 | −126.12% |
| TXN-2231 | 2026-06-15 | Payroll & Overtime | 13,613.62 | 11,879.87 | −1,733.75 | −12.74% |
| TXN-2152 | 2026-02-17 | Payroll & Overtime | 11,753.93 | 10,224.73 | −1,529.20 | −13.01% |
| TXN-2390 | 2026-01-14 | Payroll & Overtime | 9,450.57 | 7,954.96 | −1,495.61 | −15.83% |
| TXN-2414 | 2026-03-18 | Payroll & Overtime | 7,967.75 | 6,504.20 | −1,463.55 | −18.37% |

The four largest favourable lines are all credit notes. They are legitimate
accounting entries but should be matched to their original invoices and checked
for period allocation before being treated as savings.

---

## 7. What the variance does and does not tell us

**It does tell us**

- Where spend exceeded budget, by how much, and when.
- Which categories and months carry the overspend.
- Which single lines dominate the total.
- Where data quality affects the numbers.

**It does not tell us**

- Whether the spend was necessary, approved or correctly coded.
- Whether price, volume or mix caused the variance (no quantity or unit price).
- Whether a credit note relates to the current or a prior period.
- Whether payroll underspend is a saving or a vacancy.
- Whether any item is an error or fraud.

Those questions require evidence and are addressed in
`docs/follow_up_items.md` and `docs/risk_control_matrix.md`.
