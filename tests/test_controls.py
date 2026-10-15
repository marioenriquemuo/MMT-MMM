"""Tests for STORY-501 date-level controls (alignment and flags)."""

from __future__ import annotations

import pandas as pd

from src.data.controls import (
    COLUMNS,
    DEFAULT_HOLIDAYS_PATH,
    DEFAULT_PANEL_PATH,
    DEFAULT_PRICE_DROPS_PATH,
    DEFAULT_STOCKOUTS_PATH,
    build_controls,
)
from src.data.generator import CHANNELS, N_DAYS

CONTROL_COLUMNS = [name for name in COLUMNS if name != "date"]


def _spend_panel() -> pd.DataFrame:
    return pd.read_csv(DEFAULT_PANEL_PATH, parse_dates=["date"])


def _row(df: pd.DataFrame, day) -> pd.Series:
    hit = df.loc[pd.to_datetime(df["date"]) == pd.Timestamp(day)]
    assert len(hit) == 1, day
    return hit.iloc[0]


def test_row_count_matches_unique_panel_dates():
    panel = _spend_panel()
    controls = build_controls(panel)
    assert panel["date"].nunique() == N_DAYS
    assert len(controls) == N_DAYS
    assert int(controls.isna().to_numpy().sum()) == 0


def test_quincena_flag_matches_calendar():
    controls = build_controls(DEFAULT_PANEL_PATH)
    dates = pd.to_datetime(controls["date"])
    expected = ((dates.dt.day == 15) | dates.dt.is_month_end).astype("int64")
    got = controls["quincena_flag"].astype("int64")
    assert got.tolist() == expected.tolist()


def test_listed_event_is_one_and_normal_day_is_zero():
    controls = build_controls(DEFAULT_PANEL_PATH)
    holiday_dates = pd.to_datetime(pd.read_csv(DEFAULT_HOLIDAYS_PATH)["date"])
    price_dates = pd.to_datetime(pd.read_csv(DEFAULT_PRICE_DROPS_PATH)["date"])
    stock_dates = pd.to_datetime(pd.read_csv(DEFAULT_STOCKOUTS_PATH)["date"])
    assert int(_row(controls, holiday_dates.iloc[0])["holiday_flag"]) == 1
    assert int(_row(controls, price_dates.iloc[0])["price_drop_flag"]) == 1
    assert int(_row(controls, stock_dates.iloc[0])["inventory_oos_flag"]) == 1

    listed = set(holiday_dates) | set(price_dates) | set(stock_dates)
    dates = pd.to_datetime(controls["date"])
    normal = [
        day
        for day in dates
        if day not in listed and day.day != 15 and not day.is_month_end
    ]
    assert normal
    row = _row(controls, normal[0])
    assert int(row["holiday_flag"]) == 0
    assert int(row["price_drop_flag"]) == 0
    assert int(row["inventory_oos_flag"]) == 0


def test_missing_auxiliary_day_fills_zero():
    panel = pd.DataFrame(
        {"date": ["2023-07-14", "2023-07-15"], "channel": ["meta", "google"]}
    )
    # 15th is absent. A forward-fill would copy 10 from the 14th.
    organic = pd.DataFrame({"date": ["2023-07-14"], "organic_seo_clicks": [10]})
    brand = pd.DataFrame(
        {"date": ["2023-07-14", "2023-07-15"], "brand_search_volume": [1, 2]}
    )
    crm = pd.DataFrame(
        {"date": ["2023-07-14", "2023-07-15"], "crm_email_volume": [3, 4]}
    )
    outside = pd.DataFrame({"date": ["2020-01-01"]})
    controls = build_controls(panel, organic, brand, crm, outside, outside, outside)
    assert int(controls.isna().to_numpy().sum()) == 0
    assert int(_row(controls, "2023-07-15")["organic_seo_clicks"]) == 0
    assert int(_row(controls, "2023-07-14")["organic_seo_clicks"]) == 10


def test_left_join_keeps_spend_rows_and_control_values():
    spend = _spend_panel()
    controls = build_controls(spend)
    merged = spend.merge(controls, on="date", how="left")
    assert len(merged) == len(spend) == N_DAYS * len(CHANNELS)
    assert int(merged[CONTROL_COLUMNS].isna().to_numpy().sum()) == 0
