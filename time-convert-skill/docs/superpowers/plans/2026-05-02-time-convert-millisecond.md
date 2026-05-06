# time-convert Millisecond Timestamp Support — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support millisecond-precision timestamps (8-byte big-endian) alongside existing second-precision (4-byte). Auto-detect by digit/byte count.

**Architecture:** Extend detection→parsing→formatting pipeline to handle both 4-byte and 8-byte timestamps. Byte count determines precision: 4 bytes = seconds (`>I`), 8 bytes = milliseconds (`>Q`). `format_time` checks `len(byte_list)` to decide whether to show `.123` suffix. `convert_to_bytes` uses `ts >= 10**12` heuristic for reverse inputs, and `dt.timestamp() * 1000` for forward ms inputs.

**Tech Stack:** Python 3.9+ stdlib (`struct`, `datetime`, `re`)

---

### Task 1: Extend detection — 13-digit ms timestamps, 16-char hex

**Files:**
- Modify: `scripts/time-convert:98-116`

- [ ] **Step 1: Update `detect_input_type`**

Replace lines 110-114:

```python
    if re.fullmatch(r'\d{13}', s):
        return "timestamp"

    if re.fullmatch(r'\d{10}', s):
        return "timestamp"

    if re.fullmatch(r'[0-9a-fA-F]{16}', s):
        return "hex"

    if re.fullmatch(r'[0-9a-fA-F]{8}', s) and re.search(r'[a-fA-F]', s):
        return "hex"
```

Order: 13-digit before 10-digit (longer match first). 16-char hex before 8-char hex.

- [ ] **Step 2: Run existing tests — all 35 must still pass**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 pass, 0 fail. Existing tests must not break.

- [ ] **Step 3: Commit**

```bash
git add scripts/time-convert
git commit -m "feat: detect 13-digit ms timestamps and 16-char hex"
```

---

### Task 2: Extend `extract_timestamp_from_bytes` — support 8-byte `>Q`

**Files:**
- Modify: `scripts/time-convert:151-154`

- [ ] **Step 1: Update `extract_timestamp_from_bytes`**

Replace lines 151-154:

```python
def extract_timestamp_from_bytes(byte_list: list[int]) -> int:
    if len(byte_list) >= 8:
        return struct.unpack('>Q', bytes(byte_list[:8]))[0]
    if len(byte_list) >= 4:
        return struct.unpack('>I', bytes(byte_list[:4]))[0]
    raise ValueError(f"Need at least 4 bytes, got {len(byte_list)}")
```

8-byte check first, then 4-byte fallback.

- [ ] **Step 2: Run tests**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 pass.

- [ ] **Step 3: Commit**

```bash
git add scripts/time-convert
git commit -m "feat: support 8-byte >Q unpacking for millisecond timestamps"
```

---

### Task 3: Extend `format_time` — show `.123` for ms

**Files:**
- Modify: `scripts/time-convert:208-210` (format_time signature + body)

- [ ] **Step 1: Update `format_time` to accept `byte_list` and show ms**

Replace lines 208-210:

```python
def format_time(ts: int, byte_list: list[int], tz) -> str:
    if len(byte_list) >= 8:
        dt = datetime.fromtimestamp(ts / 1000.0, tz=tz)
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' ' + dt.strftime('%z')
    else:
        dt = datetime.fromtimestamp(ts, tz=tz)
        return dt.strftime('%Y-%m-%d %H:%M:%S %z')
```

- [ ] **Step 2: Update all callers to pass `byte_list`**

In `_format_single` (line 240): change `format_time(ts, tz)` to `format_time(ts, byte_list, tz)`

- [ ] **Step 3: Run tests**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 pass (existing second-precision tests unchanged).

- [ ] **Step 4: Commit**

```bash
git add scripts/time-convert
git commit -m "feat: format_time shows milliseconds for 8-byte timestamps"
```

---

### Task 4: Extend `convert_to_bytes` — ms forward + reverse

**Files:**
- Modify: `scripts/time-convert:213-224`

- [ ] **Step 1: Update `convert_to_bytes` for ms support**

Replace lines 213-224:

