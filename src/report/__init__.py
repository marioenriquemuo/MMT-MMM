"""STORY-302 C-suite brief (fact pack, schema, offline renderer)."""

from src.report.brief import build_messages, render_offline
from src.report.facts import build_fact_pack, numbers_match
from src.report.schema import ChannelShift, CsuiteBrief, FactPack, emit_brief_json_schema

__all__ = [
    "ChannelShift",
    "CsuiteBrief",
    "FactPack",
    "build_fact_pack",
    "build_messages",
    "emit_brief_json_schema",
    "numbers_match",
    "render_offline",
]
