---
name: rowkey-convert
description: Convert HBase rowkey between mixed (hbase shell), hex, escaped, bytes array, and annotated formats
---

# Rowkey Convert

Convert HBase rowkey between mixed (hbase shell), hex, escaped, bytes array, and annotated formats.

## Usage

When the user provides a rowkey string (mixed `\x00\xFFhello`, hex `00FF68656C6C6F`, or bytes `[0, 255, 104]`), run the conversion script:

```bash
python3 ./rowkey-convert '<input>' [--format hex|escaped|bytes|annotated|all]
```

Show the full output to the user. If they only need a specific format, pass `--format`.