```python
def convert_to_bytes(input_str: str, tz) -> tuple[int, list[int]]:
    """Parse input and return (timestamp, byte_list). Raises ValueError on failure."""
    input_type = detect_input_type(input_str)
    if input_type == "empty":
        raise ValueError("Empty input")
    if input_type == "time":
        dt = parse_time_string(input_str, tz)
        ts_float = dt.timestamp()
        if ts_float != int(ts_float):
            # Has sub-second part → millisecond precision
            ts = int(ts_float * 1000)
            ts_bytes = struct.pack('>Q', ts)
        else:
            ts = int(ts_float)
            ts_bytes = struct.pack('>I', ts)
    else:
        ts = parse_to_timestamp(input_str)
        if ts >= 10**12:
            ts_bytes = struct.pack('>Q', ts)
        else:
            ts_bytes = struct.pack('>I', ts)
    return ts, list(ts_bytes)
```

- [ ] **Step 2: Run tests**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 pass.

- [ ] **Step 3: Commit**

```bash
git add scripts/time-convert
git commit -m "feat: ms precision in convert_to_bytes (forward + reverse)"
```

---

### Task 5: Support `.123` format in time strings

**Files:**
- Modify: `scripts/time-convert:39-53` (TIME_FORMATS)

- [ ] **Step 1: Add microsecond format variants**

Add these 4 formats to TIME_FORMATS list after existing formats:

```python
    '%Y-%m-%dT%H:%M:%S.%f%z',
    '%Y-%m-%dT%H:%M:%S.%f',
    '%Y-%m-%d %H:%M:%S.%f%z',
    '%Y-%m-%d %H:%M:%S.%f',
```

Also update the error message on line 92 to mention the `.123` format:
```python
        f"Cannot parse time string: '{s}'.\n"
        "Supported formats: 2026-04-26T21:00:00+08:00, 2026-04-26 21:00:00.123, "
        "2026/04/26 21:00, 20260426210000, etc."
```

- [ ] **Step 2: Run tests**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 pass.

- [ ] **Step 3: Commit**

```bash
git add scripts/time-convert
git commit -m "feat: support .123 millisecond format in time strings"
```

---

### Task 6: Extend extract mode — 8-byte windows

**Files:**
- Modify: `scripts/time-convert:246-286`

- [ ] **Step 1: Add 8-byte sliding window to \xHH extract**

Replace lines 257-265 (the escaped extraction inner loop):

The code currently scans 4-byte windows. Add 8-byte scanning alongside:

```python
        for offset in range(len(byte_list) - 3):
            ts = extract_timestamp_from_bytes(byte_list[offset:offset+4])
            ts_bytes = byte_list[offset:offset+4]
            found_any = True
            if show_headers:
                print(f'--- offset {offset} ({format_escaped(ts_bytes)}) [4-byte] ---')
                print_formats(ts, ts_bytes, tz, fmt_filter)
            else:
                print(_format_single(ts, ts_bytes, tz, fmt_filter))
        for offset in range(len(byte_list) - 7):
            ts = extract_timestamp_from_bytes(byte_list[offset:offset+8])
            ts_bytes = byte_list[offset:offset+8]
            found_any = True
            if show_headers:
                print(f'--- offset {offset} ({format_escaped(ts_bytes)}) [8-byte] ---')
                print_formats(ts, ts_bytes, tz, fmt_filter)
            else:
                print(_format_single(ts, ts_bytes, tz, fmt_filter))
```

Note the `[4-byte]` / `[8-byte]` label to distinguish window sizes.

- [ ] **Step 2: Add 16-char hex windows**

Replace lines 274-283 (the hex extraction inner loop). Add 16-char scanning before the existing 8-char loop:

```python
        for offset in range(0, len(seq) - 15, 2):
            chunk = seq[offset:offset+16]
            ts_bytes = [int(chunk[i:i+2], 16) for i in range(0, 16, 2)]
            ts = extract_timestamp_from_bytes(ts_bytes)
            found_any = True
            if show_headers:
                print(f'--- offset {offset//2} ({format_escaped(ts_bytes)}) [8-byte] ---')
                print_formats(ts, ts_bytes, tz, fmt_filter)
            else:
                print(_format_single(ts, ts_bytes, tz, fmt_filter))
        for offset in range(0, len(seq) - 7, 2):
            chunk = seq[offset:offset+8]
            ts_bytes = [int(chunk[i:i+2], 16) for i in range(0, 8, 2)]
            ts = extract_timestamp_from_bytes(ts_bytes)
            found_any = True
            if show_headers:
                print(f'--- offset {offset//2} ({format_escaped(ts_bytes)}) [4-byte] ---')
                print_formats(ts, ts_bytes, tz, fmt_filter)
            else:
                print(_format_single(ts, ts_bytes, tz, fmt_filter))
```

