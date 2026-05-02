# time-convert

时间字符串与 HBase rowkey 时间字节（4 字节 big-endian Unix 时间戳）互转工具。

## 背景

在 Java+大数据项目中，HBase rowkey 常以 4 字节 big-endian Unix 时间戳（精确到秒）编码时间。线上排查问题时，需要在 `hbase shell` 输出的 `\xHH` 格式与人类可读的时间字符串之间频繁互转。本工具自动化这一过程。

## 安装

### 方式一：作为 Claude Code skill

```bash
cp -r . ~/.claude/skills/time-convert/
```

之后在 Claude Code 中可直接通过 skill 调用。

### 方式二：独立命令行工具

```bash
cp scripts/time-convert /usr/local/bin/time-convert
chmod +x /usr/local/bin/time-convert
```

### 依赖

- Python 3.9+（无需额外 pip 安装，仅标准库）

## 用法

```
python3 ./scripts/time-convert <input> [-z 时区] [-f 格式] [-e] [-b]
```

### 基本示例

```bash
# 正向：时间字符串 → 所有格式
$ python3 ./scripts/time-convert '2026-04-26 21:00:00'
[Timestamp]     1777208400
[Hex]           69EE0C50
[Escaped]       \x69\xEE\x0C\x50
[Bytes]         [105, 238, 12, 80]
[Java bytes]    [105, -18, 12, 80]
[Time]          2026-04-26 21:00:00 +0800
```

### 反向转换

支持多种输入格式，自动检测：

```bash
# Hex（从 HBase shell 复制后去掉 \x 前缀）
$ python3 ./scripts/time-convert '69EE0C50'

# Escaped（HBase shell 原生格式）
$ python3 ./scripts/time-convert '\x69\xEE\x0C\x50'

# Bytes 数组
$ python3 ./scripts/time-convert '[105, 238, 12, 80]'

# Unix 时间戳
$ python3 ./scripts/time-convert '1777208400'

# 以上四种均输出相同结果 → 2026-04-26 21:00:00 +0800
```

### 支持的输入格式

| 格式 | 示例 |
|------|------|
| ISO 8601 | `2026-04-26T21:00:00`、`2026-04-26T21:00:00+08:00` |
| 日期时间 | `2026-04-26 21:00:00`、`2026-04-26 21:00` |
| 日期 | `2026-04-26` |
| 斜线分隔 | `2026/04/26 21:00:00` |
| 紧凑格式 | `20260426210000`、`20260426` |

### 时区

默认 `Asia/Shanghai` (UTC+8)。通过 `-z` 指定：

```bash
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' --tz UTC+0
$ python3 ./scripts/time-convert '2026-04-26 09:00:00' --tz America/New_York
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' --tz +9
```

支持三种时区写法：IANA 名（`Asia/Tokyo`）、UTC 偏移（`UTC+8`）、简写偏移（`+8`、`-5`）。

### 筛选输出格式

```bash
# 只需要 \xHH 格式，复制到 HBase shell 查询
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' -f escaped
\x69\xEE\x0C\x50

# 只需要时间戳
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' -f timestamp
1777208400

# Java signed bytes
$ python3 ./scripts/time-convert '2026-04-26 21:00:00' -f java
[105, -18, 12, 80]
```

可选值：`timestamp`、`hex`、`escaped`、`bytes`、`java`、`time`、`all`（默认）。

### 从混合行键提取时间

当一个行键包含前缀、时间戳、后缀等多个部分时，用 `-e` 扫描所有可能的时间片段：

```bash
$ python3 ./scripts/time-convert 'prefix_\x69\xEE\x0C\x50_data_\x67\x89\xAB\xCD' -e
--- 偏移 0 (\x69\xEE\x0C\x50) ---
[Timestamp]     1777208400
[Time]          2026-04-26 21:00:00 +0800
--- 偏移 0 (\x67\x89\xAB\xCD) ---
[Timestamp]     1737075661
[Time]          2025-01-17 09:01:01 +0800
```

### 批量模式

每行作为独立输入解析，格式自动检测：

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

管道友好输出（仅值，无标签）：

```bash
$ printf '2026-04-26 21:00:00\n69EE0C50' | \
    python3 ./scripts/time-convert - --batch --format hex
69EE0C50
69EE0C50
```

### stdin 输入

```bash
$ printf '%s\n' '\x69\xEE\x0C\x50' | python3 ./scripts/time-convert -
```

## 与 rowkey-convert 配合

```bash
# 场景：HBase shell 输出了一条行键，需要分析其中时间
$ python3 ~/.claude/skills/rowkey-convert/scripts/rowkey-convert \
    'prefix_\x69\xEE\x0C\x50' -f escaped
\x70\x72\x65\x66\x69\x78\x5F\x69\xEE\x0C\x50

# 取出时间部分直接用 time-convert 解析
$ python3 ./scripts/time-convert '\x69\xEE\x0C\x50'
```

## 测试

```bash
python3 tests/test_time_convert.py
```

33 个用例覆盖正向转换、反向转换（4 种输入）、时区（3 种写法）、格式筛选（含 java）、提取模式、批量模式（含管道友好、错误继续、batch+extract）。
