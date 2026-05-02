# time-convert Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor time-convert-skill to align with rowkey-convert-skill engineering patterns: scripts/tests/ directory structure, unittest framework, --batch/stdin support, java output format, and SKILL.md metadata.

**Architecture:** Single Python 3 stdlib script at `scripts/time-convert` with detection→parsing→formatting→output pipeline. Tests at `tests/test_time_convert.py` using `unittest.TestCase` with `subprocess.run`. The script supports five input types (time string, timestamp, hex, escaped, bytes array) and six output formats (timestamp, hex, escaped, bytes, java, time).

**Tech Stack:** Python 3.9+ stdlib only (argparse, re, struct, subprocess, unittest, datetime, zoneinfo)

---

### Task 1: Create directory structure and move files

**Files:**
- Create: `scripts/` (directory)
- Create: `tests/` (directory)

- [ ] **Step 1: Create directories and move script**

```bash
mkdir -p scripts tests
git mv time-convert scripts/time-convert
git mv test_cases.py tests/test_time_convert.py
```

- [ ] **Step 2: Commit**

```bash
git add scripts/ tests/ time-convert test_cases.py
git commit -m "refactor: move to scripts/ and tests/ directories"
```

---

### Task 2: Rewrite tests as unittest

**Files:**
- Write: `tests/test_time_convert.py` (overwrite)

- [ ] **Step 1: Write the full test suite**

