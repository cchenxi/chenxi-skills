# rowkey-convert Skill 完整性评审 TODO

> 两轮评审合并，共 32 项。按 P0/P1/P2 三级排列。

## P0 — 必须修

### 功能测试
- [x] **#7 `--format annotated` 无独立测试** — 其他 4 种格式都有 flag 测试，唯独 annotated 没有

### SKILL.md 质量
- [x] **#12 SKILL.md 过于简略** — 加 3-5 个输入/输出示例 + 错误处理指引（告诉 Claude 如何向用户展示结果、出错时怎么说），对标 time-convert 的 SKILL.md
- [x] **#28 description 缺乏触发场景** — 当前只描述 WHAT 没描述 WHEN。标准要求 description 包含触发条件，避免 under-triggering。建议改为含 `Use when the user pastes a rowkey string...` 句式
- [x] **#27 缺少 `allowed-tools` 字段** — Claude Code 扩展字段。不加的话每次调用脚本可能弹出权限确认，应声明 `Bash` 权限

### Python 依赖
- [x] **#16 未声明 Python 最低版本** — `list[int]` 类型注解 (PEP 585) 需要 Python ≥ 3.9。若用户只有 3.7/3.8 会报 `TypeError: 'type' object is not subscriptable`，信息极不友好。README/SKILL.md/CLAUDE.md 均未写明
- [x] **#17 `python3` 命令名不通用** — SKILL.md 中硬编码 `python3`。部分 Linux 只有 `python`，Windows 上是 `py` 或 `python`。需加 fallback 指引

## P1 — 建议修

### 文档与标准
- [ ] **#14 缺少与 time-convert 的交叉引用** — SKILL.md 中提一下 time-convert 可以解析行键中的时间戳
- [ ] **#13 SKILL.md 与 README.md 内容重叠** — SKILL.md 应侧重"指导 Claude 行为"而非重复 README 内容
- [ ] **#31 缺少 `user-invocable` 显式声明** — 虽默认 true 行为正确，但纯工具型 skill 应显式声明
- [ ] **#33 仓库 SKILL.md 与实际安装的不同步** — 仓库写 `python3 ./rowkey-convert`，安装后变 `python3 ~/.claude/skills/rowkey-convert/rowkey-convert`。两份内容有差异，维护易遗漏
- [ ] **#34 脚本路径在 SKILL.md 中硬编码** — 换安装路径就需改 SKILL.md。应让 Claude 基于 SKILL.md 所在目录推导脚本路径

### 代码健壮性
- [ ] **#4 `parse_mixed` 中非法 hex（如 `\xGG`）错误信息不友好** — 抛 Python 原生 `ValueError: invalid literal for int() with base 16: 'GG'`，应包装为用户可读的提示
- [ ] **#18 无 Python 可用性探测指引** — SKILL.md 中无一言提及"如果 python3 不可用怎么办"，Claude 只能靠试错

### Windows 兼容性
- [ ] **#21 Windows shebang 无效** — `#!/usr/bin/env python3` 在 CMD 中忽略，PowerShell 中 `env` 不存在
- [ ] **#22 SKILL.md 路径使用 Unix tilde** — `~/.claude/skills/...`，Windows 上为 `%USERPROFILE%\.claude\skills\...`，Claude 需自行翻译
- [ ] **#23 Windows 安装说明缺失** — README 只覆盖 `~/.zshrc` 追加 PATH，无 PowerShell/cmd 说明
- [ ] **#24 周边文档假设 Unix** — 脚本代码本身纯 stdlib 无平台调用 ✓，但文档、安装说明、SKILL.md 路径写法全是 Unix 视角。好消息：脚本代码无需改动

## P2 — 可选

### 功能增强
- [ ] **#1 不支持 annotated 格式的反向输入** — 输入检测中无 annotated 分支
- [ ] **#2 不支持从含上下文的行键文本中提取** — 对标 time-convert 的 `-e/--extract` 模式
- [ ] **#3 不支持 stdin 管道输入** — 无法 `echo '\x00\xFF' | rowkey-convert`

### 测试补全
- [ ] **#8 bytes 数组混用 `0x` 前缀无独立测试**
- [ ] **#9 全不可打印字符的 round-trip 测试缺失**
- [ ] **#10 空 bytes 数组 `[]` 无测试**
- [ ] **#11 Unicode 字符输入无测试** — 如中文 rowkey 的 UTF-8 编码在 mixed 模式下的行为

### 边界条件
- [ ] **#5 `detect_format` 把 `[]` 识别为 bytes 而非 empty** — 语义歧义
- [ ] **#6 没有对超长输入的保护** — 缺少 `--max-length` 类保护

### 文档
- [ ] **#15 CLAUDE.md 中 `--format` 选项列表漏了 `all`** — 代码实际支持但文档未列
- [ ] **#20 安装说明仅覆盖 zsh** — README 追加 PATH 只写 zsh，bash/fish/Windows 用户缺失
- [ ] **#25 .gitignore 无 Windows 排除项** — 缺少 `Thumbs.db`、`Desktop.ini` 等
- [ ] **#29 目录结构不符合推荐规范** — 标准推荐 `scripts/` 子目录存放可执行代码，当前脚本和测试文件与 SKILL.md 平级。需将 `rowkey-convert` → `scripts/rowkey-convert`，`test_rowkey_convert.py` → `tests/test_rowkey_convert.py`，并同步更新：SKILL.md 路径、README.md CLI 示例、CLAUDE.md 引用、测试中 `SCRIPT` 路径

### 兄弟 skill 同步
- [ ] **#19 time-convert 同样存在 Python 3.9 依赖** — `from zoneinfo import ZoneInfo` 也是 3.9+，3.8 需 `pip install backports.zoneinfo`
- [ ] **#35 time-convert SKILL.md 同样存在以上大部分问题** — 两个 skill 出自分支，建议同步整改
