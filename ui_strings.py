#!/usr/bin/env python3
"""Count Orbit's English interface sentences that appear word for word in a file.

Usage: ui_strings.py en.json FILE [FILE...]

Only sentences of 30 characters or more are counted, so short common words
such as "Cancel" or "Settings" can't inflate the result.
"""
import json
import sys

if len(sys.argv) < 3:
    sys.exit(__doc__)
with open(sys.argv[1], encoding="utf-8") as source:
    sentences = sorted(key for key in json.load(source) if len(key) >= 30)
print(f"{sys.argv[1]}: {len(sentences)} sentences of 30 or more characters")
for path in sys.argv[2:]:
    with open(path, "rb") as binary:
        data = binary.read()
    found = [s for s in sentences if s.encode() in data]
    print(f"{path}: {len(found)} found word for word, for example:")
    for sentence in found[:: max(1, len(found) // 5)][:5]:
        print(f"  {sentence}")