```python
"""Test cases for time-convert CLI tool."""

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "time-convert"


def run(input_str: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), input_str, *args],
        capture_output=True, text=True
    )


class TestForwardConversion(unittest.TestCase):
    """Time string → all formats"""

    def test_datetime_to_all(self):
        r = run("2026-04-26 21:00:00")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("69EE0C50", r.stdout)
        self.assertIn(r"\x69\xEE\x0C\x50", r.stdout)
        self.assertIn("[105, 238, 12, 80]", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_iso_with_offset(self):
        r = run("2026-04-26T21:00:00+08:00")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("69EE0C50", r.stdout)

    def test_date_only(self):
        r = run("2026-04-26")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777132800", r.stdout)
        self.assertIn("2026-04-26 00:00:00 +0800", r.stdout)

    def test_slash_format(self):
        r = run("2026/04/26 21:00:00")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)

    def test_compact_format(self):
        r = run("20260426210000")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)


class TestReverseConversion(unittest.TestCase):
    """Hex / escaped / bytes / timestamp → time"""

    def test_hex_to_all(self):
        r = run("69EE0C50")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_hex_lowercase(self):
        r = run("69ee0c50")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)

    def test_escaped_to_all(self):
        r = run(r"\x69\xEE\x0C\x50")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_bytes_array_to_all(self):
        r = run("[105, 238, 12, 80]")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_timestamp_to_all(self):
        r = run("1777208400")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)


class TestTimezone(unittest.TestCase):
    """Timezone handling"""

    def test_utc_plus_1(self):
        r = run("2026-04-26 14:00:00", "--tz", "UTC+1")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 14:00:00 +0100", r.stdout)

    def test_utc_plus_0(self):
        r = run("2026-04-26 13:00:00", "--tz", "UTC+0")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 13:00:00 +0000", r.stdout)

    def test_iana_timezone(self):
        r = run("2026-04-26 09:00:00", "--tz", "America/New_York")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 09:00:00 -0400", r.stdout)

    def test_short_offset(self):
        r = run("2026-04-26 21:00:00", "--tz", "+9")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 21:00:00 +0900", r.stdout)


class TestFormatFilter(unittest.TestCase):
    """--format flag"""

    def test_format_escaped_only(self):
        r = run("2026-04-26 21:00:00", "-f", "escaped")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\x69\xEE\x0C\x50", r.stdout)
        self.assertNotIn("[Timestamp]", r.stdout)

    def test_format_hex_only(self):
        r = run("2026-04-26 21:00:00", "-f", "hex")
        self.assertEqual(r.returncode, 0)
        self.assertIn("69EE0C50", r.stdout)
        self.assertNotIn("[Timestamp]", r.stdout)

    def test_format_time_only(self):
        r = run("69EE0C50", "-f", "time")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)
        self.assertNotIn("[Hex]", r.stdout)

    def test_format_timestamp_only(self):
        r = run("69EE0C50", "-f", "timestamp")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1777208400", r.stdout)
        self.assertNotIn("[Hex]", r.stdout)

    def test_format_bytes_only(self):
        r = run("69EE0C50", "-f", "bytes")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[105, 238, 12, 80]", r.stdout)

    def test_format_java_only(self):
        r = run("69EE0C50", "-f", "java")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[105, -18, 12, 80]", r.stdout)


class TestExtractMode(unittest.TestCase):
    """--extract flag"""

    def test_extract_escaped_sequences(self):
        r = run(r"prefix_\x69\xEE\x0C\x50_data_\x67\x89\xAB\xCD", "-e")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\x69\xEE\x0C\x50", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)
        self.assertIn(r"\x67\x89\xAB\xCD", r.stdout)
        self.assertIn("2025-01-17 09:01:01 +0800", r.stdout)

    def test_extract_plain_hex(self):
        r = run("prefix_69EE0C50_data", "-e")
        self.assertEqual(r.returncode, 0)
        self.assertIn(r"\x69\xEE\x0C\x50", r.stdout)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)

    def test_extract_no_match(self):
        r = run("no timestamp here", "-e")
        self.assertEqual(r.returncode, 0)
        self.assertIn("未在输入中找到时间戳候选", r.stdout)


class TestBatchMode(unittest.TestCase):
    """--batch flag"""

    def test_batch_mixed_formats(self):
        r = run(
            "2026-04-26 21:00:00\n69EE0C50",
            "--batch", "--format", "all"
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("--- [1] (time) ---", r.stdout)
        self.assertIn("--- [2] (hex) ---", r.stdout)
        self.assertIn("1777208400", r.stdout)

    def test_batch_pipe_friendly(self):
        r = run(
            "2026-04-26 21:00:00\n69EE0C50",
            "--batch", "--format", "hex"
        )
        self.assertEqual(r.returncode, 0)
        lines = r.stdout.strip().split("\n")
        self.assertEqual(len(lines), 2)
        self.assertIn("69EE0C50", lines)

    def test_batch_blank_lines_skipped(self):
        r = run(
            "2026-04-26 21:00:00\n\n\n69EE0C50",
            "--batch", "--format", "hex"
        )
        self.assertEqual(r.returncode, 0)
        lines = r.stdout.strip().split("\n")
        self.assertEqual(len(lines), 2)

    def test_batch_error_continues(self):
        r = run(
            "2026-04-26 21:00:00\nnot_a_time_string\n69EE0C50",
            "--batch", "--format", "hex"
        )
        self.assertIn("Warning: line 2:", r.stderr)
        lines = r.stdout.strip().split("\n")
        self.assertEqual(len(lines), 2)

    def test_batch_all_fail_exit_code_one(self):
        r = run("not_a_time_string", "--batch", "--format", "hex")
        self.assertNotEqual(r.returncode, 0)

    def test_batch_partial_success_exit_code_zero(self):
        r = run(
            "2026-04-26 21:00:00\nbad_input",
            "--batch", "--format", "hex"
        )
        self.assertEqual(r.returncode, 0)

    def test_batch_with_extract(self):
        r = run(
            r"prefix_\x69\xEE\x0C\x50\nother_\x67\x89\xAB\xCD",
            "--batch", "--extract"
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-04-26 21:00:00 +0800", r.stdout)
        self.assertIn("2025-01-17 09:01:01 +0800", r.stdout)

    def test_batch_stdin(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "-", "--batch", "--format", "hex"],
            input="2026-04-26 21:00:00\n69EE0C50",
            capture_output=True, text=True
        )
        self.assertEqual(r.returncode, 0)
        lines = r.stdout.strip().split("\n")
        self.assertEqual(len(lines), 2)


class TestEdgeCases(unittest.TestCase):
    """Edge cases"""

    def test_empty_input_error(self):
        r = run("")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Error:", r.stderr)

    def test_java_output_signed_bytes(self):
        r = run("69EE0C50", "-f", "java")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[105, -18, 12, 80]", r.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail** (script not yet in scripts/)

```bash
python3 tests/test_time_convert.py
```
Expected: failures because `scripts/time-convert` doesn't exist yet, or uses old import paths. But since we moved the file in Task 1, it should already exist at `scripts/time-convert`. If tests reference old behavior, some may fail.

- [ ] **Step 3: Commit**

```bash
git add tests/test_time_convert.py
git commit -m "test: rewrite tests as unittest with batch mode coverage"
```

---

### Task 3: Refactor scripts/time-convert — add java output, batch, stdin, align output pattern

**Files:**
- Modify: `scripts/time-convert` (full rewrite)

- [ ] **Step 1: Write the refactored script**

```python
#!/usr/bin/env python3
"""Convert between time strings and HBase rowkey time bytes (4-byte big-endian Unix timestamp)."""

