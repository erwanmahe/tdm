#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/add_index_ids.sh [path_to_index_html]
# Adds id="<region>-<city>" to each city link in the root index.html sidebar
# based on its href="region/city/index.html", but only if the <a> has no id yet.
# Creates a backup index.html.bak

INDEX_HTML=${1:-index.html}
if [[ ! -f "$INDEX_HTML" ]]; then
  echo "Error: $INDEX_HTML not found" >&2
  exit 1
fi

cp "$INDEX_HTML" "$INDEX_HTML.bak"

# We use awk line-based processing; this assumes each <a class="link" ...> is on one line.
awk '
  {
    line = $0
    # If the line has a class="link" anchor with href like region/city/index.html
    # and it does NOT already contain an id= attribute, then insert id="region-city" after <a
    if (line ~ /<a[^>]*class="link"/ && line ~ /href="[a-z0-9]+\/[a-z0-9]+\/index\.html"/ && line !~ /[[:space:]]id="[^"]+"/) {
      # extract region and city
      match(line, /href="([a-z0-9]+)\/([a-z0-9]+)\/index\.html"/, m)
      if (m[1] != "" && m[2] != "") {
        id = m[1] "-" m[2]
        sub(/<a[[:space:]]+/, "<a id=\"" id "\" ", line)
      }
    }
    print line
  }
' "$INDEX_HTML.bak" > "$INDEX_HTML.tmp"

mv "$INDEX_HTML.tmp" "$INDEX_HTML"
echo "IDs added where missing in $INDEX_HTML. Backup: $INDEX_HTML.bak"
