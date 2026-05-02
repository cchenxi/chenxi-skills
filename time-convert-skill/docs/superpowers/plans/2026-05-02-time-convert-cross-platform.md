# time-convert Cross-Platform Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert all Chinese user-facing strings to English in scripts/time-convert, all three docs, and one test assertion. Add Windows tzdata note to docs.

**Architecture:** Find-and-replace 19 Chinese string literals in scripts/time-convert with English equivalents. Update 3 doc files to English. Update 1 test assertion. No logic changes.

**Tech Stack:** Python 3.9+ stdlib, no new dependencies.

---

### Task 1: English-ify scripts/time-convert — extract mode + error strings

**Files:**
- Modify: `scripts/time-convert` (lines 34, 89-93, 124, 133, 153, 161, 177, 181, 217, 262, 280, 286)

- [ ] **Step 1: Apply all string replacements**

Apply these exact replacements in order:

| Line | Old (Chinese) | New (English) |
|------|--------------|---------------|
| 34 | `f"无法识别的时区: '{tz_str}'。请使用如 Asia/Shanghai、UTC+8、+8、-5 等格式。"` | `f"Unrecognized timezone: '{tz_str}'. Use formats like Asia/Shanghai, UTC+8, +8, -5."` |
| 89-93 | `f"无法解析时间字符串: '{s}'。\n" f"支持的格式: 2026-04-26T21:00:00+08:00, 2026-04-26 21:00:00, " f"2026/04/26 21:00, 20260426210000 等。"` | `f"Cannot parse time string: '{s}'.\n" "Supported formats: 2026-04-26T21:00:00+08:00, 2026-04-26 21:00:00, " "2026/04/26 21:00, 20260426210000, etc."` |
| 124 | `"空数组"` | `"Empty array"` |
| 133 | `f"字节值超出范围: {val}"` | `f"Byte value out of range: {val}"` |
| 153 | `f"需要至少4字节，当前只有{len(byte_list)}字节"` | `f"Need at least 4 bytes, got {len(byte_list)}"` |
| 161 | `"空输入"` | `"Empty input"` |
| 177 | `f"Hex字符串长度必须为偶数，当前长度: {len(s_clean)}"` | `f"Hex string must have even length, got: {len(s_clean)}"` |
| 181 | `f"无法识别的输入格式: {s[:50]}"` | `f"Unrecognized input format: {s[:50]}"` |
| 217 | `"空输入"` | `"Empty input"` |
| 262 | `f'--- 偏移 {offset} ({format_escaped(ts_bytes)}) ---'` | `f'--- offset {offset} ({format_escaped(ts_bytes)}) ---'` |
| 280 | `f'--- 偏移 {offset//2} ({format_escaped(ts_bytes)}) ---'` | `f'--- offset {offset//2} ({format_escaped(ts_bytes)}) ---'` |
| 286 | `"未在输入中找到时间戳候选。"` | `"No timestamp candidates found in input."` |

Use the Edit tool with `replace_all: false` for each replacement (each is unique in the file).

- [ ] **Step 2: Run tests to confirm nothing broken so far**

```bash
python3 tests/test_time_convert.py
```
Expected: 34 pass, 1 fail (test_extract_no_match still asserts Chinese string). The error messages that tests check via `r.stderr` (like `Error:`) are now English, but the tests check with `self.assertIn("Error:", r.stderr)` which still matches.

- [ ] **Step 3: Commit**

```bash
git add scripts/time-convert
git commit -m "i18n: translate error messages and extract output to English"
```

---

### Task 2: English-ify scripts/time-convert — argparse help text

**Files:**
- Modify: `scripts/time-convert` (lines 356-380, 411)

- [ ] **Step 1: Apply argparse/help replacements**

| Line | Old (Chinese) | New (English) |
|------|--------------|---------------|
| 357 | `'在时间字符串与 HBase rowkey 时间字节之间互相转换。'` | `'Convert between time strings and HBase rowkey time bytes (4-byte big-endian Unix timestamp).'` |
| 361-362 | `'输入: 时间字符串、Unix时间戳(10位)、Hex、\\xHH格式、或bytes数组。使用 "-" 从 stdin 读取。'` | `'Time string, Unix timestamp (10-digit), hex, \\xHH escaped, or bytes array. Use "-" to read from stdin.'` |
| 366 | `'时区，默认 Asia/Shanghai (UTC+8)。支持 IANA 时区名、UTC+8、+8、-5 等格式。'` | `'Timezone, default Asia/Shanghai (UTC+8). Supports IANA names, UTC+8, +8, -5, etc.'` |
| 372 | `'输出格式筛选 (默认: all)'` | `'Output format filter (default: all)'` |
| 376 | `'从混合文本中提取时间片段并逐段解析'` | `'Extract timestamp candidates from mixed text'` |
| 380 | `'批量模式: 每行作为独立输入解析'` | `'Batch mode: treat each line as independent input'` |
| 411 | `'Error: 空输入。请提供时间字符串、时间戳、Hex、\\xHH 格式或 bytes 数组。'` | `'Error: empty input. Provide a time string, timestamp, hex, \\xHH escaped, or bytes array.'` |

