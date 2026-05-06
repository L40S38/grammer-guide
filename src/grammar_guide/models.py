from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TimeFocus = Literal[
    "past",
    "past_before_past",
    "present",
    "future",
    "past_to_present",
    "present_to_future",
    "past_to_future",
    "general",
    "hypothetical_present_future",
    "counterfactual_past",
]

PointOrSpan = Literal[
    "point",
    "span",
    "habit",
    "result",
    "experience",
    "progress",
    "condition",
    "not_applicable",
]

StateType = Literal[
    "fact",
    "habit",
    "action_point",
    "in_progress",
    "completed",
    "result",
    "experience",
    "possibility",
    "ability",
    "obligation",
    "advice",
    "deduction",
    "counterfactual",
    "polite_request",
    "intention",
]

RealityType = Literal["fact", "real", "likely", "hypothetical", "counterfactual"]


@dataclass(slots=True)
class GrammarItem:
    section: int
    id: str
    label: str
    form: str
    meaning_ja: str
    time_focus: str
    start: float | None
    end: float | None
    point_or_span: str
    state: str
    reality: str
    nuance: str
    example_en: str
    example_ja: str
    toeic_hint: str
    importance: int = 1


@dataclass(slots=True)
class ConditionalItem:
    label: str
    clause: str
    start: float
    end: float
    reality: str
    form: str
    meaning_ja: str
    state: str
    example_en: str
    toeic_hint: str

