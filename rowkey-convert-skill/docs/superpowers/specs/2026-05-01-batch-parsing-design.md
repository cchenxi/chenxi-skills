# rowkey-convert 批量解析设计

## 概述

为 rowkey-convert 新增 `--batch` 模式，支持按行批量解析多条 rowkey，每条独立检测格式并转换。

## CLI 接口

新增参数：

```
--batch, -b    按行批量解析，每行作为一条独立 rowkey
```

### 行为规则

- 按 `\n` 分割输入，逐行 `.strip()` 后处理
- 空行静默跳过
- 每条独立调用 `detect_format()` 检测格式 → 解析 → 转换
- 某行解析失败：stderr 输出 `Warning: line N: <reason>`，继续处理下一行
- 全失败：退出码 1；至少一行成功：退出码 0

### 互斥约束

- `--batch` 与 `--extract` 互斥，同时指定时报错
- 非 batch 模式行为零变化

### 与其他参数的交互

| 参数 | batch 模式行为 |
|------|---------------|
| `--format all` | A 模式：每条包裹分隔线，完整展示所有格式 |
| `--format <fmt>` | C 模式：每行输出一条转换结果，无标签无编号 |
| `--max-length N` | 对每行的 byte_list 独立校验 |
| stdin (`-`) | 支持，一致 |

## 输出格式

### A 模式（--format all）

```
--- [1] (mixed) ---
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

--- [2] (hex) ---
...
```

### C 模式（--format hex 等）

每行一条值，管道友好：

```
00FF68656C6C6F
00FF68656C6C6F
```

### 错误输出

成功的行 → stdout，失败的行 → stderr：

```
Warning: line 3: Invalid hex escape '\xGG' at position 0
```

## 实现

### 改动范围

单文件 `scripts/rowkey-convert`，约 40 行增量。

### 新增函数

`batch_process(input_text: str, fmt: str, max_length: int) -> int`

- 按 `\n` 分割，逐行 strip，跳过空行
- 每行调用 `parse_input()` 解析
- 成功：调用 `print_formats()`（A 模式外部包裹分隔线，C 模式直接输出值）
- 失败：stderr 警告，继续
- 统计成功/失败，返回 0 或 1

### 修改点

`main()` 函数：
- 添加 `--batch` / `-b` 参数
- 验证 `--batch` + `--extract` 互斥
- batch 模式时调用 `batch_process()` 替代单条流程

### 不动

- 所有 `parse_*` / `format_*` 函数
- `detect_format` / `parse_input`
- `print_formats`（A 模式分隔线在 `batch_process` 中组装）
- `extract_rowkeys`
- 现有参数语义

### 测试要点

- 两行 mixed + hex 混用 → 各自独立检测正确
- 空行跳过
- 某行解析失败 → 其他行照常输出，退出码 0
- 全失败 → 退出码 1
- `--batch --format hex` → 管道输出
- `--batch --extract` → 报错
- `--batch --max-length` → 超长行报错，其他行正常
- 非 batch 模式行为不变
