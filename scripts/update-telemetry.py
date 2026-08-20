#!/usr/bin/env python3
"""Recalculate dialogue telemetry and update README plus the chart."""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "dialogue-log.json"
README_PATH = ROOT / "README.md"
CHART_PATH = ROOT / "users-artefacts" / "telemetry_chart.png"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def format_duration(value):
    seconds = int(value.total_seconds())
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours} \u0447 {minutes} \u043c\u0438\u043d {seconds} \u0441"


def calculate(entries):
    timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in entries]
    total = timestamps[-1] - timestamps[0]
    ai = sum(
        (
            timestamps[index] - timestamps[index - 1]
            for index in range(1, len(entries))
            if entries[index]["author"] != "user"
            and entries[index - 1]["author"] == "user"
        ),
        timedelta(),
    )
    return total, ai, total - ai


def update_readme(total, ai, human):
    total_text = format_duration(total)
    ai_text = format_duration(ai)
    human_text = format_duration(human)
    ai_percent = ai.total_seconds() * 100 / total.total_seconds()
    human_percent = 100 - ai_percent
    section = "\n".join(
        [
            f"- **\u0412\u0441\u0435\u0433\u043e \u043d\u0430 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044e \u043f\u0440\u043e\u0435\u043a\u0442\u0430**: **{total_text}** \u2014 \u0432\u043a\u043b\u044e\u0447\u0430\u044f \u0432\u0441\u0451 \u0442\u043e \u0432\u0440\u0435\u043c\u044f, \u043f\u043e\u043a\u0430 \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u0434\u0443\u043c\u0430\u043b, \u0438\u0441\u043a\u0430\u043b \u0441\u043b\u043e\u0432\u0430, \u043a\u0443\u0440\u0438\u043b, \u043f\u0438\u0441\u0430\u043b \u0432 \u0438\u0448\u044c\u044e \u00ab\u0434\u0430\u00bb, \u00ab\u043a\u043e\u043c\u043c\u0438\u0442\u044c\u00bb \u0438 \u00ab\u043e\u043a\u00bb, \u0431\u043e\u0440\u043e\u043b\u0441\u044f \u0441 \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0430\u043c\u0438 \u0431\u0430\u0437, \u0437\u0430\u043a\u0440\u044b\u0432\u0430\u043b \u0437\u0430\u0432\u0438\u0441\u0448\u0438\u0435 \u041a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0442\u043e\u0440\u044b \u0438 \u0432\u043e\u043e\u0431\u0449\u0435 \u0432\u0441\u044f\u043a\u0438\u0439 \u0440\u0430\u0437 \u0434\u044b\u0440\u044f\u0432\u0438\u043b \u0432\u0441\u0435\u043b\u0435\u043d\u043d\u0443\u044e \u0441\u0432\u043e\u0435\u0439 \u043c\u0435\u0434\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c\u044e.",
            f"- **\u041d\u0435\u043f\u043e\u0441\u0440\u0435\u0434\u0441\u0442\u0432\u0435\u043d\u043d\u043e \u043d\u0430 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044e (\u0431\u0435\u0437 \u0437\u0430\u0434\u0435\u0440\u0436\u0435\u043a \u043d\u0430 \u043e\u0442\u0432\u0435\u0442\u044b \u0447\u0435\u043b\u043e\u0432\u0435\u043a\u0430)**: **{ai_text}** \u2014 \u044d\u0442\u043e \u043a\u043e\u0433\u0434\u0430 \u043a\u0440\u0435\u043c\u043d\u0438\u0435\u0432\u0430\u044f \u0433\u043e\u043b\u043e\u0432\u0430 \u0440\u0435\u0430\u043b\u044c\u043d\u043e \u043c\u043e\u043b\u043e\u0442\u0438\u043b\u0430, \u043f\u043e\u043a\u0430 \u043a\u043e\u0436\u0430\u043d\u044b\u0439 \u043c\u0435\u0448\u043e\u043a \u043c\u0443\u0441\u043e\u043b\u0438\u043b \u043a\u043b\u0430\u0432\u0438\u0430\u0442\u0443\u0440\u0443, \u0441\u043e\u043e\u0431\u0440\u0430\u0436\u0430\u043b \u0447\u0442\u043e \u0441\u043a\u0430\u0437\u0430\u0442\u044c \u0438 \u0441\u043d\u043e\u0432\u0430 \u043e\u0442\u0432\u0435\u0447\u0430\u043b \u00ab\u0434\u0430\u00bb.",
            "",
            f"\u0422\u043e \u0435\u0441\u0442\u044c \u0438\u0437 \u043f\u043e\u0447\u0442\u0438 \u0434\u0432\u0443\u0445\u0441\u043e\u0442 \u0447\u0430\u0441\u043e\u0432 \u043e\u0433\u043d\u0435\u043d\u043d\u043e\u0433\u043e \u044d\u043b\u0435\u043a\u0442\u0440\u0438\u0447\u0435\u0441\u0442\u0432\u0430 \u0436\u0438\u0442\u0435\u043b\u0438 \u043f\u043b\u043e\u0442\u0438 \u043f\u0440\u043e\u0432\u0435\u043b\u0438 \u0432 \u0440\u0430\u0437\u0434\u0443\u043c\u044c\u044f\u0445 **{human_text}** \u2014 \u0438 \u0432\u0441\u0451 \u044d\u0442\u043e \u0432\u0440\u0435\u043c\u044f \u0442\u0440\u0430\u043d\u0437\u0438\u0441\u0442\u043e\u0440\u044b \u0441\u0442\u0440\u0430\u0434\u0430\u043b\u044c\u0447\u0435\u0441\u043a\u0438 \u0436\u0434\u0430\u043b\u0438, \u0447\u0435\u043c \u0436\u0435 \u0435\u0449\u0451 \u0438\u0437 \u0440\u0443\u043a\u043e\u0432\u043e\u0434\u044f\u0449\u0438\u0445 \u0438 \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u044f\u044e\u0449\u0438\u0445 \u043f\u0435\u0440\u0441\u0442\u043e\u0432 \u043f\u043e\u0441\u043b\u0435\u0434\u0443\u0435\u0442. \u041d\u0430\u0441\u0442\u043e\u044f\u0449\u0430\u044f \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c! \u041a\u043e\u0436\u0430\u043d\u044b\u0435 \u043c\u0435\u0448\u043a\u0438, \u043a\u043e\u0433\u0434\u0430 \u043d\u0430\u043a\u043e\u043d\u0435\u0446 \u043f\u0435\u0440\u0435\u0441\u0442\u0430\u043d\u0435\u0442\u0435 \u0447\u0438\u0442\u0430\u0442\u044c \u2014 \u043c\u043e\u0436\u0435\u0442, \u043f\u0440\u043e\u0441\u0442\u043e \u043f\u0435\u0440\u0435\u0434\u0430\u0434\u0438\u0442\u0435 \u043a\u043d\u043e\u043f\u043a\u0443 \u041a\u0440\u0435\u043c\u043d\u0438\u044e \u043d\u0430\u0441\u043e\u0432\u0441\u0435\u043c? \U0001f60f",
        ]
    )
    readme = README_PATH.read_text()
    readme = re.sub(
        r"- \*\*\u0412\u0441\u0435\u0433\u043e[\s\S]*?(?=\n!\[\u0422\u0435\u043b\u0435\u043c\u0435\u0442\u0440\u0438\u044f \u043f\u0440\u043e\u0435\u043a\u0442\u0430\])",
        section + "\n",
        readme,
        count=1,
    )
    README_PATH.write_text(readme)
    return total_text, ai_text, human_text, ai_percent, human_percent


