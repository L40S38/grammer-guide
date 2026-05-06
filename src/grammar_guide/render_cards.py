from __future__ import annotations

from html import escape


def render_point_box(text: str) -> str:
    return f'<div class="point-box"><strong>ポイント</strong><p>{escape(text)}</p></div>'


def render_step_cards(steps: list[dict[str, str]]) -> str:
    cards: list[str] = ['<div class="step-cards">']
    for step in steps:
        cards.append(
            (
                '<article class="step-card">'
                f'<h4>Step {escape(str(step.get("step", "")))}: {escape(str(step.get("title", "")))}</h4>'
                f'<p>{escape(str(step.get("body", "")))}</p>'
                f'<p class="step-example">{escape(str(step.get("example", "")))}</p>'
                "</article>"
            )
        )
    cards.append("</div>")
    return "".join(cards)


def render_flow_steps(steps: list[str]) -> str:
    list_items = "".join(f"<li>{escape(step)}</li>" for step in steps)
    return f'<div class="flow-card"><h4>判断フロー</h4><ol>{list_items}</ol></div>'


def render_quiz_card(sentence: str, options: list[dict[str, str]]) -> str:
    rows = "".join(
        (
            "<tr>"
            f"<td>{escape(str(opt.get('form', '')))}</td>"
            f"<td>{escape(str(opt.get('meaning', '')))}</td>"
            f"<td>{escape(str(opt.get('verdict', '')))}</td>"
            "</tr>"
        )
        for opt in options
    )
    return (
        '<div class="quiz-card">'
        f"<h4>例題: {escape(sentence)}</h4>"
        "<table><thead><tr><th>選択肢</th><th>形</th><th>判定</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
        "</div>"
    )

