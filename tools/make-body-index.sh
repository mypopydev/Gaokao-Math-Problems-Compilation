#!/bin/sh
# Generate tmp/body.tex: a filtered concatenation of the per-year index
# files, used as the document body so a subset of regions can be compiled
# without editing the (many) index/YYYY.tex files.
#
# Usage: tools/make-body-index.sh <AREA> <OUT>
#   AREA=all  -> include every \input line from every index/YYYY.tex
#   otherwise -> include only \input lines whose path contains <AREA>
#                (e.g. "shanghai" matches shanghai, shanghai_spring,
#                 shanghai_science, shanghai_liberal)
#
# Years are emitted in descending order so the output matches the order of
# the full document (newest first). A year with no matching \input line is
# skipped entirely, avoiding empty year headings.
set -e

AREA="$1"
OUT="$2"

if [ -z "$AREA" ] || [ -z "$OUT" ]; then
    echo "make-body-index: usage: $0 <AREA> <OUT>" >&2
    exit 2
fi

mkdir -p "$(dirname "$OUT")"
: > "$OUT"

for f in $(ls index/[0-9][0-9][0-9][0-9].tex 2>/dev/null | sort -r); do
    year=$(basename "$f" .tex)
    if [ "$AREA" = "all" ]; then
        lines=$(grep -E '^[[:space:]]*\\input\{' "$f" || true)
    else
        # Fixed-string substring match on the region token in the path.
        lines=$(grep -E '^[[:space:]]*\\input\{' "$f" | grep -F "$AREA" || true)
    fi
    if [ -n "$lines" ]; then
        printf '\\examyear{%s年}%%\n\n' "$year" >> "$OUT"
        printf '%s\n' "$lines" >> "$OUT"
        printf '\n' >> "$OUT"
    fi
done

echo "make-body-index: wrote $OUT (area=$AREA)"
