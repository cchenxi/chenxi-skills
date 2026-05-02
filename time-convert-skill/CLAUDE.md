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

**Input detection** (`detect_input_type`): `[byte array]` > `\xHH` escaped > 10-digit timestamp > 8-char hex (with at least one A-F letter) > time string.

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
