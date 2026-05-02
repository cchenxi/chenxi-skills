---
name: time-convert
description: "Convert between time strings and HBase rowkey time bytes (4-byte big-endian Unix timestamp). Forward: time → timestamp/hex/escaped/bytes/java. Reverse: timestamp/hex/bytes → time. Supports global timezones, batch mode, stdin."
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
