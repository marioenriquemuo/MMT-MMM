"""STORY-302 C-suite brief (fact pack, schema, offline and live render)."""

from src.report.brief import DEFAULT_MODEL, build_messages, render_live, render_offline
from src.report.facts import build_fact_pack, numbers_match
from src.report.schema import ChannelShift, CsuiteBrief, FactPack, emit_brief_json_schema

__all__ = [
    "DEFAULT_MODEL",
    "ChannelShift",
    "CsuiteBrief",
    "FactPack",
    "build_fact_pack",
    "build_messages",
    "emit_brief_json_schema",
    "numbers_match",
    "render_live",
    "render_offline",
]
