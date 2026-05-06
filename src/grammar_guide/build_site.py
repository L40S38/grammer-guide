from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from grammar_guide.constants import SECTION_COLORS
from grammar_guide.load_data import load_all_data
from grammar_guide.render_cards import render_flow_steps, render_quiz_card, render_step_cards
from grammar_guide.render_tables import render_styled_table
from grammar_guide.render_timeline import render_time_axis

MIN_SECTION_IDS = [1, 2, 3, 7, 8]
ALL_SECTION_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def _make_section_payload(section: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    section_id = int(section["section_id"])
    table_html = ""
    timeline_html = ""
    cards_html = ""

    if section_id == 1:
        table_html = render_styled_table(data["forms_df"], section_id)
    elif section_id == 2:
        table_html = render_styled_table(data["tenses_df"], section_id)
        timeline_html = render_time_axis(data["tenses_items"], "時制・完了形の時間軸")
    elif section_id == 3:
        table_html = render_styled_table(data["conditionals_df"], section_id)
        timeline_html = render_time_axis(data["conditionals_items"], "条件文・仮定法の時間軸")
    elif section_id == 4:
        table_html = render_styled_table(data["modals_df"], section_id)
    elif section_id == 5:
        table_html = render_styled_table(data["modal_perfects_df"], section_id)
        timeline_html = render_time_axis(data["modal_perfects_items"], "助動詞 + have done の時間軸")
    elif section_id == 6:
        table_html = render_styled_table(data["confusions_df"], section_id)
        timeline_html = render_time_axis(data["confusions_items"], "混同しやすい形の比較")
    elif section_id == 7:
        table_html = (
            "<h3>自然な候補</h3>"
            + render_styled_table(data["toeic_natural_df"], section_id)
            + "<h3>不自然になりやすい候補</h3>"
            + render_styled_table(data["toeic_unnatural_df"], section_id)
        )
        cards_html = render_flow_steps(data["toeic_patterns"].get("flow_steps", []))
    elif section_id == 8:
        table_html = render_styled_table(data["decision_table_df"], section_id)
        timeline_html = render_time_axis(data["decision_table_items"], "判定表の時間軸")
    elif section_id == 9:
        cards_html = render_step_cards(data["check_steps"].get("steps", []))
        quiz = data["check_steps"].get("quiz", {})
        cards_html += render_quiz_card(quiz.get("sentence", ""), quiz.get("options", []))

    return {
        "section_id": section_id,
        "title": section["title"],
        "description": section.get("description", ""),
        "point_box": section.get("point_box", ""),
        "timeline_html": timeline_html,
        "table_html": table_html,
        "cards_html": cards_html,
        "color": SECTION_COLORS.get(section_id, "#1f5aa6"),
    }


def build_site(phase: str = "full") -> Path:
    project_root = Path(__file__).resolve().parents[2]
    data = load_all_data(project_root / "data")

    section_ids = MIN_SECTION_IDS if phase == "min" else ALL_SECTION_IDS
    raw_sections = [s for s in data["sections"] if int(s["section_id"]) in section_ids]
    sections = [_make_section_payload(s, data) for s in raw_sections]

    for idx, section in enumerate(sections):
        section["prev_id"] = sections[(idx - 1) % len(sections)]["section_id"]
        section["next_id"] = sections[(idx + 1) % len(sections)]["section_id"]

    env = Environment(
        loader=FileSystemLoader(project_root / "templates"),
        autoescape=select_autoescape(["html", "j2"]),
    )
    template = env.get_template("index.html.j2")
    html = template.render(page_title="TOEIC英文法・時間軸ビジュアル教材", sections=sections)

    public_dir = project_root / "public"
    assets_dir = public_dir / "assets"
    if public_dir.exists():
        shutil.rmtree(public_dir)
    (assets_dir / "css").mkdir(parents=True, exist_ok=True)
    (assets_dir / "js").mkdir(parents=True, exist_ok=True)

    shutil.copy2(project_root / "static" / "css" / "style.css", assets_dir / "css" / "style.css")
    shutil.copy2(project_root / "static" / "js" / "main.js", assets_dir / "js" / "main.js")
    (public_dir / "index.html").write_text(html, encoding="utf-8")
    (public_dir / ".nojekyll").write_text("", encoding="utf-8")
    return public_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Build grammar guide static site")
    parser.add_argument("--phase", choices=["min", "full"], default="full")
    args = parser.parse_args()
    output = build_site(phase=args.phase)
    print(f"Built site: {output}")


if __name__ == "__main__":
    main()

