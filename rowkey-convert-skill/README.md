# Rowkey Convert

Quickly convert HBase rowkeys between multiple representations — essential for Java + big data operations and debugging.

## Problem Solved

In HBase, rowkeys are `byte[]`. When queried via hbase shell, rowkeys appear in a mixed format — non-printable characters are escaped as `\xHH` while printable characters remain as-is, e.g. `\x00\xFFhello`. Troubleshooting production issues often requires converting between these formats:

| Format | Example | Use Case |
|--------|---------|----------|
| mixed | `\x00\xFFhello` | hbase shell output |
| hex | `00FF68656C6C6F` | searching / comparing in logs and code |
| escaped | `\x00\xFF\x68\x65\x6C\x6C\x6F` | hbase shell query conditions |
| bytes | `[0, 255, 104, 101, 108, 108, 111]` | Python/general (unsigned) |
| java | `[-1, -2, -3]` / `[0, -1, 104]` | Java code pasting (signed, two's complement), input + output |
| annotated | hex dump + ASCII annotation | understanding rowkey field structure |
| (batch) | multi-line input, one rowkey per line | bulk converting multiple rowkeys |

## Requirements

- Python ≥ 3.9 (uses `list[int]` type annotations)
- No third-party dependencies — stdlib only

## Installation

### Linux / macOS

```bash
# bash
echo 'export PATH="$PATH:'"$(pwd)"'"' >> ~/.bashrc && source ~/.bashrc

# zsh
echo 'export PATH="$PATH:'"$(pwd)"'"' >> ~/.zshrc && source ~/.zshrc

# fish
echo 'set -gx PATH $PATH '"$(pwd)" >> ~/.config/fish/config.fish
```

### Windows (PowerShell)

```powershell
# Add to current user PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$pwd", "User")

# Or run directly via python (no PATH install needed)
python scripts\rowkey-convert '<input>'
```

> **Note:** The script shebang (`#!/usr/bin/env python3`) does not work in Windows CMD. Windows users should invoke via `python` or `py` explicitly, e.g. `python scripts/rowkey-convert '\x00\xFFhello'`.

## CLI Usage

```bash
# Forward: mixed → all formats
python3 scripts/rowkey-convert '\x00\xFFhello'

# Reverse: hex → all formats
python3 scripts/rowkey-convert 00FF6865

# Reverse: bytes → all formats
python3 scripts/rowkey-convert '[0, 255, 104]'

# Reverse: Java bytes → all formats
python3 scripts/rowkey-convert '[-1, -2, -3]'

# Output a specific format
python3 scripts/rowkey-convert '\x00\xFFhello' --format escaped
python3 scripts/rowkey-convert '\x00\xFFhello' --format bytes
python3 scripts/rowkey-convert 00FF6865 --format mixed

# Batch mode: one rowkey per line, auto-detected independently
printf '\x00\xFFhello\n00FF68656C6C6F\n[0, 255, 104]' | python3 scripts/rowkey-convert - --batch

# Batch + specific format (pipe-friendly)
printf '\x00\xFFhello\n00FF68' | python3 scripts/rowkey-convert - --batch --format hex
```

Input format is auto-detected — no need to specify:
- Contains `\xHH` → mixed
- `[-1,...]` (has negatives) → java_bytes (signed)
- `[...]` (non-negative) → bytes (unsigned)
- Even-length hex characters → hex
- Everything else (e.g. printable string `hello`) → mixed

## Claude Code Skill

Paste a rowkey string directly in a Claude Code conversation to convert it automatically. The skill definition is in `SKILL.md`.

## Running Tests

```bash
python3 tests/test_rowkey_convert.py -v
```
