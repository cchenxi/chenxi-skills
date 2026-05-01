# rowkey-convert Skill 完整性评审 TODO

> 两轮评审合并，共 32 项。按 P0/P1/P2 三级排列。

## P0 — 必须修 ✅

- [x] **#7 `--format annotated` 无独立测试**
- [x] **#12 SKILL.md 过于简略**
- [x] **#28 description 缺乏触发场景**
- [x] **#27 缺少 `allowed-tools` 字段**
- [x] **#16 未声明 Python 最低版本**
- [x] **#17 `python3` 命令名不通用**

## P1 — 建议修 ✅

- [x] **#14 缺少与 time-convert 的交叉引用**
- [x] **#13 SKILL.md 与 README.md 内容重叠**
- [x] **#31 缺少 `user-invocable` 显式声明**
- [x] **#33 仓库 SKILL.md 与实际安装的不同步** — 已改为相对路径
- [x] **#34 脚本路径在 SKILL.md 中硬编码** — 已改为相对路径
- [x] **#4 `parse_mixed` 中非法 hex 错误信息不友好** — 已包装为用户可读提示
- [x] **#18 无 Python 可用性探测指引** — 已加入回退策略 + dependencies 声明
- [x] **#21 Windows shebang 无效** — 已在 README 中说明 Windows 使用方式
- [x] **#22 SKILL.md 路径使用 Unix tilde** — 已改为相对路径
- [x] **#23 Windows 安装说明缺失** — 已添加 PowerShell 安装说明
- [x] **#24 周边文档假设 Unix** — 已在 README 中添加跨平台说明

## P2 — 可选

### 功能增强 ✅
- [x] **#1 不支持 annotated 格式的反向输入** — 已添加 detect + parse_annotated
- [x] **#2 不支持从含上下文的行键文本中提取** — 已添加 -e/--extract 模式
- [x] **#3 不支持 stdin 管道输入** — 已支持 `-` 作为 stdin 输入

### 测试补全 ✅
- [x] **#8 bytes 数组混用 `0x` 前缀无独立测试**
- [x] **#9 全不可打印字符的 round-trip 测试缺失**
- [x] **#10 空 bytes 数组 `[]` 无测试**
- [x] **#11 Unicode 字符输入无测试**

### 边界条件 ✅
- [x] **#5 `detect_format` 把 `[]` 识别为 bytes 而非 empty** — 已特殊处理为 empty
- [x] **#6 没有对超长输入的保护** — 已添加 --max-length

### 文档 ✅
- [x] **#15 CLAUDE.md 中 `--format` 选项列表漏了 `all`** — 已追加
- [x] **#20 安装说明仅覆盖 zsh** — 已添加 bash/fish
- [x] **#25 .gitignore 无 Windows 排除项** — 已添加 Thumbs.db, Desktop.ini
- [x] **#29 目录结构不符合推荐规范** — 已规范化 scripts/ + tests/

### 兄弟 skill 同步（暂不处理）
- [ ] **#19 time-convert 同样存在 Python 3.9 依赖**
- [ ] **#35 time-convert SKILL.md 同样存在以上大部分问题**