import argparse
import re
import struct
import sys
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


# ---------- timezone ----------

def parse_timezone(tz_str: str):
    """Parse a timezone string into a ZoneInfo or timezone object.

    Supports: IANA names (Asia/Shanghai), UTC offsets (UTC+8, UTC-5, +08:00, +8, -5).
    """
    tz_str = tz_str.strip()

    try:
        return ZoneInfo(tz_str)
    except (ZoneInfoNotFoundError, KeyError):
        pass

    m = re.match(r'^(?:UTC|GMT)?\s*([+-])(\d{1,2})(?::(\d{2}))?$', tz_str, re.IGNORECASE)
    if m:
        sign = 1 if m.group(1) == '+' else -1
        hours = int(m.group(2))
        minutes = int(m.group(3)) if m.group(3) else 0
        offset = sign * timedelta(hours=hours, minutes=minutes)
        return timezone(offset)

    raise ValueError(f"无法识别的时区: '{tz_str}'。请使用如 Asia/Shanghai、UTC+8、+8、-5 等格式。")


# ---------- time string parsing ----------

TIME_FORMATS = [
    '%Y-%m-%dT%H:%M:%S%z',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M:%S%z',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d',
    '%Y/%m/%d %H:%M:%S%z',
    '%Y/%m/%d %H:%M:%S',
    '%Y/%m/%d %H:%M',
    '%Y/%m/%d',
    '%Y%m%d%H%M%S',
    '%Y%m%d%H%M',
    '%Y%m%d',
]


def _try_parse_iso(s: str):
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _try_parse_formats(s: str, tz):
    for fmt in TIME_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt
        except ValueError:
            continue
    return None


def parse_time_string(s: str, tz) -> datetime:
    """Parse a time string into a timezone-aware datetime."""
    s = s.strip()

    dt = _try_parse_iso(s)
    if dt is not None:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        return dt

    dt = _try_parse_formats(s, tz)
    if dt is not None:
        return dt

    raise ValueError(
        f"无法解析时间字符串: '{s}'。\n"
        f"支持的格式: 2026-04-26T21:00:00+08:00, 2026-04-26 21:00:00, "
        f"2026/04/26 21:00, 20260426210000 等。"
    )


# ---------- detection ----------

def detect_input_type(s: str) -> str:
    """Detect input format: 'bytes', 'escaped', 'timestamp', 'hex', or 'time'."""
    s = s.strip()
    if not s:
        return "empty"

    if re.match(r'^\[.*\]$', s):
        return "bytes"

    if re.search(r'\\x[0-9a-fA-F]{2}', s):
        return "escaped"

    if re.fullmatch(r'\d{10}', s):
        return "timestamp"

    if re.fullmatch(r'[0-9a-fA-F]{8}', s):
        return "hex"

    return "time"


# ---------- parsing ----------

def parse_bytes_array(s: str) -> list[int]:
    inner = s.strip().strip('[]')
    if not inner:
        raise ValueError("空数组")
    result = []
    for token in inner.split(','):
        token = token.strip()
        if token.startswith('0x') or token.startswith('0X'):
            val = int(token, 16)
        else:
            val = int(token)
        if not (0 <= val <= 255):
            raise ValueError(f"字节值超出范围: {val}")
        result.append(val)
    return result


