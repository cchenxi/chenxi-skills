# time-convert Millisecond Timestamp Support

## Context

Extend time-convert to support millisecond-precision timestamps alongside existing second-precision. HBase rowkeys may use 8-byte big-endian millisecond timestamps.

## Design

### Auto-detection by length

| Input | Seconds (4-byte) | Milliseconds (8-byte) |
|-------|-----------------|----------------------|
| Numeric timestamp | 10 digits | 13 digits |
| Hex | 8 chars | 16 chars |
| Escaped `\xHH` | 4 pairs | 8 pairs |
| Bytes array | 4 elements | 8 elements |

Detection priority: bytes > escaped > timestamp(13) > timestamp(10) > hex(16) > hex(8 with A-F) > time string.

### Forward conversion (time string → bytes)

- `datetime.timestamp()` returns float with sub-second precision
- Non-zero fractional part → 8-byte `>Q` (ms); zero → 4-byte `>I` (s, backward compatible)
- Support `2026-10-01 00:00:00.123` format in time strings

### Output

- `[Timestamp]` shows the raw integer (10-digit for s, 13-digit for ms)
- `[Hex]`/`[Escaped]`/`[Bytes]`/`[Java bytes]` show the full byte representation (8 bytes for ms)
- `[Time]` auto-precision: `.123` suffix only when ms

### Extract mode

- Sliding window: 4-byte AND 8-byte, each printed as separate candidates

## Non-changes

- Timezone handling
- Batch mode, stdin, --format behavior
- CLI interface (no new flags)

## Verification

```bash
python3 tests/test_time_convert.py   # all pass (new ms tests included)
python3 scripts/time-convert '1790784000123'              # ms timestamp → all formats
python3 scripts/time-convert '2026-10-01 00:00:00.123'   # ms time string → all formats
python3 scripts/time-convert '0000019538D05B40'           # 16-char hex → ms
```
