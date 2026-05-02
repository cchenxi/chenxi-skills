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

# Byte array
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
