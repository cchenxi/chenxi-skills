# time-convert Cross-Platform Support

## Context

Make time-convert-skill work on macOS, Linux, and Windows. Convert all user-facing strings to English.

## Changes

### scripts/time-convert
- All 12 Chinese error/help strings → English
- Docstring → English
- argparse description/help → English

### Documentation
- SKILL.md: all Chinese → English; add Windows tzdata note
- CLAUDE.md: all Chinese → English
- README.md: all Chinese → English; add Windows tzdata note

### Tests (tests/test_time_convert.py)
- Update assertions matching Chinese text → English equivalents

### Windows tzdata
- No runtime check. Document only: "Windows users: pip install tzdata"

## Non-changes
- Script logic, timezone handling, format output
- Shebang line
- Directory structure

## Verification
```bash
python3 tests/test_time_convert.py   # all 35 tests pass
```
