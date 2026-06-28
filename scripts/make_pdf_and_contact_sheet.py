#!/usr/bin/env python3
"""Make a PDF and contact sheet from slide PNG/JPG images.

Usage:
  python make_pdf_and_contact_sheet.py input_dir --out output.pdf
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def list_images(input_dir: Path) -> list[Path]:
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    return sorted(p for p in input_dir.iterdir() if p.suffix.lower() in exts and not p.name.startswith("contact_sheet"))


def fit_16x9(im: Image.Image, size=(1920, 1080)) -> Image.Image:
    im = im.convert("RGB")
    canvas = Image.new("RGB", size, "white")
    w, h = im.size
    target_w, target_h = size
    scale = min(target_w / w, target_h / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = im.resize((nw, nh), Image.LANCZOS)
    canvas.paste(resized, ((target_w - nw) // 2, (target_h - nh) // 2))
    return canvas


def make_pdf(images: list[Path], out_pdf: Path) -> None:
    pages = [fit_16x9(Image.open(p)) for p in images]
    if not pages:
        raise SystemExit("No images found")
    pages[0].save(out_pdf, save_all=True, append_images=pages[1:], resolution=96.0)


def make_contact_sheet(images: list[Path], out_png: Path) -> None:
    thumbs = []
    for i, p in enumerate(images, 1):
        im = fit_16x9(Image.open(p))
        im.thumbnail((320, 180))
        cell = Image.new("RGB", (340, 230), (245, 247, 250))
        cell.paste(im, (10, 10))
        draw = ImageDraw.Draw(cell)
        draw.text((12, 198), f"{i:02d} {p.name}", fill=(0, 0, 0))
        thumbs.append(cell)
    cols = 3
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 340, rows * 230), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % cols) * 340, (i // cols) * 230))
    sheet.save(out_png)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--contact-sheet", type=Path)
    args = parser.parse_args()

    images = list_images(args.input_dir)
    make_pdf(images, args.out)
    if args.contact_sheet:
        make_contact_sheet(images, args.contact_sheet)
    print(args.out)


if __name__ == "__main__":
    main()

