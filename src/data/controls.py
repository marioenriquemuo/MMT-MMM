"""STORY-501 date-level exogenous controls aligned to the spend panel.

One row per date (not per channel). Continuous series fill a missing day with 0.
Flags are never null and stay in {0, 1}.

`brand_search_volume` can be a mediator (media causes brand search).
`inventory_oos_flag` can be a result of demand. This module only aligns them.
No Meridian, no regression, no geo split.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.pandas as pa

# --- Paths ---

TableSource = str | Path | pd.DataFrame

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROLS_DIR = REPO_ROOT / "data" / "raw" / "controls"
DEFAULT_PANEL_PATH = REPO_ROOT / "data" / "raw" / "synthetic_ad_spend.csv"
DEFAULT_ORGANIC_PATH = CONTROLS_DIR / "organic_seo_clicks.csv"
DEFAULT_BRAND_PATH = CONTROLS_DIR / "brand_search_volume.csv"
DEFAULT_CRM_PATH = CONTROLS_DIR / "crm_email_volume.csv"
DEFAULT_HOLIDAYS_PATH = CONTROLS_DIR / "holidays.csv"
DEFAULT_PRICE_DROPS_PATH = CONTROLS_DIR / "price_drops.csv"
DEFAULT_STOCKOUTS_PATH = CONTROLS_DIR / "stockouts.csv"
DEFAULT_OUT_PATH = REPO_ROOT / "data" / "processed" / "exogenous_controls.parquet"

COLUMNS = (
    "date",
    "organic_seo_clicks",
    "brand_search_volume",
    "crm_email_volume",
    "holiday_flag",
    "quincena_flag",
    "price_drop_flag",
    "inventory_oos_flag",
)
EXAMPLE_DATES = ("2023-07-15", "2023-07-31", "2023-07-16")

# --- Schema ---


def _count_col() -> pa.Column:
    return pa.Column(int, checks=pa.Check.ge(0), nullable=False)


def _flag_col() -> pa.Column:
    return pa.Column(int, checks=pa.Check.isin([0, 1]), nullable=False)


ControlsSchema = pa.DataFrameSchema(
    {
        "date": pa.Column(pa.DateTime, nullable=False),
        "organic_seo_clicks": _count_col(),
        "brand_search_volume": _count_col(),
        "crm_email_volume": _count_col(),
        "holiday_flag": _flag_col(),
        "quincena_flag": _flag_col(),
        "price_drop_flag": _flag_col(),
        "inventory_oos_flag": _flag_col(),
    },
    strict=True,
    coerce=True,
    unique=["date"],
)


# --- Align ---


def _table(source: TableSource) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        return source.copy()
    if isinstance(source, (str, Path)):
        return pd.read_csv(source)
    raise TypeError("expected a CSV path or a DataFrame")


def _dated(source: TableSource) -> pd.DataFrame:
    df = _table(source)
    if "date" not in df.columns:
        raise ValueError("expected a date column")
    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.normalize()
    if df["date"].isna().any():
        raise ValueError("null dates")
    return df


def _panel_dates(panel: TableSource) -> pd.DatetimeIndex:
    dates = _dated(panel)["date"].drop_duplicates().sort_values()
    return pd.DatetimeIndex(dates)


def _counts(source: TableSource, column: str, index: pd.DatetimeIndex) -> pd.Series:
    """Reindex to the panel. Absent day → 0. Do not forward-fill."""
    df = _dated(source)
    if column not in df.columns:
        raise ValueError(f"missing column {column}")
    df[column] = pd.to_numeric(df[column], errors="raise")
    df = df.drop_duplicates(subset="date", keep="last")
    filled = df.set_index("date")[column].reindex(index).fillna(0)
    bad = (filled < 0) | (filled != filled.round(0))
    if bool(bad.any()):
        raise ValueError(f"{column} must be whole-number counts ≥ 0")
    return filled.round(0).astype("int64")


def _flag(source: TableSource, index: pd.DatetimeIndex) -> pd.Series:
    """1 when the date is listed and falls on the panel index."""
    listed = pd.DatetimeIndex(_dated(source)["date"].drop_duplicates())
    return pd.Series(index.isin(listed).astype("int64"), index=index)


def _quincena(index: pd.DatetimeIndex) -> pd.Series:
    """1 on day 15 and on the last calendar day of the month."""
    flag = ((index.day == 15) | index.is_month_end).astype("int64")
    return pd.Series(flag, index=index)


def build_controls(
    panel: TableSource,
    organic_seo_clicks: TableSource = DEFAULT_ORGANIC_PATH,
    brand_search_volume: TableSource = DEFAULT_BRAND_PATH,
    crm_email_volume: TableSource = DEFAULT_CRM_PATH,
    holidays: TableSource = DEFAULT_HOLIDAYS_PATH,
    price_drops: TableSource = DEFAULT_PRICE_DROPS_PATH,
    stockouts: TableSource = DEFAULT_STOCKOUTS_PATH,
) -> pd.DataFrame:
    """Align controls to the spend panel's unique dates.

    Each argument is a CSV path or an in-memory frame. Auxiliary dates outside
    that span are dropped. A panel day missing from a continuous source is 0
    (not forward-filled). National and local holidays share ``holiday_flag``.
    """
    index = _panel_dates(panel)
    organic = _counts(organic_seo_clicks, "organic_seo_clicks", index)
    brand = _counts(brand_search_volume, "brand_search_volume", index)
    crm = _counts(crm_email_volume, "crm_email_volume", index)
    frame = pd.DataFrame(
        {
            "date": index,
            "organic_seo_clicks": organic.to_numpy(),
            "brand_search_volume": brand.to_numpy(),
            "crm_email_volume": crm.to_numpy(),
            "holiday_flag": _flag(holidays, index).to_numpy(),
            "quincena_flag": _quincena(index).to_numpy(),
            "price_drop_flag": _flag(price_drops, index).to_numpy(),
            "inventory_oos_flag": _flag(stockouts, index).to_numpy(),
        }
    )
    return ControlsSchema.validate(frame)


# --- Write ---


def write_controls(
    df: pd.DataFrame,
    path: str | Path = DEFAULT_OUT_PATH,
) -> Path:
    """Validate and write ``data/processed/exogenous_controls.parquet``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ControlsSchema.validate(df).to_parquet(path, engine="pyarrow", index=False)
    return path


