# How to test this marketing mix modeling tool

No statistics background needed. This Bayesian MMM page is a marketing measurement check on Google Meridian output. Incrementality shows up as incremental lift. Media mix optimization is the budget allocation on the executive dashboard. Unified measurement in this repo also includes touchpoint calibration, and adstock is already inside the fitted curves. You are only checking that the planner runs.

## 1. What you are testing

You are testing a budget planner. Set a total budget and a minimum and maximum share for each media partner. The recommended split aims at a higher incremental KPI. The page shows response curves, where saturation flattens extra spend, and a short commentary. Live Claude is optional.

## 2. Install once

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html), then from the repo root:

```bash
cd "/home/mario/dev/MMT&MMM"
conda env create -f environment.yml
conda activate mmt-mmm
```

## 3. Automated test

```bash
conda activate mmt-mmm
python -m pytest tests/ -q
```

Pass: the pytest summary reports no failures. On failure, copy the last 30 lines of the output.

## 4. Dashboard test, no API key

```bash
conda activate mmt-mmm
cd "/home/mario/dev/MMT&MMM"
streamlit run app/streamlit_app.py
```

Open the local URL Streamlit prints. Move the total budget. Move one partner’s min % and max %. Check the allocation table, the response-curve chart, the saturation chart, the before/after chart, and the offline commentary. The recommended split and the charts move together. Commentary stays offline until **Update insights**.

## 5. Optional live test

Set `ANTHROPIC_API_KEY`, or put one line in gitignored `Secret/anthropic_api_key`. Then click **Update insights**. Success: the commentary figures match the table. A missing key fails only this optional step. The offline brief and the rest of the dashboard still run.

## 6. What a good result is not

A good result is not currency, not client revenue, and not proof that Meridian channel rank matches the synthetic ground truth.
