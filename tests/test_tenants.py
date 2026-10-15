"""STORY-502: one client's files never enter another client's tree."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.data.etl import run_etl
from src.data.tenants import (
    REPO_ROOT,
    TenantError,
    list_processed,
    load_client,
    open_client_file,
    resolve_client_path,
)


def test_pathc_keeps_legacy_roots():
    client = load_client()
    roots = client["roots"]
    assert client["client_id"] == "pathc"
    assert client["currency"] == "USD"
    assert client["channels"] == ["meta", "google", "tiktok", "tv"]
    assert client["regions"] == ["national"]
    assert roots["raw"] == (REPO_ROOT / "data" / "raw").resolve()
    assert roots["processed"] == (REPO_ROOT / "data" / "processed").resolve()
    assert roots["reports"] == (REPO_ROOT / "reports").resolve()
    assert roots["models"] == (REPO_ROOT / "data" / "clients" / "pathc" / "models").resolve()


def test_wellness_stays_in_its_own_tree():
    client = load_client("wellness")
    home = (REPO_ROOT / "data" / "clients" / "wellness").resolve()
    assert client["channels"] == ["meta", "google"]
    assert client["regions"] == ["national"]
    for root in client["roots"].values():
        root.resolve().relative_to(home)


@pytest.mark.parametrize("client_id", ["../pathc", "pathc/../wellness", "unknown-client", ""])
def test_bad_client_id_raises(client_id: str):
    with pytest.raises(TenantError):
        load_client(client_id)


def test_model_paths_do_not_nest():
    pathc = load_client("pathc")["roots"]
    wellness = load_client("wellness")["roots"]
    wellness_models = wellness["models"].resolve()
    pathc_models = pathc["models"].resolve()
    for root in pathc.values():
        with pytest.raises(ValueError):
            wellness_models.relative_to(root.resolve())
    for root in wellness.values():
        with pytest.raises(ValueError):
            pathc_models.relative_to(root.resolve())


def test_open_client_file_rejects_other_client():
    wellness_csv = load_client("wellness")["roots"]["raw"] / "synthetic_ad_spend.csv"
    pathc_csv = load_client("pathc")["roots"]["raw"] / "synthetic_ad_spend.csv"
    with pytest.raises(TenantError):
        open_client_file("pathc", wellness_csv)
    with pytest.raises(TenantError):
        resolve_client_path(
            "wellness",
            "data/raw/../clients/wellness/../../raw/synthetic_ad_spend.csv",
        )
    with open_client_file("wellness", wellness_csv) as handle:
        assert "date,channel" in handle.readline()
    assert resolve_client_path("pathc", pathc_csv) == pathc_csv.resolve()


def test_list_processed_does_not_return_other_client():
    wellness_processed = load_client("wellness")["roots"]["processed"]
    marker = wellness_processed / "wellness-only.txt"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("only-wellness\n", encoding="utf-8")
    pathc_processed = load_client("pathc")["roots"]["processed"].resolve()
    try:
        wellness_files = list_processed("wellness")
        pathc_files = list_processed("pathc")
        assert marker.resolve() in wellness_files
        assert marker.resolve() not in pathc_files
        assert all(pathc_processed not in path.parents for path in wellness_files)
        assert all(marker.resolve() != path for path in pathc_files)
    finally:
        marker.unlink(missing_ok=True)


def test_symlink_into_other_client_raises():
    target = load_client("pathc")["roots"]["raw"] / "synthetic_ad_spend.csv"
    scratch = load_client("wellness")["roots"]["raw"] / "scratch-link-to-pathc.csv"
    scratch.symlink_to(target)
    try:
        with pytest.raises(TenantError):
            resolve_client_path("wellness", scratch)
    finally:
        scratch.unlink(missing_ok=True)


def test_wellness_etl_grid_keeps_client_channels(tmp_path: Path):
    raw = load_client("wellness")["roots"]["raw"] / "synthetic_ad_spend.csv"
    out = tmp_path / "clean_spend.parquet"
    df = run_etl(raw, out, channels=tuple(load_client("wellness")["channels"]))
    assert set(df["channel"]) == {"meta", "google"}
    assert out.is_file()
