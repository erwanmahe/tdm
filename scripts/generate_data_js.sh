#!/usr/bin/env bash
# Generate data.js for each city under a continent (default: amsud),
# following the model of amsud/arequipa/data.js
# The script extracts:
# - title: from <div class="titre">...</div>
# - resume: from <div class="resume">...</div>
# - gallery: from files under photos/ (recursively)
#   * href:  photos/<relative path to .jpg>
#   * src:   photos/<relative dir>/mini_<basename>.jpg
#   * caption: contents of matching .txt next to the image (if any)
#
# Usage:
#   ./scripts/generate_data_js.sh                 # default continent: amsud
#   ./scripts/generate_data_js.sh ausnz           # specify continent folder
#
# Notes:
# - Skips 'arequipa' (already has data.js)
# - If no .txt exists for an image, caption is empty string
# - data.js is written in each city folder (e.g., amsud/cuzco/data.js)
#
set -euo pipefail

CONTINENT=${1:-amsud}
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BASE_DIR="$ROOT_DIR/$CONTINENT"

if [[ ! -d "$BASE_DIR" ]]; then
  echo "Error: Continent directory not found: $BASE_DIR" >&2
  exit 1
fi

# Helper: Quote a string for a JS literal, preserving UTF-8 (no \u escapes)
json_quote() {
  python3 - "$1" <<'PY'
import sys, json
print(json.dumps(sys.argv[1], ensure_ascii=False))
PY
}

# Helper: read a file if it exists, output JSON-escaped string; otherwise empty quoted string
read_caption_json() {
  local path="$1"
  if [[ -f "$path" ]]; then
    # Read and escape (argument-based to preserve content reliably)
    local content
    content=$(cat "$path")
    json_quote "$content"
  else
    printf '""'
  fi
}

# Extract inner text for a given class using grep/sed, as requested
extract_div_text() {
  local file="$1" class="$2"
  # Use the pattern provided by the user, generalized for any class name
  # Assumes the target <div> is on a single line (which matches our pages)
  grep "class=\"$class\"" "$file" \
    | sed 's/.*'"$class"'">//' \
    | sed 's/<\/div>//' \
    | head -n1 \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}


printf 'Generating data.js in %s\n' "$BASE_DIR"

shopt -s nullglob
for city_dir in "$BASE_DIR"/*/; do
  [[ -d "$city_dir" ]] || continue
  city_name=$(basename "$city_dir")
  # Skip 'photos' pseudo dir if any and skip arequipa (already done)
  [[ "$city_name" == photos ]] && continue
  [[ "$city_name" == arequipa ]] && { echo "- Skipping arequipa"; continue; }

  index_html="$city_dir/index.html"
  photos_dir="$city_dir/photos"
  out_js="$city_dir/data.js"

  if [[ ! -f "$index_html" ]]; then
    echo "- Skipping $city_name (no index.html)"
    continue
  fi

  # Extract title and resume
  raw_title=$(extract_div_text "$index_html" 'titre')
  raw_resume=$(extract_div_text "$index_html" 'resume')

  echo "raw_title: $raw_title"
  echo "raw_resume: $raw_resume"

  # Strict requirement: only from div.titre and div.resume; default to empty when missing
  [[ -z "$raw_title" ]] && raw_title=""
  [[ -z "$raw_resume" ]] && raw_resume=""

  # JSON-escape them
  title_json=$(json_quote "$raw_title")
  resume_json=$(json_quote "$raw_resume")

  echo "title_json: $title_json"
  echo "resume_json: $resume_json"
  # Begin file
  {
    echo "// Per-page data for petite-vue. Works offline (file://) as plain JS."
    echo "window.TDM_PAGE = {"
    printf '  title: %s,\n' "$title_json"
    printf '  resume: %s,\n' "$resume_json"
    echo '  backlinkHref: "../../index.html",'
    echo '  gallery: ['

    first=1
    if [[ -d "$photos_dir" ]]; then
      # Find all jpg/jpeg images recursively
      while IFS= read -r -d '' img; do
        rel_path=${img#"$photos_dir/"}               # e.g., subdir/file.jpg or file.jpg
        dir_part=$(dirname "$rel_path")
        base=$(basename "$rel_path")                 # file.jpg
        name_no_ext=${base%.*}                         # file
        mini_path="$dir_part/mini_${name_no_ext}.jpg" # expected mini path (same dir)
        # Normalize mini path if no dir
        [[ "$dir_part" == "." ]] && mini_path="mini_${name_no_ext}.jpg"

        # Caption file path (same dir, .txt)
        cap_path="$photos_dir/${rel_path%.*}.txt"
        cap_json=$(read_caption_json "$cap_path")

        # Emit comma between items
        if [[ $first -eq 0 ]]; then echo ','; fi
        first=0

        printf '  {\n'
        printf '    "href": %s,\n' "$(printf '"photos/%s"' "$rel_path")"
        printf '    "src": %s,\n'  "$(printf '"photos/%s"' "$mini_path")"
        printf '    "caption": %s\n' "$cap_json"
        printf '  }'
      done < <(find "$photos_dir" -type f \( -iname '*.jpg' -o -iname '*.jpeg' \) -print0 | sort -z)
    fi

    echo ''
    echo '  ]'
    echo '};'
  } > "$out_js"

  echo "- Wrote $out_js"

done
shopt -u nullglob

echo "Done."
