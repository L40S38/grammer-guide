from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

from grammar_guide.constants import REALITY_STYLES, TIME_AXIS_LABELS, TIME_AXIS_TICKS


def _get_value(item: Any, key: str, default: Any = "") -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def render_time_axis(items: list[Any], title: str) -> str:
    fig = go.Figure()
    if not items:
        return fig.to_html(include_plotlyjs=False, full_html=False)

    for idx, item in enumerate(items):
        label = str(_get_value(item, "label", f"item-{idx + 1}"))
        start = _get_value(item, "start", 0)
        end = _get_value(item, "end", start)
        point_or_span = str(_get_value(item, "point_or_span", "point"))
        reality = str(_get_value(item, "reality", "fact"))
        styles = REALITY_STYLES.get(reality, REALITY_STYLES["fact"])

        hover_text = "<br>".join(
            [
                f"形: {_get_value(item, 'form', '')}",
                f"意味: {_get_value(item, 'meaning_ja', '')}",
                f"状態: {_get_value(item, 'state', '')}",
                f"例文: {_get_value(item, 'example_en', '')}",
                f"TOEICヒント: {_get_value(item, 'toeic_hint', '')}",
            ]
        )

        if point_or_span in {"span", "habit", "result", "experience", "progress", "condition"}:
            fig.add_trace(
                go.Scatter(
                    x=[start, end],
                    y=[label, label],
                    mode="lines+markers",
                    line={"color": styles["color"], "dash": styles["dash"], "width": 6},
                    marker={"size": 8, "color": styles["color"]},
                    hovertemplate=hover_text + "<extra></extra>",
                    showlegend=False,
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=[start],
                    y=[label],
                    mode="markers",
                    marker={"size": 11, "color": styles["color"], "symbol": "circle"},
                    hovertemplate=hover_text + "<extra></extra>",
                    showlegend=False,
                )
            )

    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="#334155")
    fig.update_layout(
        title=title,
        xaxis={
            "tickmode": "array",
            "tickvals": TIME_AXIS_TICKS,
            "ticktext": TIME_AXIS_LABELS,
            "range": [-5.5, 3.5],
            "title": "時間軸",
        },
        yaxis={"title": ""},
        height=max(360, 80 + len(items) * 55),
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig.to_html(include_plotlyjs=False, full_html=False)

