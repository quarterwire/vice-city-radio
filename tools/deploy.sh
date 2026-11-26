#!/usr/bin/env bash
# Publish the committed site files (and nothing else) to the gh-pages branch, which GitHub Pages serves.
# Usage: bash tools/deploy.sh
set -euo pipefail
repo=$(git rev-parse --show-toplevel)
cd "$repo"
files="index.html legal.html app.js stations.js logos bg fonts"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir "$tmp/site"
git archive HEAD $files | tar -x -C "$tmp/site"
touch "$tmp/site/.nojekyll"   # serve files as-is, no Jekyll processing

# refuse to publish anything unexpected
bad=$(cd "$tmp/site" && find . -type f ! -name '*.html' ! -name '*.js' ! -name '*.webp' ! -name '*.woff2' ! -name 'OFL.txt' ! -name '.nojekyll')
if [ -n "$bad" ]; then echo "Unexpected files, not deploying:"; echo "$bad"; exit 1; fi

export GIT_INDEX_FILE="$tmp/index"
tree=$(cd "$tmp/site" && git --git-dir="$repo/.git" --work-tree=. add -A && git --git-dir="$repo/.git" write-tree)
unset GIT_INDEX_FILE
parent=$(git rev-parse -q --verify refs/heads/gh-pages || true)
if [ -n "$parent" ] && [ "$(git rev-parse "$parent^{tree}")" = "$tree" ]; then echo "gh-pages is already up to date"; exit 0; fi
commit=$(git commit-tree "$tree" ${parent:+-p "$parent"} -m "Deploy $(git rev-parse --short HEAD)")
git update-ref refs/heads/gh-pages "$commit"
git push origin gh-pages
echo "Deployed $(git rev-parse --short HEAD). GitHub Pages updates in about a minute."
