#!/usr/bin/env python3
"""Recursively replace .jpg files with same-dimension placeholder images."""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BG_COLOR = (40, 55, 80)        # dark muted blue
TEXT_COLOR = (255, 255, 255)   # white
TEXT = "placeholder"
SUBDIR_NAME = "placeholders"

FONT_CANDIDATES = [
    "DejaVuSans.ttf",
    "Arial.ttf",
    "arial.ttf",
    "Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def load_font(size):
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def fit_font_size(width, height, target_ratio=0.7):
    max_width = width * target_ratio
    max_height = height * target_ratio
    lo, hi = 4, max(8, min(width, height))
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        font = load_font(mid)
        bbox = font.getbbox(TEXT)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if tw <= max_width and th <= max_height:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return load_font(best)


def make_placeholder(width, height, out_path):
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    font = fit_font_size(width, height)
    bbox = draw.textbbox((0, 0), TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) / 2 - bbox[0]
    y = (height - th) / 2 - bbox[1]
    draw.text((x, y), TEXT, fill=TEXT_COLOR, font=font)
    img.save(out_path, "JPEG", quality=85)


def process_directory(directory, root):
    """Process .jpgs in one directory, skipping any 'placeholders' subdir."""
    if directory.name == SUBDIR_NAME:
        return 0, 0

    jpgs = [p for p in directory.iterdir()
            if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg")]

    if not jpgs:
        return 0, 0

    out_dir = directory / SUBDIR_NAME
    out_dir.mkdir(exist_ok=True)

    processed = 0
    skipped = 0
    for path in jpgs:
        try:
            with Image.open(path) as im:
                w, h = im.size
        except Exception as e:
            print(f"  SKIP {path.name}: {e}")
            skipped += 1
            continue

        out_path = out_dir / path.name
        make_placeholder(w, h, out_path)
        rel = path.relative_to(root)
        print(f"  {rel}  ->  {SUBDIR_NAME}/{path.name}  ({w}x{h})")
        processed += 1

    return processed, skipped


def main(directory):
    root = Path(directory).resolve()
    if not root.is_dir():
        sys.exit(f"Not a directory: {root}")

    print(f"Scanning {root} recursively...\n")

    total_processed = 0
    total_skipped = 0
    # rglob '*' walks all subdirectories; filter to dirs and skip placeholders dirs
    all_dirs = [root] + [p for p in root.rglob("*")
                         if p.is_dir() and p.name != SUBDIR_NAME
                         and SUBDIR_NAME not in p.parts]

    for d in all_dirs:
        p, s = process_directory(d, root)
        total_processed += p
        total_skipped += s

    print(f"\nDone. {total_processed} placeholder(s) created, {total_skipped} skipped.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    main(target)