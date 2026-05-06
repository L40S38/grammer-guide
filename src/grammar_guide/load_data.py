from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from grammar_guide.models import ConditionalItem, GrammarItem


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return loaded


def _to_grammar_items(section_id: int, timeline: list[dict[str, Any]]) -> list[GrammarItem]:
    items: list[GrammarItem] = []
    for i, row in enumerate(timeline, start=1):
        item = GrammarItem(
            section=section_id,
            id=f"sec{section_id}_{i:02d}",
            label=str(row.get("label", "")),
            form=str(row.get("form", "")),
            meaning_ja=str(row.get("meaning_ja", "")),
            time_focus=str(row.get("time_focus", "general")),
            start=float(row["start"]) if row.get("start") is not None else None,
            end=float(row["end"]) if row.get("end") is not None else None,
            point_or_span=str(row.get("point_or_span", "not_applicable")),
            state=str(row.get("state", "fact")),
            reality=str(row.get("reality", "fact")),
            nuance=str(row.get("style", "")),
            example_en=str(row.get("example_en", "")),
            example_ja=str(row.get("example_ja", "")),
            toeic_hint=str(row.get("toeic_hint", "")),
            importance=int(row.get("importance", 1)),
        )
        items.append(item)
    return items


def _to_conditional_items(timeline: list[dict[str, Any]]) -> list[ConditionalItem]:
    items: list[ConditionalItem] = []
    for row in timeline:
        items.append(
            ConditionalItem(
                label=str(row.get("label", "")),
                clause=str(row.get("clause", "")),
                start=float(row.get("start", 0)),
                end=float(row.get("end", 0)),
                reality=str(row.get("reality", "fact")),
                form=str(row.get("form", "")),
                meaning_ja=str(row.get("meaning_ja", "")),
                state=str(row.get("state", "fact")),
                example_en=str(row.get("example_en", "")),
                toeic_hint=str(row.get("toeic_hint", "")),
            )
        )
    return items


def _to_df(data: dict[str, Any], key: str = "rows") -> pd.DataFrame:
    rows = data.get(key, [])
    if not isinstance(rows, list):
        raise ValueError(f"'{key}' must be list")
    return pd.DataFrame(rows)


def load_all_data(data_dir: str | Path) -> dict[str, Any]:
    base = Path(data_dir)
    sections = yaml.safe_load((base / "grammar_sections.yaml").read_text(encoding="utf-8")) or []

    forms = _load_yaml(base / "grammar_forms.yaml")
    tenses = _load_yaml(base / "grammar_tenses.yaml")
    conditionals = _load_yaml(base / "grammar_conditionals.yaml")
    modals = _load_yaml(base / "grammar_modals.yaml")
    modal_perfects = _load_yaml(base / "grammar_modal_perfects.yaml")
    confusions = _load_yaml(base / "grammar_confusions.yaml")
    toeic_patterns = _load_yaml(base / "grammar_toeic_patterns.yaml")
    decision_table = _load_yaml(base / "grammar_decision_table.yaml")
    check_steps = _load_yaml(base / "grammar_check_steps.yaml")

    return {
        "sections": sections,
        "forms": forms,
        "forms_df": _to_df(forms),
        "tenses": tenses,
        "tenses_df": _to_df(tenses),
        "tenses_items": _to_grammar_items(2, tenses.get("timeline", [])),
        "conditionals": conditionals,
        "conditionals_df": _to_df(conditionals),
        "conditionals_items": _to_conditional_items(conditionals.get("timeline", [])),
        "modals": modals,
        "modals_df": _to_df(modals),
        "modal_perfects": modal_perfects,
        "modal_perfects_df": _to_df(modal_perfects),
        "modal_perfects_items": _to_grammar_items(5, modal_perfects.get("timeline", [])),
        "confusions": confusions,
        "confusions_df": _to_df(confusions),
        "confusions_items": _to_grammar_items(6, confusions.get("timeline", [])),
        "toeic_patterns": toeic_patterns,
        "toeic_natural_df": _to_df(toeic_patterns, key="natural_rows"),
        "toeic_unnatural_df": _to_df(toeic_patterns, key="unnatural_rows"),
        "decision_table": decision_table,
        "decision_table_df": _to_df(decision_table),
        "decision_table_items": _to_grammar_items(8, decision_table.get("timeline", [])),
        "check_steps": check_steps,
    }

