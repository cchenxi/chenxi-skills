# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Code skill —— `time-convert`，用于在时间字符串与 HBase rowkey 中的 4 字节 big-endian Unix 时间戳之间互相转换。与 `rowkey-convert` skill 互补：rowkey-convert 处理行键格式转换（mixed/hex/bytes），time-convert 专注时间语义的编解码。

## Commands

```bash
# 正向: 时间字符串 → 各格式
python3 ./scripts/time-convert '2026-04-26 21:00:00'

# 反向: hex/escaped/bytes/timestamp → 时间
python3 ./scripts/time-convert '69EE0C50'
python3 ./scripts/time-convert '\x69\xEE\x0C\x50'
python3 ./scripts/time-convert '[105, 238, 12, 80]'
python3 ./scripts/time-convert '1777208400'

# 指定时区
python3 ./scripts/time-convert '2026-04-26 21:00:00' --tz UTC+0

# 筛选输出格式 (timestamp/hex/escaped/bytes/java/time/all)
python3 ./scripts/time-convert '2026-04-26 21:00:00' -f escaped

# 提取模式: 扫描混合文本中的时间片段
python3 ./scripts/time-convert 'prefix_\x69\xEE\x0C\x50_data' -e

# 批量模式: 每行独立解析
printf '2026-04-26 21:00:00\n69EE0C50' | python3 ./scripts/time-convert - --batch

# 从 stdin 读取
printf '%s\n' '\x69\xEE\x0C\x50' | python3 ./scripts/time-convert -

# 运行测试
python3 tests/test_time_convert.py
```

## Architecture

单文件 Python 脚本 (`scripts/time-convert`)，仅使用标准库（`argparse`, `re`, `struct`, `sys`, `datetime`, `zoneinfo`），无外部依赖。

**转换路径:**
- **正向** (time string → bytes): `parse_time_string()` → `datetime.timestamp()` → `struct.pack('>I', ts)` → 6 种格式输出
- **反向** (bytes → time string): `detect_input_type()` 识别格式 → `parse_to_timestamp()` 提取时间戳 → `datetime.fromtimestamp(ts, tz=tz)` 还原为时间字符串

**输入检测** (`detect_input_type`): `[bytes数组]` > `\xHH` escaped > 10位纯数字时间戳 > 8字符纯hex > 时间字符串。hex 检测要求恰好 8 字符（对应 4 字节），否则回退到时间字符串解析。

**输出格式:** `timestamp` (Unix 时间戳), `hex` (大写 hex), `escaped` (`\xHH` 格式), `bytes` (`[0, 255, ...]`), `java` (`[0, -1, ...]` signed bytes), `time` (格式化时间字符串)。

**提取模式** (`-e`): 扫描混合文本中的 `\xHH` 序列和 8+ 位纯 hex 序列，以 4 字节滑动窗口逐一解析每个候选时间戳。

**批量模式** (`-b`/`--batch`): 每行独立解析，自动检测格式。解析失败输出 `Warning:` 到 stderr 继续处理。支持与 `-e` 组合使用。

## 时区处理

`parse_timezone()` 支持三种输入形式:
- IANA 时区名 → `ZoneInfo(name)`
- UTC 偏移格式 (`UTC+8`, `UTC-5:30`) → `timezone(offset)`
- 简写偏移 (`+8`, `-5`) → 同上

反向转换输出使用 `datetime.fromtimestamp(ts, tz=tz)` 还原到指定时区。
