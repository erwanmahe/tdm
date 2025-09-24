#!/usr/bin/env bash
# Rewrite every continent/city/index.html (except arequipa) using arequipa/index.html as a template.
# Steps per city:
# 1) Extract and preserve the city's <div class="texte"> ... </div> block
# 2) Delete existing index.html
# 3) Write new index.html as: [arequipa lines 1-68] + preserved texte + [arequipa lines 278-305]
#
# Usage:
#   ./scripts/rewrite_city_pages.sh           # dry-run: shows what would be updated
#   ./scripts/rewrite_city_pages.sh --write   # actually rewrite files
#
# Notes:
# - This relies on the current line numbers in amsud/arequipa/index.html
# - Parsing of <div class="texte"> is done with a small Python HTML-aware matcher
# - Back up your repo beforehand or rely on git for safety

# Be resilient: don't abort on first non-zero command; still treat unset as error
set -u

WRITE=0
if [[ ${1:-} == "--write" ]]; then
  WRITE=1
fi

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TEMPLATE="$ROOT_DIR/amsud/arequipa/index.html"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "Template not found: $TEMPLATE" >&2
  exit 1
fi

# Extract header and footer slices from template (lines are 1-based)
HEADER=$(sed -n '1,68p' "$TEMPLATE")
FOOTER=$(sed -n '278,305p' "$TEMPLATE")

if [[ -z "$HEADER" || -z "$FOOTER" ]]; then
  echo "Failed to extract header/footer from template. Check line numbers." >&2
  exit 1
fi

# Python helper to extract the exact <div class="texte">...</div> block with balanced <div> nesting.
extract_texte_py() {
  python3 - "$1" <<'PY'
import sys, re
try:
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    # Find the start of <div class="texte">
    start = re.search(r'<div\s+class=["\']texte["\']\s*>', html)
    if not start:
        # Not found: emit nothing and exit 0 so the caller can choose a default
        sys.exit(0)
    idx = start.end()
    # Walk forward counting div nesting until matching </div>
    # Initialize depth at 1 for the texte div
    depth = 1
    pos = idx
    while depth > 0 and pos < len(html):
        m = re.search(r'<div\b|</div\s*>', html[pos:])
        if not m:
            break
        token = m.group(0)
        pos = pos + m.start()
        if token.startswith('<div'):
            depth += 1
            pos += len(token)
        else:
            depth -= 1
            pos += len(token)
    # Slice the complete block
    block = html[start.start():pos]
    # Emit the block exactly as found
    sys.stdout.write(block)
except Exception:
    # On any parsing error, emit nothing
    pass
PY
}

# Find all city index.html files via globbing (continent/city/index.html), except arequipa
shopt -s nullglob
CITY_INDEXES=()
for f in "$ROOT_DIR"/*/*/index.html; do
  [[ "$f" == "$ROOT_DIR/amsud/arequipa/index.html" ]] && continue
  CITY_INDEXES+=("$f")
done
shopt -u nullglob

echo "Found ${#CITY_INDEXES[@]} city pages to process"

updated=0
skipped=0
errors=0
defaults_used=0
for f in "${CITY_INDEXES[@]}"; do
  rel=${f#"$ROOT_DIR/"}
  echo "Processing: $rel"
  # Extract texte block
  TEXTE=$(extract_texte_py "$f" || true)
  if [[ -z "$TEXTE" ]]; then
    # Inject default texte block
    TEXTE=$'\n<div id="texte"></div>\n<div class="texte">\n  <p></p>\n  <a class="backtop" href="#top">Revenir en haut</a>\n</div>'
    ((defaults_used++))
  fi

  # Verbose logging: show the texte content that will be inserted
  echo "--- $rel: <div class=\"texte\"> content ---"
  printf '%s\n' "$TEXTE"
  echo "--- end texte for $rel ---"

  # Compose new content
  NEW_CONTENT="$HEADER
$TEXTE
$FOOTER
"

  if [[ $WRITE -eq 0 ]]; then
    echo "- DRY-RUN: would update $rel"
    ((updated++))
    continue
  fi

  # Overwrite file safely
  tmp="$f.tmp.$$"
  printf '%s' "$NEW_CONTENT" > "$tmp"
  mv "$tmp" "$f"
  echo "- Updated $rel"
  ((updated++))

done

echo "Done. Updated $updated, skipped $skipped, errors $errors, defaults_used $defaults_used."
