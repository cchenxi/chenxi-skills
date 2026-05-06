# time-convert Mixed Format — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add "Mixed" format (HBase shell native: printable ASCII as chars, non-printable as `\xHH`) as both input detection type and output format.

**Architecture:** Add `format_mixed()` function, split `detect_input_type` "escaped" into "mixed" (has non-\xHH chars too) and "escaped" (pure `\xHH`), add "mixed" to FORMAT_LABELS and --format choices.

**Tech Stack:** Python 3.9+ stdlib

---

### Task 1: Add format_mixed + Mixed output

**Files:**
- Modify: `scripts/time-convert:206-207` (add after format_escaped)
- Modify: `scripts/time-convert:291-298` (FORMAT_LABELS)
- Modify: `scripts/time-convert:370` (--format choices)
- Modify: `scripts/time-convert:230` (_format_single)
- Modify: `scripts/time-convert:228` (add _format_single mixed case)

- [ ] **Step 1: Add `format_mixed` function after `format_escaped` (after line 194)**

```python
def format_mixed(byte_list: list[int]) -> str:
    """Format as mixed string: printable ASCII as chars, rest as \\xHH."""
    result = []
    for b in byte_list:
        if 0x20 <= b <= 0x7E:
            result.append(chr(b))
        else:
            result.append(f'\\x{b:02X}')
    return ''.join(result)
```

- [ ] **Step 2: Add "mixed" to FORMAT_LABELS**

Change line ~291:
```python
FORMAT_LABELS = {
    'timestamp': 'Timestamp',
    'hex':       'Hex',
    'escaped':   'Escaped',
    'mixed':     'Mixed',       # new
    'bytes':     'Bytes',
    'java':      'Java bytes',
    'time':      'Time',
}
```

- [ ] **Step 3: Add "mixed" to argparse --format choices**

Change line ~370:
```python
        choices=['timestamp', 'hex', 'escaped', 'mixed', 'bytes', 'java', 'time', 'all'],
```

- [ ] **Step 4: Add mixed case to `_format_single`**

Add after the `escaped` case (line ~234):
```python
    if fmt == 'mixed':
        return format_mixed(byte_list)
```

- [ ] **Step 5: Run existing tests — must still pass**

```bash
python3 tests/test_time_convert.py
```

- [ ] **Step 6: Commit**

```bash
git add scripts/time-convert
git commit -m "feat: add Mixed output format (HBase shell native)"
```

---

### Task 2: Add "mixed" input detection type

**Files:**
- Modify: `scripts/time-convert:112-116` (detect_input_type)

- [ ] **Step 1: Update `detect_input_type` to split "mixed" from "escaped"**

Replace lines ~121-122:
```python
    if re.search(r'\\x[0-9a-fA-F]{2}', s):
        return "escaped"
```

With:
```python
    if re.search(r'\\x[0-9a-fA-F]{2}', s):
        # Distinguish pure escaped vs mixed (has printable chars outside \xHH)
        if re.fullmatch(r'(\\x[0-9a-fA-F]{2})+', s):
            return "escaped"
        return "mixed"
```

"escaped" = pure `(\xHH)+` sequence. "mixed" = `\xHH` plus other characters.

- [ ] **Step 2: Run tests — existing must still pass**

```bash
python3 tests/test_time_convert.py
```
Note: tests that check for "(escaped)" in headers may need updating to "(mixed)".

- [ ] **Step 3: Fix any test assertions if needed**

- [ ] **Step 4: Commit**

```bash
git add scripts/time-convert tests/test_time_convert.py
git commit -m "feat: add Mixed input detection (printable chars + \\xHH)"
```

---

### Task 3: Add mixed format test cases

**Files:**
- Modify: `tests/test_time_convert.py`

- [ ] **Step 1: Add tests**

```python
class TestMixedFormat(unittest.TestCase):
    """Mixed output format (HBase shell native)"""

    def test_mixed_output(self):
        r = run("2026-04-26 21:00:00", "-f", "mixed")
        self.assertEqual(r.returncode, 0)
        # 0x69='i', 0xEE=\xEE, 0x0C=\x0C, 0x50='P'
        self.assertIn(r"i\xEE\x0CP", r.stdout)

    def test_mixed_input_detected(self):
        r = run(r"prefix_\x69\xEE\x0C\x50_data", "-f", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("(mixed)", r.stdout)

    def test_escaped_input_still_works(self):
        r = run(r"\x69\xEE\x0C\x50", "-f", "all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("(escaped)", r.stdout)
```

- [ ] **Step 2: Run all tests**

```bash
python3 tests/test_time_convert.py
```
Expected: all pass.

- [ ] **Step 3: Commit**

```bash
git add tests/test_time_convert.py
git commit -m "test: add Mixed format test cases"
```

---

### Task 4: Update docs + sync

- [ ] **Step 1: Update SKILL.md, CLAUDE.md, README.md** to mention Mixed format

- [ ] **Step 2: Sync global install**

```bash
cp scripts/time-convert ~/.claude/skills/time-convert/scripts/time-convert
cp SKILL.md CLAUDE.md README.md ~/.claude/skills/time-convert/
```

- [ ] **Step 3: Run final test + commit**

```bash
python3 tests/test_time_convert.py
```
