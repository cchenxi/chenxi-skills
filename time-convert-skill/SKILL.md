---
name: time-convert
description: 时间与HBase rowkey字节互转。正向：时间字符串→时间戳/Hex/Escaped/Bytes。反向：时间戳/Hex/Bytes→时间字符串。支持全球时区，默认UTC+8。
---

# Time Convert

在时间字符串与 HBase rowkey 时间字节（4字节 big-endian Unix时间戳）之间互相转换。

## 用法

```bash
python3 time-convert '<input>' [-z TIMEZONE] [-f FORMAT] [-e]
```

## 示例

```bash
# 正向：时间字符串 → 字节表示
python3 time-convert '2026-04-26 21:00:00'
# [Timestamp]     1777208400
# [Hex]           69EE0C50
# [Escaped]       \x69\xEE\x0C\x50
# [Bytes]         [105, 238, 12, 80]
# [Time]          2026-04-26 21:00:00 +0800

# 反向：从 rowkey 片段还原时间
python3 time-convert '\x69\xEE\x0C\x50'
# → 2026-04-26 21:00:00 +0800

# 反向：Hex 输入
python3 time-convert '69EE0C50'

# 反向：时间戳输入
python3 time-convert '1777208400'

# 反向：Bytes 数组
python3 time-convert '[105, 238, 12, 80]'

# 指定时区
python3 time-convert '2026-04-26 21:00:00' --tz UTC+0

# 从混合行键中提取时间
python3 time-convert 'prefix_\x69\xEE\x0C\x50_data' -e

# 仅输出特定格式
python3 time-convert '2026-04-26 21:00:00' -f escaped
```
