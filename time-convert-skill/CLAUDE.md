# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Code skill —— `time-convert`，用于在时间字符串与 HBase rowkey 中的 4 字节 big-endian Unix 时间戳之间互相转换。与 `rowkey-convert` skill 互补：rowkey-convert 处理行键格式转换（mixed/hex/bytes），time-convert 专注时间语义的编解码。

## 运行与测试

```bash
python3 time-convert '<input>' [-z TIMEZONE] [-f FORMAT] [-e]
python3 test_cases.py          # 运行全部 18 个测试用例
```

无构建步骤，无外部依赖（仅 Python 3.9+ 标准库）。Skill 需放在 `~/.claude/skills/time-convert/` 目录下。

## 架构

单文件脚本 `time-convert`，核心为两条转换路径：

- **正向** (time string → bytes)：`parse_time_string()` 解析输入 → `datetime.timestamp()` → `struct.pack('>I', ts)` 编码为 4 字节 → 5 种格式输出
- **反向** (bytes → time string)：`detect_input_type()` 识别格式 → `parse_to_timestamp()` 提取时间戳 → `datetime.fromtimestamp(ts, tz=tz)` 还原为时间字符串

输入检测优先级：`[bytes数组]` > `\xHH` escaped > 10位纯数字时间戳 > 8字符纯hex > 时间字符串。注意 hex 检测要求**恰好 8 字符**（对应 4 字节），否则回退到时间字符串解析（避免紧凑格式如 `20260426210000` 被误判）。

时间解析先尝试 `datetime.fromisoformat()`（ISO 8601），再回退到 `TIME_FORMATS` 列表中的 13 种 `strptime` 格式。无时区的输入默认使用 `Asia/Shanghai` (UTC+8)。

`-e/--extract` 模式扫描混合文本中的 `\xHH` 序列和 8+ 位 hex 序列，以 4 字节滑动窗口逐一解析每个候选时间戳。

## 时区处理

`parse_timezone()` 支持三种输入形式：
- IANA 时区名 → `ZoneInfo(name)`
- UTC 偏移格式（`UTC+8`, `UTC-5:30`）→ `timezone(offset)`
- 简写偏移（`+8`, `-5`）→ 同上

反向转换输出使用 `datetime.fromtimestamp(ts, tz=tz)` 还原到指定时区。
