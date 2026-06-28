#!/usr/bin/env python3
"""Create operation explanation slides from real screenshots.

The source UI screenshot stays visible, while arrows, boxes, labels, and the
standard #78a9ff bars are added mechanically.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1920, 1080
BAR_COLOR = "#78a9ff"
BAR_HEIGHT = 42
NAVY = "#07184A"
BLUE = "#0B6BFF"
RED = "#EF3340"
YELLOW = "#FFE66D"
WHITE = "#FFFFFF"
BLACK = "#111827"
LIGHT_BLUE = "#EEF6FF"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc" if bold else "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F_TITLE = load_font(62, True)
F_SUB = load_font(30, True)
F_BODY = load_font(30, True)
F_SMALL = load_font(24, True)


def fit_inside(im: Image.Image, box: tuple[int, int, int, int]) -> tuple[Image.Image, tuple[int, int]]:
    x1, y1, x2, y2 = box
    max_w, max_h = x2 - x1, y2 - y1
    scale = min(max_w / im.width, max_h / im.height)
    resized = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    return resized, (x1 + (max_w - resized.width) // 2, y1 + (max_h - resized.height) // 2)


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], font: ImageFont.FreeTypeFont, max_w: int, fill=BLACK, gap=8):
    x, y = xy
    line = ""
    for ch in text:
        test = line + ch
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            line = test
        else:
            draw.text((x, y), line, font=font, fill=fill)
            y += font.size + gap
            line = ch
    if line:
        draw.text((x, y), line, font=font, fill=fill)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color=RED, width=8):
    import math

    draw.line((start, end), fill=color, width=width)
    sx, sy = start
    ex, ey = end
    angle = math.atan2(ey - sy, ex - sx)
    size = 28
    a1 = angle + math.pi * 0.82
    a2 = angle - math.pi * 0.82
    draw.polygon(
        [
            (ex, ey),
            (ex + size * math.cos(a1), ey + size * math.sin(a1)),
            (ex + size * math.cos(a2), ey + size * math.sin(a2)),
        ],
        fill=color,
    )


def make_slide(spec: dict, out: Path) -> None:
    src = Image.open(spec["screenshot"]).convert("RGB")
    if "crop" in spec:
        src = src.crop(tuple(spec["crop"]))

    canvas = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.text((92, 80), spec["title"], font=F_TITLE, fill=NAVY)
    if spec.get("subtitle"):
        draw.text((96, 160), spec["subtitle"], font=F_SUB, fill=NAVY)

    screenshot_box = tuple(spec.get("screenshot_box", [100, 220, 1320, 960]))
    shot, pos = fit_inside(src, screenshot_box)
    draw.rounded_rectangle((screenshot_box[0] - 12, screenshot_box[1] - 12, screenshot_box[2] + 12, screenshot_box[3] + 12), radius=16, outline=BAR_COLOR, width=4, fill=WHITE)
    canvas.paste(shot, pos)

    scale_x = shot.width / src.width
    scale_y = shot.height / src.height
    offset_x, offset_y = pos

    def map_point(pt):
        return int(offset_x + pt[0] * scale_x), int(offset_y + pt[1] * scale_y)

    for item in spec.get("boxes", []):
        x1, y1 = map_point((item["x"], item["y"]))
        x2, y2 = map_point((item["x"] + item["w"], item["y"] + item["h"]))
        draw.rounded_rectangle((x1, y1, x2, y2), radius=8, outline=item.get("color", RED), width=item.get("width", 6))

    for item in spec.get("arrows", []):
        arrow(draw, map_point(tuple(item["from"])), map_point(tuple(item["to"])), color=item.get("color", RED), width=item.get("width", 8))

    note_x = spec.get("notes_x", 1380)
    note_y = 250
    for idx, note in enumerate(spec.get("notes", []), 1):
        y = note_y + (idx - 1) * 170
        draw.rounded_rectangle((note_x, y, 1810, y + 126), radius=18, fill=LIGHT_BLUE, outline=BAR_COLOR, width=3)
        draw.ellipse((note_x + 22, y + 32, note_x + 82, y + 92), fill=BLUE)
        tw = draw.textbbox((0, 0), str(idx), font=F_BODY)[2]
        draw.text((note_x + 52 - tw / 2, y + 44), str(idx), font=F_BODY, fill=WHITE)
        draw_wrapped(draw, note, (note_x + 104, y + 28), F_BODY, 285, fill=NAVY)

    for label in spec.get("labels", []):
        x, y = map_point(tuple(label["at"]))
        text = label["text"]
        bbox = draw.textbbox((0, 0), text, font=F_SMALL)
        pad_x, pad_y = 14, 8
        draw.rounded_rectangle((x, y, x + bbox[2] + pad_x * 2, y + bbox[3] + pad_y * 2), radius=8, fill=label.get("fill", YELLOW), outline=BLACK, width=2)
        draw.text((x + pad_x, y + pad_y), text, font=F_SMALL, fill=label.get("color", BLACK))

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    specs = json.loads(args.spec.read_text(encoding="utf-8"))
    for i, spec in enumerate(specs, 1):
        make_slide(spec, args.out_dir / f"{i:02d}_{spec['slug']}.png")
    print(args.out_dir)


if __name__ == "__main__":
    main()