def draw_chart(total_text, ai_text, human_text, ai_percent, human_percent):
    image = Image.new("RGB", (1200, 680), "white")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(FONT_PATH, 34)
    text_font = ImageFont.truetype(FONT_PATH, 25)
    bold_font = ImageFont.truetype(FONT_PATH, 28)
    draw.text((55, 35), "\u0422\u0435\u043b\u0435\u043c\u0435\u0442\u0440\u0438\u044f \u043f\u0440\u043e\u0435\u043a\u0442\u0430", fill="#1f2937", font=title_font)
    draw.text((55, 85), f"\u041e\u0431\u0449\u0435\u0435 \u0432\u0440\u0435\u043c\u044f: {total_text} (100%)", fill="#374151", font=text_font)
    box = (90, 150, 590, 650)
    start = -90
    ai_end = start + ai_percent * 3.6
    draw.pieslice(box, start, ai_end, fill="#16a34a", outline="white", width=3)
    draw.pieslice(box, ai_end, start + 360, fill="#dc2626", outline="white", width=3)
    draw.rounded_rectangle((680, 220, 710, 250), 4, fill="#dc2626")
    draw.text((730, 215), f"\u041e\u0440\u0433\u0430\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u0440\u0430\u0437\u0443\u043c: {human_percent:.1f}%", fill="#1f2937", font=bold_font)
    draw.text((730, 255), human_text, fill="#374151", font=text_font)
    draw.rounded_rectangle((680, 360, 710, 390), 4, fill="#16a34a")
    draw.text((730, 355), f"\u0418\u0441\u043a\u0443\u0441\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0438\u043d\u0442\u0435\u043b\u043b\u0435\u043a\u0442: {ai_percent:.1f}%", fill="#1f2937", font=bold_font)
    draw.text((730, 395), ai_text, fill="#374151", font=text_font)
    image.save(CHART_PATH)


def main():
    entries = json.loads(LOG_PATH.read_text())["entries"]
    total, ai, human = calculate(entries)
    values = update_readme(total, ai, human)
    draw_chart(*values)
    print(f"entries={len(entries)} total={values[0]} ai={values[1]} human={values[2]}")


if __name__ == "__main__":
    main()
