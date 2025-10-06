#!/usr/bin/env bash
set -x
# Minimal script: scans all data.js files under current directory and
# updates only the backlinkHref line by replacing:
#   index.html (with or without an existing fragment)
# with:
#   index.html#<region>-<city>
# where <region>-<city> is derived from the path region/city/data.js.
# This script does NOT modify any index.html files.

modified=0
for f in $(find /home/emahe/Desktop/tdm -type f -name data.js); do
  dir=$(dirname "$f")
  city=$(basename "$dir")
  region=$(basename "$(dirname "$dir")")
  anchor="${region}-${city}"

  # Only operate on lines containing backlinkHref
    sed -i "s/index.html/index.html#${anchor}/" $f
    echo "Updated $f -> index.html#${anchor}"
    ((modified++))
done

echo "Done. Modified $modified files."
