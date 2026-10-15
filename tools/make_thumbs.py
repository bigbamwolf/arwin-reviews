#!/usr/bin/env python3
"""Write 300px wide WebP thumbnails to img/t/ for every poster in img/.
Review pages show posters at 150px and list pages at 60px, but ship the full
source JPG (median 183 KB, up to 3.6 MB). build_review_pages.py serves img/t/<name>.webp
through <picture> whenever the thumbnail exists, and keeps the JPG as fallback and og:image.
Requires Pillow. Idempotent, skips thumbnails newer than their source."""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "img")
DST = os.path.join(SRC, "t")
WIDTH = 300


def main():
    os.makedirs(DST, exist_ok=True)
    made = skipped = failed = 0
    before = after = 0
    for fn in sorted(os.listdir(SRC)):
        if not fn.lower().endswith((".jpg", ".jpeg", ".png")) or fn.startswith(("favicon", "apple-touch", "og-card")):
            continue
        src = os.path.join(SRC, fn)
        dst = os.path.join(DST, os.path.splitext(fn)[0] + ".webp")
        if os.path.exists(dst) and (os.environ.get("GITHUB_ACTIONS") or os.path.getmtime(dst) >= os.path.getmtime(src)):
            skipped += 1
            continue
        try:
            im = Image.open(src).convert("RGB")
            if im.width > WIDTH:
                im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
            im.save(dst, "WEBP", quality=78, method=6)
            before += os.path.getsize(src)
            after += os.path.getsize(dst)
            made += 1
        except Exception as e:
            failed += 1
            print("skip", fn, str(e)[:60], file=sys.stderr)
    print(f"thumbs: {made} made, {skipped} current, {failed} failed, {before // 1024} KB to {after // 1024} KB")


if __name__ == "__main__":
    main()
