# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single Python 3 CLI script that converts HBase rowkeys between formats commonly encountered when debugging with hbase shell.

## Commands

```bash
# Convert a rowkey (auto-detects input format, outputs all formats)
python3 ./scripts/rowkey-convert '<input>'

# Output a specific format only
python3 ./scripts/rowkey-convert '<input>' --format hex|escaped|bytes|java|annotated|mixed|all

# Read from stdin
echo '\x00\xFFhello' | python3 ./scripts/rowkey-convert -

# Batch mode: each line as an independent rowkey
printf '\x00\xFFhello\n00FF68' | python3 ./scripts/rowkey-convert - --batch

# Batch + specific format (pipe-friendly)
printf '\x00\xFFhello\n00FF68' | python3 ./scripts/rowkey-convert - --batch --format hex

# Extract rowkeys from mixed text (e.g. log lines)
python3 ./scripts/rowkey-convert 'prefix_\x00\xFF_data' -e

# Limit max byte length
python3 ./scripts/rowkey-convert '<input>' --max-length 100
```

## Architecture

Single-file Python script (`scripts/rowkey-convert`) using only stdlib (`argparse`, `re`, `sys`). No dependencies, no build step.

**Conversion flows:**
- **Forward** (mixed → other): parses `\xHH` escape sequences and literal characters into a byte list, then formats that byte list into any output format
- **Reverse** (hex/bytes/annotated → mixed): parses input into a byte list, then formats to any output format

**Input auto-detection** (`detect_format`): `[]` → empty, `[...]` → bytes, `\xHH` present → mixed, even-length hex chars → hex, newline-separated hex tokens → annotated, otherwise → mixed.

**Output formats:** `hex` (continuous uppercase hex), `escaped` (`\xHH` for hbase shell), `bytes` (`[0, 255, ...]` unsigned), `java` (`[0, -1, ...]` signed, for Java code pasting), `annotated` (hex dump with ASCII line), `mixed` (printable chars as-is, rest `\xHH`).

**Extract mode** (`-e`): Scans mixed text for `\xHH` sequences and extracts each as a rowkey candidate.

**Batch mode** (`-b`/`--batch`): Splits input by newline, treating each line as an independent rowkey with auto-detected format. Blank lines are skipped. Parse errors on a single line emit a `Warning:` to stderr and continue processing remaining lines. Mutually exclusive with `--extract`.

## Skill

The `SKILL.md` file registers this as a Claude Code skill. When the skill is loaded, Claude invokes the Python script to convert whatever rowkey the user provides.
