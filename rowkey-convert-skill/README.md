# Rowkey Convert

在 Java + 大数据项目的运维场景中，快速转换 HBase rowkey 的多种表示形式。

## 解决的问题

HBase 中 rowkey 是 `byte[]`，通过 hbase shell 查询时，rowkey 显示为混合格式——非打印字符转义为 `\xHH`，可打印字符保持原样，例如 `\x00\xFFhello`。排查线上问题时，经常需要在以下形式间转换：

| 格式 | 示例 | 场景 |
|------|------|------|
| mixed | `\x00\xFFhello` | hbase shell 输出 |
| hex | `00FF68656C6C6F` | 日志 / 代码中搜索比对 |
| escaped | `\x00\xFF\x68\x65\x6C\x6C\x6F` | hbase shell 查询条件 |
| bytes | `[0, 255, 104, 101, 108, 108, 111]` | Java 代码中粘贴 |
| annotated | hex dump + ASCII 注解行 | 理解 rowkey 各字段含义 |

## 安装

```bash
# 加入 PATH（推荐）
echo 'export PATH="$PATH:'"$(pwd)"'"' >> ~/.zshrc
source ~/.zshrc
```

无需任何第三方依赖，仅需 Python 3。

## CLI 使用

```bash
# 正向：mixed → 全部格式
rowkey-convert '\x00\xFFhello'

# 反向：hex → mixed
rowkey-convert 00FF6865

# 反向：bytes → mixed
rowkey-convert '[0, 255, 104]'

# 指定输出格式
rowkey-convert '\x00\xFFhello' --format escaped
rowkey-convert '\x00\xFFhello' --format bytes
rowkey-convert 00FF6865 --format mixed
```

输入格式自动识别，无需指定：
- 包含 `\xHH` → mixed
- `[...]` → bytes
- 纯 hex 字符串（偶数长度） → hex
- 其他（如纯可打印字符串 `hello`） → mixed

## Claude Code Skill 使用

在 Claude Code 对话中，直接粘贴 rowkey 字符串即可自动转换：

```
用户: \x69\xEE\x0C\x50
Claude: [输出全部 5 种格式]
```

Skill 文件位于 `SKILL.md`，本质是对 CLI 脚本的薄封装。

## 运行测试

```bash
python3 -m unittest test_rowkey_convert -v
```
