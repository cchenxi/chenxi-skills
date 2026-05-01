---
name: rowkey-convert
description: Convert HBase rowkey between mixed (hbase shell), hex, escaped, bytes array, and annotated formats. Use when the user pastes a rowkey string like \x00\xFFhello, 00FF68656C6C6F, or [0, 255, 104] and needs to see it in other formats.
allowed-tools: Bash
dependencies: python>=3.9
user-invocable: true
---

# Rowkey Convert

Convert HBase rowkey between mixed, hex, escaped, bytes array, and annotated formats.

## Usage

```bash
python3 ./scripts/rowkey-convert '<input>' [--format hex|escaped|bytes|annotated|mixed|all] [--max-length N] [-e]
```

If `python3` is not available, try `python` or `python3.9`.

Additional modes:
- **stdin**: use `-` as input, e.g. `echo '\x00\xFF' | python3 ./scripts/rowkey-convert -`
- **extract**: `-e` scans mixed text (e.g. log lines) for `\xHH` sequences
- **max-length**: `-m N` limits maximum byte length (safety for large inputs)

## Examples

### Forward: mixed → all formats
```bash
python3 ./scripts/rowkey-convert '\x00\xFFhello'
```
```
[Hex]
00FF68656C6C6F

[Escaped]
\x00\xFF\x68\x65\x6C\x6C\x6F

[Bytes]
[0, 255, 104, 101, 108, 108, 111]

[Annotated]
00 FF 68 65 6C 6C 6F
 .   .   h   e   l   l   o

[Mixed]
\x00\xFFhello
```

### Reverse: hex → all formats
```bash
python3 ./scripts/rowkey-convert 00FF68656C6C6F
```

### Reverse: bytes array → all formats
```bash
python3 ./scripts/rowkey-convert '[0, 255, 104, 101, 108, 108, 111]'
```

### Single format output
```bash
python3 ./scripts/rowkey-convert '\x00\xFFhello' --format escaped
```
```
[Escaped]
\x00\xFF\x68\x65\x6C\x6C\x6F
```

## Displaying results

Show the full output to the user in a code block. If they only need a specific format, pass `--format`.

## Error handling

- If the script fails with `Error:`, relay the error message to the user and suggest checking the input format.
- If `python3` is not found, try `python` or `python3.9`. If none are available, tell the user that Python 3.9+ is required.
- Input auto-detection: `\xHH...` → mixed, `[...]` → bytes, even-length hex chars → hex, plain text (e.g. `hello`) → mixed.

## Related skills

- **time-convert**: Use when the user needs to extract or convert timestamps within a rowkey, rather than converting the rowkey format itself.