def parse_escaped(s: str) -> list[int]:
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 3 < len(s) and s[i+1] == 'x':
            result.append(int(s[i+2:i+4], 16))
            i += 4
        else:
            result.append(ord(s[i]))
            i += 1
    return result


def extract_timestamp_from_bytes(byte_list: list[int]) -> int:
    if len(byte_list) < 4:
        raise ValueError(f"需要至少4字节，当前只有{len(byte_list)}字节")
    return struct.unpack('>I', bytes(byte_list[:4]))[0]


def parse_to_timestamp(s: str) -> int:
    input_type = detect_input_type(s)

    if input_type == "empty":
        raise ValueError("空输入")

    if input_type == "timestamp":
        return int(s.strip())

    if input_type == "bytes":
        byte_list = parse_bytes_array(s)
        return extract_timestamp_from_bytes(byte_list)

    if input_type == "escaped":
        byte_list = parse_escaped(s)
        return extract_timestamp_from_bytes(byte_list)

    if input_type == "hex":
        s_clean = s.strip()
        if len(s_clean) % 2 != 0:
            raise ValueError(f"Hex字符串长度必须为偶数，当前长度: {len(s_clean)}")
        byte_list = [int(s_clean[i:i+2], 16) for i in range(0, len(s_clean), 2)]
        return extract_timestamp_from_bytes(byte_list)

    raise ValueError(f"无法识别的输入格式: {s[:50]}")


# ---------- formatting ----------

def format_timestamp(ts: int) -> str:
    return str(ts)


def format_hex(byte_list: list[int]) -> str:
    return ''.join(f'{b:02X}' for b in byte_list)


def format_escaped(byte_list: list[int]) -> str:
    return ''.join(f'\\x{b:02X}' for b in byte_list)


def format_bytes(byte_list: list[int]) -> str:
    return '[' + ', '.join(str(b) for b in byte_list) + ']'


def format_java_bytes(byte_list: list[int]) -> str:
    def to_signed(b: int) -> int:
        return b if b < 128 else b - 256
    return '[' + ', '.join(str(to_signed(b)) for b in byte_list) + ']'


def format_time(ts: int, tz) -> str:
    dt = datetime.fromtimestamp(ts, tz=tz)
    return dt.strftime('%Y-%m-%d %H:%M:%S %z')


# ---------- extract ----------

def extract_and_print(s: str, tz, fmt_filter: str):
    """Extract 4-byte timestamp candidates from mixed text and print each."""
    found_any = False

    # Find \xHH sequences
    pattern = re.compile(r'(\\x[0-9a-fA-F]{2})+')
    for m in pattern.finditer(s):
        seq = m.group()
        byte_list = parse_escaped(seq)
        if len(byte_list) < 4:
            continue
        for offset in range(len(byte_list) - 3):
            ts = extract_timestamp_from_bytes(byte_list[offset:offset+4])
            ts_bytes = byte_list[offset:offset+4]
            found_any = True
            print(f'--- 偏移 {offset} ({format_escaped(ts_bytes)}) ---')
            print_formats(ts, ts_bytes, tz, fmt_filter)

    # Also find pure hex sequences (8+ chars, not part of escaped)
    hex_pattern = re.compile(r'[0-9a-fA-F]{8,}')
    for m in hex_pattern.finditer(s):
        seq = m.group()
        start = m.start()
        if start >= 2 and s[start-2:start] == '\\x':
            continue
        for offset in range(0, len(seq) - 7, 2):
            chunk = seq[offset:offset+8]
            ts_bytes = [int(chunk[i:i+2], 16) for i in range(0, 8, 2)]
            ts = extract_timestamp_from_bytes(ts_bytes)
            found_any = True
            print(f'--- 偏移 {offset//2} ({format_escaped(ts_bytes)}) ---')
            print_formats(ts, ts_bytes, tz, fmt_filter)

    if not found_any:
        print("未在输入中找到时间戳候选。")


# ---------- output ----------