- [ ] **Step 2: Run tests**

```bash
python3 tests/test_time_convert.py
```
Expected: 34 pass, 1 fail (same extract_no_match test)

- [ ] **Step 3: Commit**

```bash
git add scripts/time-convert
git commit -m "i18n: translate argparse help text to English"
```

---

### Task 3: Update test assertion for English extract message

**Files:**
- Modify: `tests/test_time_convert.py:168`

- [ ] **Step 1: Replace the Chinese assertion**

```python
# Line 168: change
self.assertIn("未在输入中找到时间戳候选", r.stdout)
# to
self.assertIn("No timestamp candidates found in input.", r.stdout)
```

- [ ] **Step 2: Run tests — all 35 should pass**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 pass, 0 fail

- [ ] **Step 3: Commit**

```bash
git add tests/test_time_convert.py
git commit -m "test: update extract-no-match assertion to English"
```

---

### Task 4: English-ify all documentation + add Windows tzdata note

**Files:**
- Modify: `SKILL.md` (full rewrite)
- Modify: `CLAUDE.md` (full rewrite)
- Modify: `README.md` (full rewrite)

- [ ] **Step 1: Write English SKILL.md**

```markdown
---
name: time-convert
description: Convert between time strings and HBase rowkey time bytes (4-byte big-endian Unix timestamp). Forward: time string → timestamp/hex/escaped/bytes/java. Reverse: timestamp/hex/bytes → time string. Supports global timezones, batch mode, stdin.
allowed-tools: Bash
dependencies: python>=3.9
user-invocable: true
---

# Time Convert

Convert between time strings and HBase rowkey time bytes (4-byte big-endian Unix timestamp).

> **Windows users:** Install IANA timezone data before use: `pip install tzdata`

## Usage

```bash
python3 ./scripts/time-convert '<input>' [-z TIMEZONE] [-f FORMAT] [-e] [-b]
```

If `python3` is not available, try `python` or `python3.9`.

Additional modes:
- **stdin**: use `-` as input, e.g. `printf '%s\n' '\x69\xEE\x0C\x50' | python3 ./scripts/time-convert -`
- **batch**: `-b`/`--batch` treats each line as an independent input
- **extract**: `-e` scans mixed text for timestamp candidates

## Examples

### Forward: time string → all formats

```bash
python3 ./scripts/time-convert '2026-04-26 21:00:00'
```

```
[Timestamp]     1777208400
[Hex]           69EE0C50
[Escaped]       \x69\xEE\x0C\x50
[Bytes]         [105, 238, 12, 80]
[Java bytes]    [105, -18, 12, 80]
[Time]          2026-04-26 21:00:00 +0800
```

### Reverse: bytes → time

```bash
python3 ./scripts/time-convert '\x69\xEE\x0C\x50'
python3 ./scripts/time-convert '69EE0C50'
python3 ./scripts/time-convert '[105, 238, 12, 80]'
python3 ./scripts/time-convert '1777208400'
```

### Single format output

```bash
python3 ./scripts/time-convert '2026-04-26 21:00:00' -f escaped
```
```
\x69\xEE\x0C\x50
```

### Timezone

```bash
python3 ./scripts/time-convert '2026-04-26 21:00:00' --tz UTC+0
python3 ./scripts/time-convert '2026-04-26 09:00:00' --tz America/New_York
```

### Extract timestamps from mixed text

```bash
python3 ./scripts/time-convert 'prefix_\x69\xEE\x0C\x50_data' -e
```

### Batch mode

```bash
printf '2026-04-26 21:00:00\n69EE0C50' | python3 ./scripts/time-convert - --batch
```

### Batch + pipe-friendly output

```bash
printf '2026-04-26 21:00:00\n69EE0C50' | python3 ./scripts/time-convert - --batch --format hex
```
```
69EE0C50
69EE0C50
```

## Displaying results

Show the full output to the user in a code block. If they only need a specific format, pass `--format`. For batch mode, pipe / multi-line input through stdin with `-`.

## Error handling

- If the script fails with `Error:`, relay the error message to the user and suggest checking the input format.
- In batch mode, parse errors on a single line produce a `Warning:` to stderr but do not stop processing of remaining lines.
- If `python3` is not found, try `python` or `python3.9`. If none are available, tell the user that Python 3.9+ is required.

## Related skills

- **rowkey-convert**: Use when the user needs to convert HBase rowkey format between mixed, hex, escaped, bytes, and annotated.
```

