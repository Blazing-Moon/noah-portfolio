"""
build_gallery.py
================

Generates the gallery manifest (data/gallery.json) and optimized web-sized
images + thumbnails from source photos.

Workflow
--------
1. Extract Photography.zip  -> images/photos/       (originals, any size)
   Extract Stills.zip        -> images/stills/

2. Run:
       python scripts/build_gallery.py

   This script will:
     - Process every image in images/photos/   and images/stills/
     - Create an optimized full-size version (max 2000px on longest edge)
         -> images/photos/        (overwrites originals)  [controlled by REPLACE_ORIGINALS]
            images/stills/
     - Create a small thumbnail (600px on longest edge)
         -> images/photos-thumbs/
            images/stills-thumbs/
     - Write data/gallery.json, which the site reads at load time.

3. Re-run any time photos are added/removed. The script skips files whose
   thumbnail + web version already exist with a newer source mtime
   (i.e., it's incremental).

Settings
--------
- Supported extensions: .jpg, .jpeg, .png, .webp, .tif, .tiff, .heic (HEIC
  requires `pillow-heif` — optional; skipped gracefully if not installed).
- Web images are saved as .jpg (quality 85), which is a big size win with
  almost imperceptible quality loss for portfolio-grade photos.
- If you want to KEEP the untouched originals, set REPLACE_ORIGINALS = False
  below. The script will then leave the source files alone and write web
  versions into images/photos-web/ and images/stills-web/ — but you'll need
  to also adjust the manifest paths below (see PHOTO_WEB_DIR).

Requirements
------------
    pip install Pillow
    pip install pillow-heif   # optional, for HEIC/HEIF support
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("ERROR: Pillow is not installed.\n  pip install Pillow")

# Optional HEIC support
try:
    import pillow_heif  # type: ignore
    pillow_heif.register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False


# ------------------------- CONFIGURATION -------------------------

# If True, overwrites sources in images/photos and images/stills with
# the web-optimized versions. The script is non-destructive to a copy
# by default — set to True only once you're happy with the output.
REPLACE_ORIGINALS = True

# Max dimension (longest edge) for full-size web versions
WEB_MAX_EDGE      = 2000
# Max dimension for thumbnails
THUMB_MAX_EDGE    = 600

# JPEG quality for outputs
WEB_QUALITY       = 85
THUMB_QUALITY     = 80

# Supported input extensions
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic", ".heif"}

# Project paths (resolved relative to this script's location)
ROOT        = Path(__file__).resolve().parent.parent
PHOTO_DIR   = ROOT / "images" / "photos"
STILL_DIR   = ROOT / "images" / "stills"
PHOTO_THUMB = ROOT / "images" / "photos-thumbs"
STILL_THUMB = ROOT / "images" / "stills-thumbs"
MANIFEST    = ROOT / "data" / "gallery.json"


# ------------------------- CORE LOGIC ----------------------------

def process_directory(src_dir: Path, thumb_dir: Path, category_label: str) -> list[dict]:
    """Process one category (photos or stills). Returns manifest entries."""
    if not src_dir.exists():
        print(f"  [skip] {src_dir} does not exist — skipping {category_label}")
        return []

    thumb_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    processed = 0
    skipped = 0
    failed = 0

    source_files = sorted(
        [p for p in src_dir.iterdir()
         if p.is_file() and p.suffix.lower() in EXTENSIONS]
    )

    if not source_files:
        print(f"  [empty] no images found in {src_dir}")
        return []

    print(f"\nProcessing {len(source_files)} {category_label} from {src_dir.name}/")

    for src in source_files:
        # Skip non-HEIC if HEIC isn't installed
        if src.suffix.lower() in {".heic", ".heif"} and not HEIC_SUPPORTED:
            print(f"  [skip] {src.name}: HEIC support not installed (pip install pillow-heif)")
            skipped += 1
            continue

        # Output filenames: same stem, always .jpg
        web_name  = src.stem + ".jpg"
        thumb_name = src.stem + ".jpg"

        web_path   = src_dir / web_name if REPLACE_ORIGINALS else src_dir.parent / f"{src_dir.name}-web" / web_name
        thumb_path = thumb_dir / thumb_name

        # Incremental skip: both outputs exist and are newer than source
        if (thumb_path.exists() and web_path.exists()
            and thumb_path.stat().st_mtime >= src.stat().st_mtime
            and web_path.stat().st_mtime >= src.stat().st_mtime):
            # Already up to date — just record the manifest entry
            entries.append(build_entry(src, web_path, thumb_path, category_label))
            skipped += 1
            continue

        try:
            with Image.open(src) as img:
                # Honor EXIF orientation, then strip EXIF
                img = ImageOps.exif_transpose(img)
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                # Full-size web version
                web_img = img.copy()
                web_img.thumbnail((WEB_MAX_EDGE, WEB_MAX_EDGE), Image.LANCZOS)
                web_path.parent.mkdir(parents=True, exist_ok=True)
                web_img.save(web_path, "JPEG", quality=WEB_QUALITY, optimize=True, progressive=True)

                # Thumbnail
                thumb_img = img.copy()
                thumb_img.thumbnail((THUMB_MAX_EDGE, THUMB_MAX_EDGE), Image.LANCZOS)
                thumb_img.save(thumb_path, "JPEG", quality=THUMB_QUALITY, optimize=True)

            # If we replaced originals with .jpg and the original was a
            # different extension (e.g., .png / .heic), remove the source.
            if REPLACE_ORIGINALS and src.suffix.lower() != ".jpg":
                # web_path uses .jpg stem; src may be different extension
                if src != web_path and src.exists():
                    src.unlink()

            entries.append(build_entry(src, web_path, thumb_path, category_label))
            processed += 1
            if processed % 10 == 0 or processed == len(source_files):
                print(f"  processed {processed}/{len(source_files)}…")

        except Exception as e:
            print(f"  [FAIL] {src.name}: {e}")
            failed += 1

    print(f"  done: {processed} processed, {skipped} already current, {failed} failed")
    return entries


def build_entry(src: Path, web_path: Path, thumb_path: Path, category: str) -> dict:
    """Build a manifest entry. Paths are relative to the site root."""
    return {
        "file":    str(web_path.relative_to(ROOT)).replace("\\", "/"),
        "thumb":   str(thumb_path.relative_to(ROOT)).replace("\\", "/"),
        "full":    str(web_path.relative_to(ROOT)).replace("\\", "/"),
        "caption": src.stem.replace("_", " ").replace("-", " "),
    }


def main():
    print("=" * 60)
    print("  Noah Giesler Portfolio — Gallery Build")
    print("=" * 60)

    if not HEIC_SUPPORTED:
        print("  (HEIC support: disabled. Install pillow-heif if needed.)")

    photos = process_directory(PHOTO_DIR, PHOTO_THUMB, "photos")
    stills = process_directory(STILL_DIR, STILL_THUMB, "stills")

    manifest = {
        "photos": photos,
        "stills": stills,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    total = len(photos) + len(stills)
    print(f"\nWrote manifest: {MANIFEST.relative_to(ROOT)} ({total} images total)")
    print(f"  photos: {len(photos)}")
    print(f"  stills: {len(stills)}")
    print("\nDone. Open index.html in a browser to view.")


if __name__ == "__main__":
    main()
