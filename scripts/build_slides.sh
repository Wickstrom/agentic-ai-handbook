#!/usr/bin/env bash
# Export every Marimo lecture to a standalone WASM page under _slides/, and
# copy the landing page next to them. Mirrors what the GitHub Actions workflow
# does, so the site can be previewed locally before pushing.
#
# Usage: ./scripts/build_slides.sh

set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is not installed — see https://docs.astral.sh/uv/" >&2
  exit 1
fi

rm -rf _slides
mkdir -p _slides

shopt -s nullglob
notebooks=(notebooks/*/*.py)

if [ ${#notebooks[@]} -eq 0 ]; then
  echo "error: no notebooks found under notebooks/*/*.py" >&2
  exit 1
fi

for nb in "${notebooks[@]}"; do
  dir=$(dirname "$nb")
  base=$(basename "$nb" .py)
  target="_slides/$dir/$base"
  mkdir -p "$target"

  # Media (if any) must sit next to the exported HTML so relative paths resolve.
  if [ -d "$dir/media" ]; then
    cp -R "$dir/media" "$target/"
  fi

  echo "exporting $nb -> $target"
  # --no-show-code keeps the published deck looking like slides; code remains
  # visible in `marimo edit` locally.
  uv run marimo export html-wasm "$nb" -o "$target" --mode run --no-show-code
done

cp index.html _slides/index.html
touch _slides/.nojekyll

echo "done: _slides/ ($(find _slides -name index.html | wc -l | tr -d ' ') page(s))"
echo "preview: python3 -m http.server -d _slides 8000"