# --- Smoke ---


def _self_check() -> None:
    """Frames: one row per date, missing day is 0, outside dates drop."""
    panel = pd.DataFrame(
        {
            "date": ["2023-07-14", "2023-07-15", "2023-07-16"] * 2,
            "channel": ["meta"] * 3 + ["google"] * 3,
        }
    )
    organic = pd.DataFrame(
        {
            "date": ["2023-07-14", "2023-07-16", "2023-01-01"],
            "organic_seo_clicks": [10, 30, 999],
        }
    )
    brand = pd.DataFrame({"date": ["2023-07-14"], "brand_search_volume": [4]})
    crm = pd.DataFrame({"date": ["2023-07-15"], "crm_email_volume": [7]})
    holidays = pd.DataFrame(
        {
            "date": ["2023-07-16", "2023-07-16", "2022-12-25"],
            "scope": ["national", "local", "national"],
        }
    )
    price = pd.DataFrame({"date": ["2023-07-15", "2025-01-01"]})
    stock = pd.DataFrame({"date": ["2023-07-14"]})
    df = build_controls(panel, organic, brand, crm, holidays, price, stock)
    if len(df) != 3 or int(df.isna().to_numpy().sum()) != 0:
        raise AssertionError("self-check shape")
    by_day = df.set_index(pd.to_datetime(df["date"]))
    fifteenth = pd.Timestamp("2023-07-15")
    if int(by_day.loc[fifteenth, "organic_seo_clicks"]) != 0:
        raise AssertionError("missing day was not 0")
    if int(by_day.loc[fifteenth, "brand_search_volume"]) != 0:
        raise AssertionError("forward-filled a continuous column")
    if int(by_day.loc[fifteenth, "quincena_flag"]) != 1:
        raise AssertionError("day 15 quincena")
    if int(by_day.loc[fifteenth, "price_drop_flag"]) != 1:
        raise AssertionError("price-drop flag")
    if int(by_day.loc[pd.Timestamp("2023-07-16"), "holiday_flag"]) != 1:
        raise AssertionError("national and local must share holiday_flag")
    if int(by_day.loc[pd.Timestamp("2023-07-14"), "inventory_oos_flag"]) != 1:
        raise AssertionError("stockout flag")
    if int(df["organic_seo_clicks"].max()) == 999 or int(df["holiday_flag"].sum()) != 1:
        raise AssertionError("date outside the panel span leaked")


def _assert_matches_panel(df: pd.DataFrame, panel: TableSource) -> None:
    expected = _panel_dates(panel)
    got = pd.DatetimeIndex(pd.to_datetime(df["date"]))
    if not got.equals(expected):
        raise AssertionError(
            f"controls dates {len(got)} != unique spend panel dates {len(expected)}"
        )
    if int(df.isna().to_numpy().sum()) != 0:
        raise AssertionError("null controls")
    quincena = pd.Series(((expected.day == 15) | expected.is_month_end).astype("int64"))
    got_q = df["quincena_flag"].astype("int64").reset_index(drop=True)
    if not got_q.equals(quincena):
        raise AssertionError("quincena_flag is not day 15 or calendar month-end")
    for column, source in (
        ("holiday_flag", DEFAULT_HOLIDAYS_PATH),
        ("price_drop_flag", DEFAULT_PRICE_DROPS_PATH),
        ("inventory_oos_flag", DEFAULT_STOCKOUTS_PATH),
    ):
        listed = pd.DatetimeIndex(_dated(source)["date"].drop_duplicates())
        want = pd.Series(expected.isin(listed).astype("int64"))
        got_flag = df[column].astype("int64").reset_index(drop=True)
        if not got_flag.equals(want):
            raise AssertionError(f"{column} does not match listed dates")


def _print_examples(df: pd.DataFrame) -> None:
    print(f"rows={len(df)} nulls={int(df.isna().to_numpy().sum())}")
    dated = pd.to_datetime(df["date"])
    for day in EXAMPLE_DATES:
        row = df.loc[dated == pd.Timestamp(day)]
        if len(row) != 1:
            raise AssertionError(f"missing example date {day}")
        rec = row.iloc[0]
        print(
            day,
            f"organic_seo_clicks={int(rec.organic_seo_clicks)}",
            f"brand_search_volume={int(rec.brand_search_volume)}",
            f"crm_email_volume={int(rec.crm_email_volume)}",
            f"holiday_flag={int(rec.holiday_flag)}",
            f"quincena_flag={int(rec.quincena_flag)}",
            f"price_drop_flag={int(rec.price_drop_flag)}",
            f"inventory_oos_flag={int(rec.inventory_oos_flag)}",
        )


def main() -> None:
    """CLI: ``python -m src.data.controls``."""
    _self_check()
    panel = _table(DEFAULT_PANEL_PATH)
    df = build_controls(panel)
    _assert_matches_panel(df, panel)
    out = write_controls(df)
    _print_examples(df)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
