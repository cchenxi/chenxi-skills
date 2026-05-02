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
python3 ./scripts/rowkey-convert '<input>' [--format hex|escaped|bytes|java|annotated|mixed|all] [--max-length N] [-b|--batch] [-e]

```


If `python3` is not available, try `python` or `python3.9`.

Additional modes:
- **stdin**: use `-` as input, e.g. `echo '\x00\xFF' | python3 ./scripts/rowkey-convert -`
- **batch**: `-b`/`--batch` treats each line as an independent rowkey
- **extract**: `-e` scans mixed text (e.g. log lines) for `\xHH` sequences
- **max-length**: `-m N` limits maximum byte length (safety for large inputs)

## Examples

### Forward: mixed → all formats
```bash
python3 ./scripts/rowkey-convert '\x00\xFFhello'
```
```
[Input] (mixed)
\x00\xFFhello

[Mixed]
\x00\xFFhello

[Hex]
00FF68656C6C6F

[Escaped]
\x00\xFF\x68\x65\x6C\x6C\x6F

[Annotated]
00 FF 68 65 6C 6C 6F
 .   .   h   e   l   l   o

[Bytes]
[0, 255, 104, 101, 108, 108, 111]

[Java bytes]
[0, -1, 104, 101, 108, 108, 111]
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

### Batch mode: multi-line input
```bash
printf '\x00\xFFhello\n00FF68656C6C6F\n[0, 255, 104]' | python3 ./scripts/rowkey-convert - --batch
```
```
--- [1] (mixed) ---
[Input] (mixed)
\x00\xFFhello
...

--- [2] (hex) ---
[Input] (hex)
00FF68656C6C6F
...

--- [3] (bytes) ---
[Input] (bytes)
[0, 255, 104]
...
```

### Batch + pipe-friendly output
```bash
printf '\x00\xFFhello\n00FF68' | python3 ./scripts/rowkey-convert - --batch --format hex
```
```
00FF68656C6C6F
00FF68
```

## Displaying results

Show the full output to the user in a code block. If they only need a specific format, pass `--format`. For batch mode, pipe / multi-line input through stdin with `-`.

## Error handling

- If the script fails with `Error:`, relay the error message to the user and suggest checking the input format.
- In batch mode, parse errors on a single line produce a `Warning:` to stderr but do not stop processing of remaining lines.
- If `python3` is not found, try `python` or `python3.9`. If none are available, tell the user that Python 3.9+ is required.
- Input auto-detection: `\xHH...` → mixed, `[...]` → bytes, even-length hex chars → hex, plain text (e.g. `hello`) → mixed.

## Related skills

- **time-convert**: Use when the user needs to extract or convert timestamps within a rowkey, rather than converting the rowkey format itself.
