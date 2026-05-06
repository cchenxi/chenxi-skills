# time-convert Mixed Format Support

## Context

Add "Mixed" format (HBase shell native format) as both input and output. Printable ASCII (0x20-0x7E) displayed as characters, non-printable bytes as `\xHH`.

Reference: rowkey-convert-skill `format_mixed`.

## Changes

### Input detection
Add "mixed" type between "bytes" and "escaped":
- `mixed`: contains `\xHH` AND at least one non-`\xHH` character
- `escaped`: pure `\xHH` sequences only

Priority: bytes > mixed > escaped > timestamp(12-13) > timestamp(10) > hex(16) > hex(8+A-F) > time

### format_mixed
```python
def format_mixed(byte_list: list[int]) -> str:
    result = []
    for b in byte_list:
        if 0x20 <= b <= 0x7E:
            result.append(chr(b))
        else:
            result.append(f'\\x{b:02X}')
    return ''.join(result)
```

### Output
Add "mixed" to FORMAT_LABELS and --format choices. Output appears between Escaped and Bytes.

### Tests
Add mixed format tests to TestFormatFilter and TestForwardConversion.

## Verification
```bash
python3 tests/test_time_convert.py   # all pass
```
