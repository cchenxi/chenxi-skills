# Rowkey Convert

在 Java + 大数据项目的运维场景中，快速转换 HBase rowkey 的多种表示形式。

## 解决的问题

HBase 中 rowkey 是 `byte[]`，通过 hbase shell 查询时，rowkey 显示为混合格式——非打印字符转义为 `\xHH`，可打印字符保持原样，例如 `\x00\xFFhello`。排查线上问题时，经常需要在以下形式间转换：

| 格式 | 示例 | 场景 |
|------|------|------|
| mixed | `\x00\xFFhello` | hbase shell 输出 |
| hex | `00FF68656C6C6F` | 日志 / 代码中搜索比对 |
| escaped | `\x00\xFF\x68\x65\x6C\x6C\x6F` | hbase shell 查询条件 |
| bytes | `[0, 255, 104, 101, 108, 108, 111]` | Python/通用（无符号） |
| java | `[-1, -2, -3]` / `[0, -1, 104]` | Java 代码中粘贴（有符号，补码），支持输入输出 |
| annotated | hex dump + ASCII 注解行 | 理解 rowkey 各字段含义 |
| (batch) | 多行输入，每行独立解析 | 批量转换多条 rowkey |

## 环境要求

- Python ≥ 3.9（使用 `list[int]` 类型注解）
- 无第三方依赖，仅需标准库

## 安装

### Linux / macOS

```bash
# bash
echo 'export PATH="$PATH:'"$(pwd)"'"' >> ~/.bashrc && source ~/.bashrc

# zsh
echo 'export PATH="$PATH:'"$(pwd)"'"' >> ~/.zshrc && source ~/.zshrc

# fish
echo 'set -gx PATH $PATH '"$(pwd)" >> ~/.config/fish/config.fish
```

### Windows (PowerShell)

```powershell
# 添加到当前用户 PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$pwd", "User")

# 或者直接通过 python 运行（无需安装到 PATH）
python scripts\rowkey-convert '<input>'
```

> **注意：** 脚本 shebang (`#!/usr/bin/env python3`) 在 Windows CMD 中不生效。Windows 用户请使用 `python` 或 `py` 显式调用，如 `python scripts/rowkey-convert '\x00\xFFhello'`。

## CLI 使用

```bash
# 正向：mixed → 全部格式
python3 scripts/rowkey-convert '\x00\xFFhello'

# 反向：hex → mixed
python3 scripts/rowkey-convert 00FF6865

# 反向：bytes → mixed
python3 scripts/rowkey-convert '[0, 255, 104]'

# 反向：Java bytes → mixed
python3 scripts/rowkey-convert '[-1, -2, -3]'

# 指定输出格式
python3 scripts/rowkey-convert '\x00\xFFhello' --format escaped
python3 scripts/rowkey-convert '\x00\xFFhello' --format bytes
python3 scripts/rowkey-convert 00FF6865 --format mixed

# 批量模式：每行一条 rowkey，独立检测格式
printf '\x00\xFFhello\n00FF68656C6C6F\n[0, 255, 104]' | python3 scripts/rowkey-convert - --batch

# 批量 + 指定格式（管道友好）
printf '\x00\xFFhello\n00FF68' | python3 scripts/rowkey-convert - --batch --format hex
```

输入格式自动识别，无需指定：
- 包含 `\xHH` → mixed
- `[-1,...]`（含负数） → java_bytes（有符号）
- `[...]`（非负数） → bytes（无符号）
- 纯 hex 字符串（偶数长度） → hex
- 其他（如纯可打印字符串 `hello`） → mixed

## Claude Code Skill 使用

在 Claude Code 对话中，直接粘贴 rowkey 字符串即可自动转换。Skill 文件位于 `SKILL.md`。

## 运行测试

```bash
python3 tests/test_rowkey_convert.py -v
```