def print_formats(ts: int, ts_bytes: list[int], tz, fmt: str, input_str: str = '', detected_fmt: str = ''):
    """Print timestamp and byte list in the requested format(s)."""
    formats = [
        ('timestamp', 'Timestamp', format_timestamp(ts)),
        ('hex',       'Hex',       format_hex(ts_bytes)),
        ('escaped',   'Escaped',   format_escaped(ts_bytes)),
        ('bytes',     'Bytes',     format_bytes(ts_bytes)),
        ('java',      'Java bytes', format_java_bytes(ts_bytes)),
        ('time',      'Time',      format_time(ts, tz)),
    ]

    if fmt == 'all':
        if input_str:
            print(f'[Input] ({detected_fmt})\n{input_str}\n')
        for _, label, value in formats:
            print(f'[{label}]     {value}')
    else:
        for key, label, value in formats:
            if key == fmt:
                print(f'[{label}]     {value}')
                break


# ---------- batch ----------

def batch_process(input_text: str, fmt: str, tz, extract: bool) -> int:
    """Process input line-by-line as independent time inputs. Returns exit code."""
    lines = input_text.split('\n')
    success_count = 0
    fail_count = 0

    for i, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue

        if extract:
            print(f'--- [{i}] ---')
            extract_and_print(line, tz, fmt)
            success_count += 1
            continue

        input_type = detect_input_type(line)

        if input_type == "empty":
            print(f'Warning: line {i}: 空输入', file=sys.stderr)
            fail_count += 1
            continue

        # Forward: time string → bytes
        if input_type == "time":
            try:
                dt = parse_time_string(line, tz)
            except ValueError as e:
                print(f'Warning: line {i}: {e}', file=sys.stderr)
                fail_count += 1
                continue
            ts = int(dt.timestamp())
            ts_bytes = struct.pack('>I', ts)
            byte_list = list(ts_bytes)
        else:
            # Reverse: bytes → time
            try:
                ts = parse_to_timestamp(line)
            except ValueError as e:
                print(f'Warning: line {i}: {e}', file=sys.stderr)
                fail_count += 1
                continue
            ts_bytes = struct.pack('>I', ts)
            byte_list = list(ts_bytes)

        if fmt == 'all':
            print(f'--- [{i}] ({input_type}) ---')
            print_formats(ts, byte_list, tz, fmt, line, input_type)
        else:
            # Pipe-friendly: value only, no label
            fmts = [
                ('timestamp', format_timestamp(ts)),
                ('hex',       format_hex(byte_list)),
                ('escaped',   format_escaped(byte_list)),
                ('bytes',     format_bytes(byte_list)),
                ('java',      format_java_bytes(byte_list)),
                ('time',      format_time(ts, tz)),
            ]
            for key, value in fmts:
                if key == fmt:
                    print(value)
                    break
        success_count += 1

    if fail_count > 0 and success_count == 0:
        return 1
    return 0


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(
        description='在时间字符串与 HBase rowkey 时间字节之间互相转换。'
    )
    parser.add_argument(
        'input', type=str, nargs='?',
        help='输入: 时间字符串、Unix时间戳(10位)、Hex、\\xHH格式、或bytes数组。'
             ' 使用 "-" 从 stdin 读取。'
    )
    parser.add_argument(
        '-z', '--tz', type=str, default='Asia/Shanghai',
        help='时区，默认 Asia/Shanghai (UTC+8)。支持 IANA 时区名、UTC+8、+8、-5 等格式。'
    )
    parser.add_argument(
        '-f', '--format', type=str,
        choices=['timestamp', 'hex', 'escaped', 'bytes', 'java', 'time', 'all'],
        default='all',
        help='输出格式筛选 (默认: all)'
    )
    parser.add_argument(
        '-e', '--extract', action='store_true',
        help='从混合文本中提取时间片段并逐段解析'
    )
    parser.add_argument(
        '-b', '--batch', action='store_true',
        help='批量模式: 每行作为独立输入解析'
    )
    args = parser.parse_args()

    try:
        tz = parse_timezone(args.tz)
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    # Read from stdin if needed
    if args.input is None or args.input == '-':
        raw = sys.stdin.buffer.read()
        args.input = raw.decode('latin-1').strip()
        if not args.input:
            print('Error: no input provided (stdin was empty).', file=sys.stderr)
            sys.exit(1)

    if args.batch:
        sys.exit(batch_process(args.input, args.format, tz, args.extract))

    if args.extract:
        extract_and_print(args.input, tz, args.format)
        return

    input_type = detect_input_type(args.input)

    if input_type == "empty":
        print('Error: 空输入。请提供时间字符串、时间戳、Hex、\\xHH 格式或 bytes 数组。',
              file=sys.stderr)
        sys.exit(1)

    # Forward: time string → timestamp/bytes
    if input_type == "time":
        try:
            dt = parse_time_string(args.input, tz)
        except ValueError as e:
            print(f'Error: {e}', file=sys.stderr)
            sys.exit(1)

        ts = int(dt.timestamp())
        ts_bytes = struct.pack('>I', ts)
        byte_list = list(ts_bytes)
        print_formats(ts, byte_list, tz, args.format)
        return

    # Reverse: timestamp/hex/escaped/bytes → time
    try:
        ts = parse_to_timestamp(args.input)
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    ts_bytes = struct.pack('>I', ts)
    byte_list = list(ts_bytes)
    print_formats(ts, byte_list, tz, args.format)


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run tests**

