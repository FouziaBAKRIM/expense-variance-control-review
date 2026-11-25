# Screenshots — Capture Guide

> **Boundary.** Synthetic educational data only. Not an audit, assurance
> engagement, audit opinion or financial advice. Every image published from this
> folder must carry that statement in its caption.

---

## What is in this folder

| File | What it is | Status |
|---|---|---|
| `dashboard_mockup.html` | HTML/CSS design comp of page 1 | Source |
| `dashboard_mockup.png` | 1600 × 900 render of the comp | **Design mockup, not a Power BI render** |

The mockup exists to lock the layout, palette and copy **before** the `.pbix` is
authored. It is generated from hand-written HTML/CSS — not from Power BI — so it
must never be presented as a screenshot of a working report. Once the report is
built, replace it (or keep it clearly labelled as a design comp).

### Regenerate the mockup

From the repository root, on Windows:

```powershell
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$html = (Resolve-Path "power_bi\screenshots\dashboard_mockup.html").Path
$png  = (Join-Path (Get-Location) "power_bi\screenshots\dashboard_mockup.png")
$url  = "file:///" + ($html -replace '\\','/')

& $edge --headless=new --disable-gpu --hide-scrollbars --no-first-run `
  --force-device-scale-factor=1 --window-size=1600,900 `
  --screenshot="$png" "$url"
```

Chrome works identically; point `$edge` at
`C:\Program Files\Google\Chrome\Application\chrome.exe`.

---

## The screenshot set to aim for

| File | Page | What it must show |
|---|---|---|
| `01_executive_overview.png` | Executive Overview | Five KPIs, category bar, monthly + cumulative, top-5 lines, narrative |
| `02_variance_deep_dive.png` | Variance Deep Dive | Heatmap with the three big cells, decomposition tree expanded once, top-15 table |
| `03_data_quality_controls.png` | Data Quality & Controls | 17 / 13 / 37 / 10 cards, check-hit bar, disposition donut, control scorecard |
| `04_follow_up_actions.png` | Follow-Up & Actions | Three evidence-request cards, at-risk total, priority actions |
| `05_method_verification.png` *(optional)* | Method & Verification | Reconciliation bridge ending 0.00, six validation cards at 0 |

One hero image plus three supporting images is the right portfolio size. Five is
the maximum before a reviewer stops scrolling.

---

## Capture a real Power BI page

### Option A — Power BI Desktop (fastest)

1. **View → Page view → Actual size**; zoom to 100%.
2. Click an empty part of the canvas so no visual is selected (removes selection
   handles).
3. `Win + Shift + S` → rectangle → drag exactly around the canvas.
4. Save as PNG. Crop to the canvas; exclude the ribbon, field list and page tabs.

### Option B — Power BI Service (cleanest)

1. **Home → Publish** to a workspace.
2. Open the report in the browser and press **Full screen**.
3. Hide the filter pane. Set the browser viewport to 1920 × 1080 (DevTools device
   toolbar) so the 16:9 canvas fills the frame.
4. Capture with the browser screenshot command or the OS snipping tool.
5. Crop to the canvas.

### Option C — PDF then image

1. **File → Export → PDF**.
2. Convert the relevant PDF page to PNG at 150–200 dpi.
3. Crop. Best option if you also want a print-ready portfolio PDF.

---

## Capture checklist

- [ ] All slicers cleared (the numbers match `POWER_BI_BUILD_GUIDE.md` §7).
- [ ] No visual is selected; no selection borders.
- [ ] No scrollbars, tooltips or filter pane in frame.
- [ ] Canvas is exactly 16:9; no ribbon or browser chrome.
- [ ] Page 1 shows `+€59,380` and `€0.00 BALANCED`.
- [ ] Page 2 heatmap total is `+€59,380`.
- [ ] Page 3 shows `37` flagged and `39` hits — not `35`.
- [ ] Page 4 shows `€34,707` at risk and `0` conclusions.
- [ ] Boundary statement visible on every page.
- [ ] Grayscale check passed (signs and arrows still readable).
- [ ] PNG, not JPG; each file under ~500 KB.
- [ ] Consistent crop and border across the set.

---

## Post-processing

- Crop to the canvas; no browser chrome, ribbon or scrollbars.
- Export PNG for text sharpness.
- Keep a consistent 16:9 ratio across the set.
- Add a 1 px `#E3E8EF` border only if the image sits on a white page.
- Do **not** add fake browser frames or fake Power BI chrome.
- Do **not** Photoshop numbers. If a number is wrong, fix the model.

---

## Caption template

Use this under every published image:

> **Expense Variance & Control Review — [page name].** Synthetic educational
> dataset (454 lines, H1 2026). Built in Power BI. Not an audit, assurance
> engagement, audit opinion or financial advice.

For the mockup, the caption must say so:

> **Design mockup of the Executive Overview page.** HTML/CSS comp, not a Power BI
> render. The `.pbix` is authored locally; see
> [`../POWER_BI_BUILD_GUIDE.md`](../POWER_BI_BUILD_GUIDE.md).

---

## Alt text

Write alt text as if the reader cannot see colour:

> "Dashboard showing €2.09M actual against €2.03M budget, a +€59,380 adverse
> variance (+2.93%), Freight as the largest adverse category at +€30,829, and a
> €0.00 reconciliation."

Add it in Power BI (**Format → General → Alt text**) and in the README.

---

## Do not

- Do not label the mockup as a Power BI screenshot.
- Do not publish a screenshot with a filter applied unless the caption says so.
- Do not crop out the boundary statement.
- Do not use stock imagery or invented store photos.
- Do not imply the synthetic data is real client data.
