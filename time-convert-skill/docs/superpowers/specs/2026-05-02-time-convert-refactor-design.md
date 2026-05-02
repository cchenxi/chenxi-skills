# time-convert 重构设计

## Context

将 time-convert-skill 全面对齐 rowkey-convert-skill 的工程模式：目录结构、测试框架、SKILL.md 元数据、batch/stdin/extract 功能。

## 目录结构

```
time-convert-skill/
├── scripts/
│   └── time-convert          # 从根目录移入
├── tests/
│   └── test_time_convert.py  # 原 test_cases.py，改用 unittest
├── SKILL.md
├── CLAUDE.md
└── README.md
```

## 主脚本改造 (scripts/time-convert)

### 功能新增

- **`--batch` / `-b`**: 每行独立解析，自动检测格式，失败行 Warning→stderr 继续处理。全部失败→exit 1。`--batch --format hex` 每行仅输出值，管道友好。
- **stdin 输入**: `-` 作为 input，`sys.stdin.buffer.read()` + `latin-1` 解码。
- **`--batch` + `--extract` 组合**: 每行独立做 extract 扫描（与 rowkey-convert 不同，那里互斥）。

### 输出格式扩展

新增 `java` 格式：signed byte 数组，如 `[105, -18, 12, 80]`。`--format` choices 增加 `java`。

### 代码组织

保持现有逻辑，对齐 rowkey-convert 的风格：
- 分区注释 `# ---------- name ----------`
- `print_output()` → `print_formats()`，采用元组列表模式
- 新增 `batch_process()` 函数

### 不引入

- `--max-length`: 固定 4 字节场景无意义。

## 测试改造 (tests/test_time_convert.py)

手写 `check()` → `unittest.TestCase`，按场景分 class：

- `TestForwardConversion` — 时间字符串 → 各格式
- `TestReverseConversion` — hex/escaped/bytes/timestamp → 时间
- `TestTimezone` — IANA/UTC偏移/简写偏移
- `TestFormatFilter` — `-f` 各输出格式（含 java）
- `TestExtractMode` — `-e` 扫描
- `TestBatchMode` — `-b` 批量（含自动检测、管道友好、错误继续、batch+extract）
- `TestEdgeCases` — 紧凑格式、小写hex、空输入等

## SKILL.md

补充元数据：

```yaml
allowed-tools: Bash
dependencies: python>=3.9
user-invocable: true
```

更新脚本路径引用为 `./scripts/time-convert`。

## Verification

```bash
python3 tests/test_time_convert.py   # 全部 unittest 通过
python3 scripts/time-convert '2026-04-26 21:00:00'  # 正向全格式
python3 scripts/time-convert '69EE0C50'              # 反向 hex
python3 scripts/time-convert '2026-04-26 21:00:00' -f java  # Java bytes 输出
echo '\x69\xEE\x0C\x50' | python3 scripts/time-convert - --batch  # stdin batch
```