- [ ] **Step 2: Write English CLAUDE.md**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Claude Code skill — `time-convert`, for converting between time strings and 4-byte big-endian Unix timestamps in HBase rowkeys. Complementary to `rowkey-convert` skill: rowkey-convert handles rowkey format conversion (mixed/hex/bytes), time-convert focuses on time encoding/decoding.

## Commands

```bash
# Forward: time string → all formats
python3 ./scripts/time-convert '2026-04-26 21:00:00'

# Reverse: hex/escaped/bytes/timestamp → time
python3 ./scripts/time-convert '69EE0C50'
python3 ./scripts/time-convert '\x69\xEE\x0C\x50'
python3 ./scripts/time-convert '[105, 238, 12, 80]'
python3 ./scripts/time-convert '1777208400'

# Specify timezone
python3 ./scripts/time-convert '2026-04-26 21:00:00' --tz UTC+0

# Filter output format (timestamp/hex/escaped/bytes/java/time/all)
python3 ./scripts/time-convert '2026-04-26 21:00:00' -f escaped

# Extract mode: scan mixed text for timestamp candidates
python3 ./scripts/time-convert 'prefix_\x69\xEE\x0C\x50_data' -e

# Batch mode: each line as independent input
printf '2026-04-26 21:00:00\n69EE0C50' | python3 ./scripts/time-convert - --batch

# Read from stdin
printf '%s\n' '\x69\xEE\x0C\x50' | python3 ./scripts/time-convert -

# Run tests
python3 tests/test_time_convert.py
```

## Architecture

Single-file Python script (`scripts/time-convert`), using only stdlib (`argparse`, `re`, `struct`, `sys`, `datetime`, `zoneinfo`), no external dependencies. Requires Python 3.9+.

**Conversion paths:**
- **Forward** (time string → bytes): `parse_time_string()` → `datetime.timestamp()` → `struct.pack('>I', ts)` → 6 output formats
- **Reverse** (bytes → time string): `detect_input_type()` → `parse_to_timestamp()` → `datetime.fromtimestamp(ts, tz=tz)` → time string

**Input detection** (`detect_input_type`): `[bytes array]` > `\xHH` escaped > 10-digit timestamp > 8-char hex (with at least one A-F letter) > time string.

**Output formats:** `timestamp` (Unix timestamp), `hex` (uppercase hex), `escaped` (`\xHH` format), `bytes` (`[0, 255, ...]`), `java` (`[0, -1, ...]` signed bytes), `time` (formatted time string).

**Extract mode** (`-e`): Scans mixed text for `\xHH` sequences and 8+ char hex sequences, parsing each 4-byte sliding window as a timestamp candidate.

**Batch mode** (`-b`/`--batch`): Each line processed independently with auto-detection. Parse failures emit `Warning:` to stderr and continue. Supports combination with `-e`.

## Timezone handling

`parse_timezone()` supports three input forms:
- IANA names → `ZoneInfo(name)`
- UTC offset format (`UTC+8`, `UTC-5:30`) → `timezone(offset)`
- Short offset (`+8`, `-5`) → same as above

**Windows users:** Install `tzdata` package for IANA timezone support: `pip install tzdata`

Reverse conversion uses `datetime.fromtimestamp(ts, tz=tz)` to restore to the specified timezone.
```

- [ ] **Step 3: Write English README.md**

```markdown
# time-convert

Convert between time strings and HBase rowkey time bytes (4-byte big-endian Unix timestamp).

## Background

In Java/big-data projects, HBase rowkeys often encode time as a 4-byte big-endian Unix timestamp (second precision). When debugging, you frequently need to convert between `hbase shell` `\xHH` output and human-readable time strings. This tool automates that process.

## Installation

### Option 1: As a Claude Code skill

```bash
cp -r . ~/.claude/skills/time-convert/
```

Then invoke via Claude Code skill.

### Option 2: Standalone CLI tool

```bash
cp scripts/time-convert /usr/local/bin/time-convert
chmod +x /usr/local/bin/time-convert
```

### Dependencies

- Python 3.9+ (no pip packages required)
- **Windows users:** `pip install tzdata` (provides IANA timezone data for `zoneinfo`)

## Usage

```
python3 ./scripts/time-convert <input> [-z TIMEZONE] [-f FORMAT] [-e] [-b]
```

### Basic examples

