#!/bin/sh
# Reproduces the findings on https://saawant12.github.io/blackbox-gpl/
#
#   sh check.sh [BlackBox release tag]      default v1.0.8
#
# Needs curl, python3, and binutils that can read x86-64 (plain binutils on
# x86-64 Linux, binutils-x86-64-linux-gnu or llvm elsewhere). Nothing is run
# from the downloaded files; they are only read.
set -eu

tag=${1:-v1.0.8}
orbit=v0.9.1
kit=$(cd "$(dirname "$0")" && pwd)
work=${WORK:-$PWD/blackbox-check}
mkdir -p "$work"
cd "$work"

bb=blackbox-$tag.elf
ob=orbit-$orbit.elf
en=$kit/orbit-$orbit-en.json

fetch() {
  [ -s "$2" ] || curl -fsSL -o "$2" "$1"
}
fetch "https://github.com/D3ATHLY/blackbox/releases/download/$tag/blackbox.elf" "$bb"
fetch "https://github.com/saawant12/orbit-store-ps5/releases/download/$orbit/orbit_store.elf" "$ob"

hash() {
  if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1
}
section() {
  printf '\n== %s\n' "$1"
}

section "Files"
for file in "$bb" "$ob" "$en"; do
  sum=$(hash "$file")
  expected=$(awk -v f="${file##*/}" '$2 == f { print $1 }' "$kit/SHA256SUMS")
  if [ -z "$expected" ]; then note="(not in SHA256SUMS)"
  elif [ "$sum" = "$expected" ]; then note="(same file the page examined)"
  else note="(DIFFERENT from the file the page examined: $expected)"
  fi
  echo "$sum  ${file##*/} $note"
done

sources() {
  readelf -p .debug_line_str "$1" 2>/dev/null | grep -oE '[^ ]+\.[ch]$' |
    grep -E '^(backend|launcher)/|^orbit\.h$' | sort -u
}
section "1. Application source files named in $bb's own debug information"
sources "$ob" > orbit-sources.txt
sources "$bb" | while read -r file; do
  if grep -qx "$file" orbit-sources.txt; then echo "$file  (also in Orbit $orbit)"
  else echo "$file  (BlackBox only)"
  fi
done

section "2. Build directories recorded by the compiler"
for file in "$bb" "$ob"; do
  echo "$file:"
  readelf --debug-dump=info "$file" 2>/dev/null | grep DW_AT_comp_dir |
    sed 's/.*: //' | sort -u | sed 's/^/  /'
done

section "3. Launcher ownership string (Orbit's launcher/install.c, line 15)"
for file in "$ob" "$bb"; do
  printf '%s: ' "$file"
  strings -a -n 8 "$file" | grep -m1 -E 'ORBT00001 launcher v1|BLKB00001 launcher v1'
done

section "4. Orbit names still in $bb"
nm --defined-only "$bb" | awk '{ print $3 }' | grep -E '^orbit_' | sort -u | tr '\n' ' '
echo
printf "Orbit's TV app ID PPSA99177 appears %s times\n" \
  "$(strings -a -n 8 "$bb" | grep -o PPSA99177 | wc -l | tr -d ' ')"

section "5. Functions compared with Orbit $orbit"
python3 -I "$kit/compare.py" "$bb" "$ob"

section "6. Orbit $orbit interface text in $bb"
python3 -I "$kit/ui_strings.py" "$en" "$bb" | sed "s|$kit/||"

section "7. Licence and source in the BlackBox repository"
curl -fsSL https://api.github.com/repos/D3ATHLY/blackbox | python3 -Ic \
  'import json,sys; print("licence detected by GitHub:", json.load(sys.stdin)["license"])'
curl -fsSL https://api.github.com/repos/D3ATHLY/blackbox/contents | python3 -Ic \
  'import json,sys; print("top-level files:", ", ".join(i["name"] for i in json.load(sys.stdin)))'
