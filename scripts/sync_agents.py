#!/usr/bin/env python3
"""Copy the shared agent guide into a repository checkout."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

START = b"<!-- qso-graph:shared:start -->"
END = b"<!-- qso-graph:shared:end -->"
CANONICAL = Path(__file__).resolve().parent.parent / "AGENTS-SHARED.md"


def block_span(data: bytes) -> tuple[int, int] | None:
    """Find the sole complete block, rejecting ambiguous or incomplete markers."""
    starts, ends = data.count(START), data.count(END)
    if starts == ends == 0:
        return None
    if starts != 1 or ends != 1:
        raise ValueError("Expected exactly one pair of shared block markers")
    start, end = data.index(START), data.index(END)
    if end < start:
        raise ValueError("Shared block markers are out of order")
    return start, end + len(END)


def canonical_block() -> bytes:
    data = CANONICAL.read_bytes()
    span = block_span(data)
    if span is None or data[:span[0]].strip() or data[span[1]:].strip():
        raise ValueError("Invalid canonical shared block")
    return data[span[0]:span[1]]


def synchronize(root: Path, check: bool = False) -> bool:
    """Write the guide and return whether the existing block was current."""
    block = canonical_block()
    guide = root / "AGENTS.md"
    data = guide.read_bytes() if guide.exists() else None
    span = block_span(data) if data is not None else None
    current = span is not None and data[span[0]:span[1]] == block
    if check:
        return current
    if data is None:
        updated = b"# Agent guide\n\n" + block + b"\n\n## This repository\n\nAdd repository-specific guidance here.\n"
    elif span:
        updated = data[:span[0]] + block + data[span[1]:]
    else:
        heading = re.search(rb"(?m)^#{1,6}[ \t]+[^\r\n]*(?:\r?\n|$)", data)
        if heading:
            before, after = data[:heading.end()], data[heading.end():]
            updated = before.rstrip(b"\r\n") + b"\n\n" + block + b"\n\n" + after.lstrip(b"\r\n")
        else:
            updated = block + b"\n\n" + data
    if data != updated:
        guide.write_bytes(updated)
    claude = root / "CLAUDE.md"
    if not claude.exists():
        claude.write_bytes(b"@AGENTS.md\n")
    return current


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="path to the repository checkout")
    parser.add_argument("--check", action="store_true", help="exit 10 if the shared block differs")
    args = parser.parse_args()
    if not args.checkout.is_dir():
        parser.error("checkout must be an existing directory")
    try:
        current = synchronize(args.checkout, args.check)
    except ValueError as error:
        parser.error(str(error))
    return 10 if args.check and not current else 0


if __name__ == "__main__":
    raise SystemExit(main())