```bash
# Forward: time string → all formats
$ python3 ./scripts/time-convert '2026-04-26 21:00:00'
[Timestamp]     1777208400
[Hex]           69EE0C50
[Escaped]       \x69\xEE\x0C\x50
[Bytes]         [105, 238, 12, 80]
[Java bytes]    [105, -18, 12, 80]
[Time]          2026-04-26 21:00:00 +0800
```

### Reverse conversion

Supports multiple input formats with auto-detection:

```bash
# Hex (copy from HBase shell, remove \x prefix)
$ python3 ./scripts/time-convert '69EE0C50'

# Escaped (HBase shell native format)
$ python3 ./scripts/time-convert '\x69\xEE\x0C\x50'

# Bytes array
$ python3 ./scripts/time-convert '[105, 238, 12, 80]'

# Unix timestamp
$ python3 ./scripts/time-convert '1777208400'

# All four produce the same result → 2026-04-26 21:00:00 +0800
```

### Supported input formats

| Format | Example |
|--------|---------|
| ISO 8601 | `2026-04-26T21:00:00`, `2026-04-26T21:00:00+08:00` |
| Date time | `2026-04-26 21:00:00`, `2026-04-26 21:00` |
| Date only | `2026-04-26` |
| Slash separated | `2026/04/26 21:00:00` |
| Compact | `20260426210000`, `20260426` |

### Timezone

Default: `Asia/Shanghai` (UTC+8). Override with `-z`:

```bash
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' --tz UTC+0
$ python3 ./scripts/time-convert '2026-04-26 09:00:00' --tz America/New_York
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' --tz +9
```

Supports three timezone formats: IANA names (`Asia/Tokyo`), UTC offsets (`UTC+8`), short offsets (`+8`, `-5`).

### Filter output format

```bash
# Only need \xHH format for pasting into HBase shell
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' -f escaped
\x69\xEE\x0C\x50

# Only need the timestamp
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' -f timestamp
1777208400

# Java signed bytes
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' -f java
[105, -18, 12, 80]
```

Options: `timestamp`, `hex`, `escaped`, `bytes`, `java`, `time`, `all` (default).

### Extract timestamps from mixed rowkeys

When a rowkey contains prefix, timestamp, suffix, use `-e` to scan all possible time segments:

```bash
$ python3 ./scripts/time-convert 'prefix_\x69\xEE\x0C\x50_data_\x67\x89\xAB\xCD' -e
--- offset 0 (\x69\xEE\x0C\x50) ---
[Timestamp]     1777208400
[Time]          2026-04-26 21:00:00 +0800
--- offset 0 (\x67\x89\xAB\xCD) ---
[Timestamp]     1737075661
[Time]          2025-01-17 09:01:01 +0800
```

### Batch mode

Each line processed as independent input with format auto-detection:

```bash
$ printf '2026-04-26 21:00:00\n69EE0C50\n[105, 238, 12, 80]' | \
    python3 ./scripts/time-convert - --batch
--- [1] (time) ---
[Timestamp]     1777208400
...
--- [2] (hex) ---
[Timestamp]     1777208400
...
--- [3] (bytes) ---
[Timestamp]     1777208400
...
```

Pipe-friendly output (values only, no labels):

```bash
$ printf '2026-04-26 21:00:00\n69EE0C50' | \
    python3 ./scripts/time-convert - --batch --format hex
69EE0C50
69EE0C50
```

### stdin input

```bash
$ printf '%s\n' '\x69\xEE\x0C\x50' | python3 ./scripts/time-convert -
```

## Using with rowkey-convert

```bash
# Scenario: HBase shell outputs a rowkey, need to analyze the time portion
$ python3 ~/.claude/skills/rowkey-convert/scripts/rowkey-convert \
    'prefix_\x69\xEE\x0C\x50' -f escaped
\x70\x72\x65\x66\x69\x78\x5F\x69\xEE\x0C\x50

# Extract the time portion and parse with time-convert
$ python3 ./scripts/time-convert '\x69\xEE\x0C\x50'
```

## Testing

```bash
python3 tests/test_time_convert.py
```

35 test cases covering forward conversion, reverse conversion (4 input types), timezones (3 formats), format filtering (including java), extract mode, batch mode (including pipe-friendly, error continuation, batch+extract).
```

- [ ] **Step 4: Commit**

```bash
git add SKILL.md CLAUDE.md README.md
git commit -m "docs: translate all documentation to English, add Windows tzdata note"
```

---

### Task 5: Final verification

- [ ] **Step 1: Run full test suite**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 pass, 0 fail

- [ ] **Step 2: Manual smoke tests**

```bash
python3 scripts/time-convert '2026-04-26 21:00:00'
python3 scripts/time-convert '69EE0C50' -f time
python3 scripts/time-convert --help
```
Expected: all output in English

- [ ] **Step 3: Commit any final fixes if needed**
