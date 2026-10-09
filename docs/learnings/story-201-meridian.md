# STORY-201 learnings — Meridian Bayesian MMM spike

Spike status: **done** (script DoD on national weekly Path-C). Working history lived on
`cursor/story-201-meridian-702b`; lands on `sprint-1-core-data-engine`.

## What we learned

### Meridian is a local pip library

`google-meridian` is **not** a Google Cloud API and needs **no API key**. It installs into
conda env `mmt-mmm` via pip (`environment.yml` pins `google-meridian==2.1.0`) and runs MCMC
on your machine (TensorFlow / TFP stack — fat install, slow on CPU).

Tested combo: `google-meridian==2.1.0` + `arviz` 0.19.x + `matplotlib` 3.10.x
(`matplotlib<3.11` — arviz 0.19 breaks on 3.11+) + `pymc` 6.x.

### Smoke vs full

| Mode | Purpose | R-hat |
| --- | --- | --- |
| `--mode smoke` | Prove the training loop; short chains | Peek only; prints `SMOKE_RHAT_WARN` if high; exit 0 unless `--fail-on-rhat` |
| `--mode full` | DoD artifacts | Hard-fail if max core R-hat ≥ 1.05 |

Lean fuller defaults (laptop CPU): 4 chains, adapt 500 / burnin 200 / keep 400.

### R-hat

R-hat ≈ “did independent chains land in the same place?” Fuller spike on weekly national
data passed with max core R-hat ≈ 1.005 (&lt; 1.05). Smoke can look “bad” only because chains
are intentionally short — that is expected, not a model bug.

### National weekly adapter

`src/models/meridian_data.py` maps post-QA long channel-day Parquet → Meridian national
`InputData`:

- KPI = site-wide `baseline_sales` (`groupby(date).first()`, then **week sum**)
- Media = `impressions`; ROI denominator = `spend`
- `revenue_per_kpi = 1.0` so incremental outcome ≈ incremental units (iROAS ≈ units per $)
- Default `freq="W"` (week ending Sunday); `--freq D` is much slower

### Warnings that are normal

- `SMOKE_RHAT_WARN` on short smoke chains
- Fat TensorFlow / TFP import noise and long CPU sample times
- Parameter-recovery **mismatch is status only** — `dod.directional_recovery: false` does
  **not** exit non-zero for this spike

---

## Open issue — rank recovery vs Path-C is inconsistent

**Do not treat this spike as “we recovered channel order.”**

| Source | Channel order (strong → weak) |
| --- | --- |
| Meridian iROAS (posterior mean) | **meta → tiktok → tv → google** |
| Path-C contribution / `media_beta` | **tv → google → meta → tiktok** |

- Spearman rank correlation (iROAS vs Path-C contribution): **≈ −0.6**
- Recorded in `reports/metrics.json` (`recovery_spearman`, `dod.directional_recovery: false`)
  and `reports/parameter_recovery.md`
- **Not** a hard fail for STORY-201 DoD (convergence + artifacts were the gate)

### Likely investigation axes (post-POC)

1. **Media scaling** — Meridian media = impressions; DGP strength is planted in `media_beta` ×
   geometric adstock × Hill on a different scale
2. **Priors** — Meridian ROI / log-normal media priors vs Path-C planted magnitudes
3. **Weekly aggregation** — summing daily units / media may blur relative channel strength
4. **ROI language vs DGP `media_beta`** — iROAS (units per $) is not the same object as
   contribution means or raw `media_beta`; ranks can disagree even when both are “correct”
   for their definition

Track as an **open issue** for a later recovery / calibration story. Do not bury it in
passing notes.

---

## How to run

```bash
cd "/home/mario/dev/MMT&MMM"
conda activate mmt-mmm
conda env update -f environment.yml --prune

python -m src.data.etl
python -m src.data.qa

# Fast (no MCMC)
python -m pytest tests/test_meridian_data.py tests/test_model_spike_helpers.py -q

python scripts/02_model_spike.py --mode smoke
python scripts/02_model_spike.py --mode full   # slow on CPU
```

## Where artifacts live

| Artifact | Path |
| --- | --- |
| Adapter | `src/models/meridian_data.py` |
| Spike script | `scripts/02_model_spike.py` |
| Metrics + DoD flags | `reports/metrics.json` |
| Posterior predictive | `reports/figures/posterior_predictive.png` |
| Recovery note | `reports/parameter_recovery.md` |
| Ground truth | `data/raw/ground_truth.json` |
| Training panel | `data/processed/clean_spend.parquet` (post-QA) |

## Related docs

- [`README.md`](../../README.md) — STORY-201 how-to
- [`data/raw/DATA_CARD.md`](../../data/raw/DATA_CARD.md) — weekly aggregation rules
- [`docs/graphify-archify.md`](../graphify-archify.md) — knowledge graph + architecture index
