SECTION_COLORS: dict[int, str] = {
    1: "#1f5aa6",
    2: "#1b8a5a",
    3: "#6f42c1",
    4: "#16836f",
    5: "#f07c00",
    6: "#1f5aa6",
    7: "#6f42c1",
    8: "#0d47a1",
    9: "#0d47a1",
}

JUDGMENT_COLORS: dict[str, str] = {
    "◎": "#6bcf88",
    "○": "#d9f7e3",
    "△": "#fff1a8",
    "×": "#f5b5b5",
}

REALITY_STYLES: dict[str, dict[str, str]] = {
    "real": {"dash": "solid", "color": "#1f5aa6"},
    "fact": {"dash": "solid", "color": "#1f5aa6"},
    "likely": {"dash": "solid", "color": "#1b8a5a"},
    "hypothetical": {"dash": "dot", "color": "#6f42c1"},
    "counterfactual": {"dash": "dot", "color": "#d9534f"},
}

TIME_AXIS_TICKS = [-5, -3, 0, 3]
TIME_AXIS_LABELS = ["過去より前", "過去", "現在", "未来"]

