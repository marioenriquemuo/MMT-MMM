"""STORY-302 C-suite brief inputs (fact pack + brief schema)."""

from src.report.facts import build_fact_pack, numbers_match
from src.report.schema import ChannelShift, CsuiteBrief, FactPack, emit_brief_json_schema

__all__ = [
    "ChannelShift",
    "CsuiteBrief",
    "FactPack",
    "build_fact_pack",
    "emit_brief_json_schema",
    "numbers_match",
]
