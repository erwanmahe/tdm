#!/usr/bin/env bash
# Clean gallery entries in existing data.js files for all cities except arequipa.
# - For each */*/data.js (except amsud/arequipa/data.js):
#   * Parse the gallery array
#   * Remove any entries where:
#       - href basename starts with 'mini_'
#       - OR src contains 'mini_mini_'
#   * Write the file back preserving title, resume, backlinkHref and overall structure
#
# Usage:
#   ./scripts/clean_galleries.sh           # run cleaning
#
# Notes:
# - This script attempts to be robust by parsing only the gallery array as JSON-like content.
# - If a file cannot be parsed, it will be skipped with an error message.

set -uo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

shopt -s nullglob
TARGETS=()
for f in "$ROOT_DIR"/*/*/data.js; do
  [[ "$f" == "$ROOT_DIR/amsud/arequipa/data.js" ]] && continue
  TARGETS+=("$f")
done
shopt -u nullglob

echo "Found ${#TARGETS[@]} data.js files to clean"

updated=0
skipped=0
errors=0
for file in "${TARGETS[@]}"; do
  rel=${file#"$ROOT_DIR/"}
  echo "- Processing: $rel"
  if python3 - "$file" <<'PY'; then
import sys, os, json, re
path = sys.argv[1]
try:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        s = f.read()
    # Locate 'gallery:' then the first '[' and find its matching ']'
    m = re.search(r'\bgallery\s*:\s*\[', s)
    if not m:
        print("  ! No gallery array found; skip", file=sys.stderr)
        sys.exit(10)
    start_bracket = m.end() - 1  # points to the '['
    # Scan to matching closing bracket
    depth = 0
    i = start_bracket
    end_bracket = -1
    while i < len(s):
        ch = s[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end_bracket = i
                break
        elif ch == '"':
            # skip string literal to avoid miscounting brackets inside strings
            i += 1
            while i < len(s):
                if s[i] == '\\':
                    i += 2
                    continue
                if s[i] == '"':
                    break
                i += 1
        i += 1
    if end_bracket < 0:
        print("  ! Unterminated gallery array; skip", file=sys.stderr)
        sys.exit(11)

    inner = s[start_bracket+1:end_bracket]  # contents between [ ... ]
    # Build a JSON array string
    arr_text = '[' + inner + ']'
    try:
        arr = json.loads(arr_text)
    except Exception as e:
        # Try to remove trailing commas safely before ]
        arr_text2 = re.sub(r',\s*(\])', r'\1', arr_text)
        arr = json.loads(arr_text2)

    def is_thumb(entry):
        try:
            href = entry.get('href', '')
            src = entry.get('src', '')
        except AttributeError:
            return True
        # href basename starts with mini_
        base = os.path.basename(href)
        if base.startswith('mini_'):
            return True
        # src contains mini_mini_
        if 'mini_mini_' in src:
            return True
        return False

    cleaned = [e for e in arr if not is_thumb(e)]

    # Re-serialize with pretty formatting like the existing style
    def dump_entry(e):
        # Ensure keys order href, src, caption
        href = e.get('href', '')
        src = e.get('src', '')
        caption = e.get('caption', '')
        return (
            '  {'\
            + f'\n    "href": {json.dumps(href, ensure_ascii=False)},'\
            + f'\n    "src": {json.dumps(src, ensure_ascii=False)},'\
            + f'\n    "caption": {json.dumps(caption, ensure_ascii=False)}\n'\
            + '  }'
        )

    new_gallery = ''
    if cleaned:
        new_gallery = ',\n'.join(dump_entry(e) for e in cleaned) + '\n'

    # Replace the original gallery content
    new_s = s[:start_bracket+1] + '\n' + new_gallery + '  ' + s[end_bracket:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_s)
    print("  cleaned: removed", len(arr) - len(cleaned), "thumb entries")
except SystemExit as se:
    raise
except Exception as e:
    print("  ! Error:", e, file=sys.stderr)
    sys.exit(12)
PY
    ((updated++))
  else
    ((errors++))
  fi

done

echo "Done. Updated $updated, skipped $skipped, errors $errors."
