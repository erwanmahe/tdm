#!/usr/bin/env bash
# Create a photos/ folder in each city folder under CONTINENT/ and place media inside it.
# Usage:
#   ./scripts/migrate_photos.sh            # default: copy files/folders into photos/
#   ./scripts/migrate_photos.sh move       # move files/folders into photos/
# Notes:
# - Default action is COPY to be safe. Pass "move" to relocate instead of duplicating.
# - Copies/Moves:
#   * Top-level *.jpg, *.jpeg, *.png, *.txt files inside each city folder
#   * All top-level subfolders (e.g., bota/, pano/) except an existing photos/
# - Existing files are not overwritten during copy (cp -n). Re-run is safe.

set -euo pipefail

MODE=${1:-copy}      # "copy" (default) or "move"
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CONTINENT_DIR="$ROOT_DIR/ausnz"

if [[ ! -d "$CONTINENT_DIR" ]]; then
  echo "Error: Could not find CONTINENT directory at $CONTINENT_DIR" >&2
  exit 1
fi

shopt -s nullglob dotglob

echo "Starting migration in: $CONTINENT_DIR (mode: $MODE)"

total_cities=0
for city_dir in "$CONTINENT_DIR"/*/ ; do
  # Skip non-directories or unexpected paths
  [[ -d "$city_dir" ]] || continue

  city_name=$(basename "$city_dir")

  # Skip top-level pages like CONTINENT/photos if any (defensive)
  if [[ "$city_name" == "photos" ]]; then
    continue
  fi

  # User request: do not migrate 'arequipa'
  if [[ "$city_name" == "arequipa" ]]; then
    printf "\n--- Skipping city (per request): %s\n" "$city_name"
    continue
  fi

  (( ++total_cities ))
  printf "\n--- Processing city: %s\n" "$city_name"

  photos_dir="$city_dir/photos"
  mkdir -p "$photos_dir"

  # Collect files to move/copy
  files=(
    "$city_dir"*.jpg "$city_dir"*.JPG "$city_dir"*.jpeg "$city_dir"*.JPEG
    "$city_dir"*.png "$city_dir"*.PNG "$city_dir"*.txt
  )

  # Collect subdirectories (top-level only), excluding photos/
  subdirs=()
  for d in "$city_dir"*/ ; do
    [[ -d "$d" ]] || continue
    [[ "$(basename "$d")" == "photos" ]] && continue
    subdirs+=("$d")
  done

  # Perform action for files
  if (( ${#files[@]} > 0 )); then
    if [[ "$MODE" == "move" ]]; then
      echo "  Moving files -> photos/: ${#files[@]}"
      mv -t "$photos_dir" "${files[@]}" || true
    else
      echo "  Copying files -> photos/: ${#files[@]}"
      # -n no clobber, -p preserve timestamps/mode
      cp -n -p -t "$photos_dir" "${files[@]}" || true
    fi
  else
    echo "  No top-level media files to process."
  fi

  # Perform action for subdirectories
  if (( ${#subdirs[@]} > 0 )); then
    if [[ "$MODE" == "move" ]]; then
      echo "  Moving folders -> photos/: ${#subdirs[@]}"
      mv -t "$photos_dir" "${subdirs[@]}" || true
    else
      echo "  Copying folders -> photos/: ${#subdirs[@]}"
      # -a archive (preserve), trailing slash safe; cp -n doesn't apply to dirs, so we handle collisions
      for d in "${subdirs[@]}"; do
        base=$(basename "$d")
        if [[ -e "$photos_dir/$base" ]]; then
          echo "    Skipping folder (already exists): $base"
        else
          cp -a "$d" "$photos_dir/"
        fi
      done
    fi
  else
    echo "  No subfolders to process."
  fi

  # If photos/ ended up empty, remove it
  if [[ -d "$photos_dir" ]]; then
    if [[ -z "$(find "$photos_dir" -mindepth 1 -print -quit)" ]]; then
      rmdir "$photos_dir"
      echo "  Removed empty photos/ folder."
    fi
  fi

done

shopt -u nullglob dotglob

echo "\nDone. Processed $total_cities city folder(s)."