```bash
python3 tests/test_time_convert.py
```
Expected: all tests pass

- [ ] **Step 3: Commit**

```bash
git add scripts/time-convert
git commit -m "refactor: add java format, batch mode, stdin, align output pattern"
```

---

### Task 4: Update SKILL.md, CLAUDE.md, README.md

**Files:**
- Modify: `SKILL.md`
- Modify: `CLAUDE.md`
- Modify: `README.md`

- [ ] **Step 1: Update SKILL.md metadata**

Write `SKILL.md`:

```markdown
---
name: time-convert
description: 时间与HBase rowkey字节互转。正向：时间字符串→时间戳/Hex/Escaped/Bytes/Java。反向：时间戳/Hex/Bytes→时间字符串。支持全球时区、批量模式、stdin。
allowed-tools: Bash
dependencies: python>=3.9
user-invocable: true
---

# Time Convert

在时间字符串与 HBase rowkey 时间字节（4 字节 big-endian Unix 时间戳）之间互相转换。

## Usage

```bash
python3 ./scripts/time-convert '<input>' [-z TIMEZONE] [-f FORMAT] [-e] [-b]
```

If `python3` is not available, try `python` or `python3.9`.

Additional modes:
- **stdin**: use `-` as input, e.g. `echo '\x69\xEE\x0C\x50' | python3 ./scripts/time-convert -`
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

## Error handling

- If the script fails with `Error:`, relay the error message to the user and suggest checking the input format.
- In batch mode, parse errors on a single line produce a `Warning:` to stderr but do not stop processing of remaining lines.
- If `python3` is not found, try `python` or `python3.9`. If none are available, tell the user that Python 3.9+ is required.

## Related skills

- **rowkey-convert**: Use when the user needs to convert HBase rowkey format between mixed, hex, escaped, bytes, and annotated.
```

- [ ] **Step 2: Update CLAUDE.md**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Code skill —— `time-convert`，用于在时间字符串与 HBase rowkey 中的 4 字节 big-endian Unix 时间戳之间互相转换。与 `rowkey-convert` skill 互补：rowkey-convert 处理行键格式转换（mixed/hex/bytes），time-convert 专注时间语义的编解码。

## Commands