- [ ] **Step 3: Run tests**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 pass (existing extract tests).

- [ ] **Step 4: Commit**

```bash
git add scripts/time-convert
git commit -m "feat: extract mode scans both 4-byte and 8-byte windows"
```

---

### Task 7: Add millisecond test cases

**Files:**
- Modify: `tests/test_time_convert.py`

- [ ] **Step 1: Add ms test class**

Add after the `TestReverseConversion` class (after line 83):

```python
class TestMillisecondConversion(unittest.TestCase):
    """Millisecond timestamp support"""

    def test_ms_timestamp_to_all(self):
        r = run("1790784000123")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1790784000123", r.stdout)
        self.assertIn("2026-10-01 00:00:00.123", r.stdout)

    def test_ms_hex_to_all(self):
        r = run("0000019538D05B40")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1790784000123", r.stdout)
        self.assertIn("2026-10-01 00:00:00.123", r.stdout)

    def test_ms_escaped_to_all(self):
        r = run(r"\x00\x00\x01\x95\x38\xD0\x5B\x40")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1790784000123", r.stdout)

    def test_ms_bytes_to_all(self):
        r = run("[0, 0, 1, 149, 56, 208, 91, 64]")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1790784000123", r.stdout)

    def test_ms_time_string_forward(self):
        r = run("2026-10-01 00:00:00.123")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1790784000123", r.stdout)
        self.assertIn("2026-10-01 00:00:00.123", r.stdout)

    def test_seconds_still_work(self):
        """Second-precision must still work as before"""
        r = run("1790784000")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-10-01 00:00:00 +0800", r.stdout)
        self.assertNotIn(".000", r.stdout)
```

- [ ] **Step 2: Run tests — new tests should FAIL (not yet implemented)**

```bash
python3 tests/test_time_convert.py
```
Expected: 35 existing pass, 6 new fail (ms formats not yet fully wired through extract/full pipeline).

Wait, actually the script changes from Tasks 1-6 should make most of these pass. Let me refine: after Tasks 1-6, all 35 original + most new ms tests should pass.

- [ ] **Step 3: Run full suite**

```bash
python3 tests/test_time_convert.py
```
Expected: 41 pass, 0 fail

- [ ] **Step 4: Commit**

```bash
git add tests/test_time_convert.py
git commit -m "test: add millisecond timestamp test cases"
```

---

### Task 8: Update docs + version bump

**Files:**
- Modify: `scripts/time-convert:2,357,383`
- Modify: `SKILL.md`
- Modify: `CLAUDE.md`
- Modify: `README.md`

- [ ] **Step 1: Bump version and update docstrings**

Line 2: `"""Convert between time strings and HBase rowkey time bytes (4-byte or 8-byte big-endian Unix timestamp)."""`  
Line 357: `description='Convert between time strings and HBase rowkey time bytes (4-byte big-endian Unix timestamp).'` → add ms mention  
Line 361: `help='Time string, Unix timestamp (10 or 13-digit), hex, ...`  
Line 383: `version='time-convert 1.1.0'`

- [ ] **Step 2: Update SKILL.md with ms examples**

Add a "Millisecond timestamps" example section.

- [ ] **Step 3: Update CLAUDE.md**

Update "Conversion paths" and "Input detection" sections to mention ms.

- [ ] **Step 4: Update README.md**

Add ms examples. Update version reference.

- [ ] **Step 5: Run tests one final time**

```bash
python3 tests/test_time_convert.py
```
Expected: 41 pass, 0 fail.

- [ ] **Step 6: Commit**

```bash
git add scripts/time-convert SKILL.md CLAUDE.md README.md
git commit -m "docs: update for millisecond support, bump to 1.1.0"
```

---

### Task 9: Sync global install and final verification

- [ ] **Step 1: Sync to global skill**

```bash
cp -r "/Users/chenxi/workspaces/Claude Code/chenxi-skills/time-convert-skill"/* ~/.claude/skills/time-convert/
```

- [ ] **Step 2: Manual smoke tests**

```bash
python3 ~/.claude/skills/time-convert/scripts/time-convert '1790784000123'
python3 ~/.claude/skills/time-convert/scripts/time-convert '2026-10-01 00:00:00.123'
python3 ~/.claude/skills/time-convert/scripts/time-convert '2026-10-01 00:00:00'
python3 ~/.claude/skills/time-convert/scripts/time-convert --version
```
Expected: all correct, version 1.1.0
