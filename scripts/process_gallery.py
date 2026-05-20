#!/usr/bin/env python3
"""Resize + recompress _inbox images into gallery slots."""
import sys
from pathlib import Path
from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

INBOX = Path("/mnt/c/Users/zindelj/Documents/TizzuLab/zindellab/assets/gallery/_inbox")
OUT = Path("/mnt/c/Users/zindelj/Documents/TizzuLab/zindellab/assets/gallery")
MAX_EDGE = 1600
QUALITY = 82

exts = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}
files = sorted([p for p in INBOX.iterdir() if p.suffix.lower() in exts])
print(f"found {len(files)} source images")

for i, src in enumerate(files, start=1):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    w, h = im.size
    scale = MAX_EDGE / max(w, h)
    if scale < 1:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    out = OUT / f"{i:02d}.jpg"
    im.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    kb = out.stat().st_size / 1024
    print(f"  {src.name:50s} -> {out.name}  {im.size[0]}x{im.size[1]}  {kb:.0f} KB")

print("done")
