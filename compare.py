#!/usr/bin/env python3
"""Compare the application functions of two unstripped PS5 payload ELFs.

Usage: compare.py OTHER.elf ORBIT.elf

A function belongs to the application when its own debug information places
it in backend/, launcher/ or orbit.h. Two functions match when their
instructions are the same once addresses are blanked out, because the two
programs are laid out differently in memory.

Needs nm and an objdump that reads x86-64: plain objdump on x86-64 Linux,
otherwise x86_64-linux-gnu-objdump or llvm-objdump. Set OBJDUMP to choose.
"""
import os
import re
import shutil
import subprocess
import sys

APP = re.compile(r"/work/((?:backend|launcher)/[^:]+|orbit\.h):\d+$")
HEADER = re.compile(r"^([0-9a-f]+) <.+>:$")
ADDRESS = re.compile(r"^\s*[0-9a-f]+:\s*")
TARGET = re.compile(r"(?:0x)?[0-9a-f]+ <([^>]+)>")
RIP = re.compile(r"-?0x[0-9a-f]+\(%rip\)")
OBJDUMP = os.environ.get("OBJDUMP") or next(
    (tool for tool in ("x86_64-linux-gnu-objdump", "llvm-objdump") if shutil.which(tool)),
    "objdump")


def run(*command):
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout


def functions(path):
    """The application's functions: (source file, name) -> address."""
    found = {}
    for line in run("nm", "-l", "--defined-only", path).splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4 or parts[1] not in "Tt":
            continue
        place = APP.search(parts[3].split("\t")[-1])
        if place:
            found.setdefault((place.group(1), parts[2]), int(parts[0], 16))
    return found


def instructions(path, wanted):
    """Instructions of the functions at the wanted addresses, addresses blanked."""
    result, start, body = {}, None, None
    for line in run(OBJDUMP, "-d", "--no-show-raw-insn", "-j", ".text", path).splitlines():
        header = HEADER.match(line)
        if header:
            if start in wanted:
                result[start] = body
            start, body = int(header.group(1), 16), []
            continue
        if body is None or not ADDRESS.match(line):
            continue
        insn = ADDRESS.sub("", line).split("#")[0].strip()
        if insn:
            insn = TARGET.sub(lambda m: "<" + re.sub(r"\+0x[0-9a-f]+$", "", m.group(1)) + ">", insn)
            body.append(re.sub(r"\s+", " ", RIP.sub("X(%rip)", insn)))
    if start in wanted:
        result[start] = body
    return result


def main(other_path, orbit_path):
    other, orbit = functions(other_path), functions(orbit_path)
    shared = other.keys() & orbit.keys()
    theirs = instructions(other_path, {other[k] for k in shared})
    ours = instructions(orbit_path, {orbit[k] for k in shared})
    same = {k for k in shared if theirs.get(other[k]) and theirs[other[k]] == ours.get(orbit[k])}
    files = sorted({f for f, _ in other})

    print(f"{other_path}: {len(other)} application functions in {len(files)} source files")
    print(f"  {len(shared)} have the same name, in the same file, in {orbit_path}")
    print(f"  {len(same)} of those have the same instructions\n")
    print(f"{'source file':28} {'functions':>9} {'same name':>9} {'same code':>9}")
    for f in files:
        print(f"{f:28} {sum(k[0] == f for k in other):9} "
              f"{sum(k[0] == f for k in shared):9} {sum(k[0] == f for k in same):9}")
    print(f"\nOnly in {other_path}:")
    for f, name in sorted(other.keys() - orbit.keys()):
        print(f"  {f}: {name}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
