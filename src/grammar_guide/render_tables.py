from __future__ import annotations

import html

import pandas as pd

from grammar_guide.constants import JUDGMENT_COLORS, SECTION_COLORS


def _judgment_style(value: object) -> str:
    color = JUDGMENT_COLORS.get(str(value), "")
    if not color:
        return ""
    return f"background-color: {color}; font-weight: 700;"


def render_styled_table(df: pd.DataFrame, section_id: int) -> str:
    if df.empty:
        return '<div class="table-wrapper"><p>データがありません。</p></div>'

    header_color = SECTION_COLORS.get(section_id, "#1f5aa6")
    styler = df.fillna("").style.set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("background-color", header_color),
                    ("color", "white"),
                    ("border", "1px solid #d8dee9"),
                    ("padding", "8px"),
                    ("text-align", "left"),
                ],
            },
            {
                "selector": "td",
                "props": [
                    ("border", "1px solid #e4e9f0"),
                    ("padding", "8px"),
                    ("vertical-align", "top"),
                    ("white-space", "pre-wrap"),
                ],
            },
        ]
    )

    if "判定" in df.columns:
        styler = styler.map(_judgment_style, subset=["判定"])

    table_html = styler.to_html()
    return f'<div class="table-wrapper">{html.unescape(table_html)}</div>'

