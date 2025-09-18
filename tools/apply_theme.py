#!/usr/bin/env python3
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static_site"
ASSETS_SRC = ROOT / "tools" / "theme_assets"
ASSETS_DST = OUT / "assets"

HEAD_INJECT = """
  <!-- Theme fonts and styles -->
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Material+Icons&display=swap\" rel=\"stylesheet\">
  <link rel=\"stylesheet\" href=\"{rel}assets/theme.css\" />
  <link rel=\"stylesheet\" href=\"{rel}assets/lightbox.css\" />
"""

BODY_INJECT = """
  <!-- Theme scripts -->
  <script src=\"{rel}assets/lightbox.js\"></script>
  <script src=\"{rel}assets/theme.js\"></script>
"""


def rel_prefix_for(path_out: Path) -> str:
    depth = len(path_out.relative_to(OUT).parts) - 1
    if depth <= 0:
        return ""
    return "../" * depth


def copy_assets():
    ASSETS_DST.mkdir(parents=True, exist_ok=True)
    for name in ("theme.css", "theme.js", "lightbox.css", "lightbox.js"):
        dst = ASSETS_DST / name
        src = ASSETS_SRC / name
        data = src.read_bytes()
        dst.write_bytes(data)


def inject_into_html(path: Path):
    html = path.read_text(encoding="utf-8")
    rel = rel_prefix_for(path)

    # Head styles: place before </head>
    if "assets/theme.css" not in html:
        html = re.sub(r"</head>", HEAD_INJECT.format(rel=rel) + "\n</head>", html, flags=re.IGNORECASE)

    # Body scripts: place before </body>
    if "assets/theme.js" not in html:
        html = re.sub(r"</body>", BODY_INJECT.format(rel=rel) + "\n</body>", html, flags=re.IGNORECASE)

    # Add data attributes to gallery links for lightbox grouping if needed
    # build_static.py already outputs anchors within .gallery; we just ensure they have class
    def add_gallery_attrs(m):
        a_tag = m.group(0)
        if 'data-lightbox' in a_tag:
            return a_tag
        # Group per page
        return a_tag.replace('<a ', '<a data-lightbox="gallery" ')

    html = re.sub(r"<a\s+href=\"[^\"]+\"\s*>", add_gallery_attrs, html)

    path.write_text(html, encoding="utf-8")


def main():
    assert OUT.exists(), f"Output dir not found: {OUT}. Run build_static.py first."
    # Copy theme assets
    copy_assets()
    # Inject all html files
    for root, _, files in os.walk(OUT):
        for f in files:
            if not f.lower().endswith('.html'):
                continue
            inject_into_html(Path(root) / f)
    print("Applied theme assets and injections to static_site/")


if __name__ == "__main__":
    main()
