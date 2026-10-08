# DATA_CARD — `synthetic_ad_spend.csv` (STORY-101)

Path-C synthetic multi-channel marketing panel for portfolio / recovery tests.

| Field | Value |
| --- | --- |
| Generator | `python -m src.data.generator` (`seed=42`) |
| Transforms | DGP calls `geometric_adstock` / `hill_saturation` from `src.models.transformations` (STORY-102) |
| Rows | 2,912 = 728 days × 4 channels |
| Grain | **Channel-day only** (`meta`, `google`, `tiktok`, `tv`) |
| Locked artifact | Committed CSV matches seed=42 **after** integer post-processing |

## Columns

| Column | Type | Meaning |
| --- | --- | --- |
| `date` | ISO date | Calendar day |
| `channel` | string | Channel ID |
| `spend` | float USD | Media spend (currency; may be fractional) |
| `impressions` | int ≥ 0 | Rounded delivery counts |
| `clicks` | int ≥ 0 | Rounded click counts |
| `baseline_sales` | int ≥ 0 | **Site-wide daily order/unit counts** (KPI) |

Integer columns are produced by continuous DGP → `round` → clip ≥ 0 → `int64`.

## Long-format rule for `baseline_sales`

`baseline_sales` is the **same site-wide daily KPI repeated on every channel row** for that date.

- Recover the series with `groupby("date")["baseline_sales"].first()` (or `.mean()`).
- **Do not sum across channels** — that would multiply the KPI by 4.

## Real-life mapping

| Synthetic column | Typical source |
| --- | --- |
| `spend`, `impressions`, `clicks` | Partner / ad-platform exports |
| `baseline_sales` | Site / CRM daily orders (units) |
| Join key | `date` (+ `channel` for media only) |

## KPI decision (locked for STORY-101)

- `baseline_sales` = **units / orders only** (integer counts).
- **No `revenue` column** in this story (keeps the STORY-101 column DoD).
- USD revenue can be the client KPI in a **later story / ETL mapping** without changing this schema.

## Out of scope (do not reopen STORY-101)

- Campaign / ad-set / creative grain
- Funnel stages (brand vs retargeting, prospecting, etc.)
- Multiple KPIs or revenue alongside units

Those are planned later; this file stays channel-level only.