```bash
# 正向: 时间字符串 → 各格式
python3 ./scripts/time-convert '2026-04-26 21:00:00'

# 反向: hex/escaped/bytes/timestamp → 时间
python3 ./scripts/time-convert '69EE0C50'
python3 ./scripts/time-convert '\x69\xEE\x0C\x50'
python3 ./scripts/time-convert '[105, 238, 12, 80]'
python3 ./scripts/time-convert '1777208400'

# 指定时区
python3 ./scripts/time-convert '2026-04-26 21:00:00' --tz UTC+0

# 筛选输出格式 (timestamp/hex/escaped/bytes/java/time/all)
python3 ./scripts/time-convert '2026-04-26 21:00:00' -f escaped

# 提取模式: 扫描混合文本中的时间片段
python3 ./scripts/time-convert 'prefix_\x69\xEE\x0C\x50_data' -e

# 批量模式: 每行独立解析
printf '2026-04-26 21:00:00\n69EE0C50' | python3 ./scripts/time-convert - --batch

# 从 stdin 读取
echo '\x69\xEE\x0C\x50' | python3 ./scripts/time-convert -

# 运行测试
python3 tests/test_time_convert.py
```

## Architecture

单文件 Python 脚本 (`scripts/time-convert`)，仅使用标准库（`argparse`, `re`, `struct`, `sys`, `datetime`, `zoneinfo`），无外部依赖。

**转换路径:**
- **正向** (time string → bytes): `parse_time_string()` → `datetime.timestamp()` → `struct.pack('>I', ts)` → 6 种格式输出
- **反向** (bytes → time string): `detect_input_type()` 识别格式 → `parse_to_timestamp()` 提取时间戳 → `datetime.fromtimestamp(ts, tz=tz)` 还原为时间字符串

**输入检测** (`detect_input_type`): `[bytes数组]` > `\xHH` escaped > 10位纯数字时间戳 > 8字符纯hex > 时间字符串。hex 检测要求恰好 8 字符（对应 4 字节），否则回退到时间字符串解析。

**输出格式:** `timestamp` (Unix 时间戳), `hex` (大写 hex), `escaped` (`\xHH` 格式), `bytes` (`[0, 255, ...]`), `java` (`[0, -1, ...]` signed bytes), `time` (格式化时间字符串)。

**提取模式** (`-e`): 扫描混合文本中的 `\xHH` 序列和 8+ 位纯 hex 序列，以 4 字节滑动窗口逐一解析每个候选时间戳。

**批量模式** (`-b`/`--batch`): 每行独立解析，自动检测格式。解析失败输出 `Warning:` 到 stderr 继续处理。支持与 `-e` 组合使用。

## 时区处理

`parse_timezone()` 支持三种输入形式:
- IANA 时区名 → `ZoneInfo(name)`
- UTC 偏移格式 (`UTC+8`, `UTC-5:30`) → `timezone(offset)`
- 简写偏移 (`+8`, `-5`) → 同上

反向转换输出使用 `datetime.fromtimestamp(ts, tz=tz)` 还原到指定时区。
```

- [ ] **Step 3: Update README.md**

Update README.md to reference `./scripts/time-convert` paths and add java format, batch mode, stdin sections. The README content is similar to SKILL.md examples with more prose.

- [ ] **Step 4: Verify SKILL.md meta fields**

```bash
python3 -c "
import yaml
# Quick check: the frontmatter should parse
with open('SKILL.md') as f:
    content = f.read()
    # Extract frontmatter between --- markers
    parts = content.split('---')
    print('Frontmatter:', parts[1].strip()[:200])
"
```

- [ ] **Step 5: Commit**

```bash
git add SKILL.md CLAUDE.md README.md
git commit -m "docs: update paths, add batch/stdin/java docs to SKILL.md/CLAUDE.md/README.md"
```

---

### Task 5: Final verification

- [ ] **Step 1: Run full test suite**

```bash
python3 tests/test_time_convert.py
```
Expected: all tests pass, no failures

- [ ] **Step 2: Manual smoke tests**

```bash
# Forward: time string → all formats
python3 scripts/time-convert '2026-04-26 21:00:00'

# Reverse: hex → time
python3 scripts/time-convert '69EE0C50'

# Java format
python3 scripts/time-convert '2026-04-26 21:00:00' -f java

# stdin batch
echo -e '2026-04-26 21:00:00\n69EE0C50' | python3 scripts/time-convert - --batch --format hex
```

- [ ] **Step 3: Commit any final fixes**

```bash
git add -A && git diff --cached --stat
# Only if fixes needed:
git commit -m "fix: final adjustments from verification"
```
