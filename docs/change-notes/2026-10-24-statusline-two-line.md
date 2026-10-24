# Claude Code 状态栏两行改造 改动手册

## Metadata（元数据）

| 字段 | 内容 |
|---|---|
| 创建时间（Created At） | `2026-10-25 00:41`（CST，UTC+8） |
| 更新时间（Updated At） | `2026-10-25 00:57`（CST，UTC+8） |
| 作者（Author） | Claude Code（AI 助手） |
| 复核人（Reviewer） | 待确认 |
| 目的（Purpose） | 记录 2026-10-24 对 Claude Code 全局状态栏脚本（statusline）的改造，让用户不依赖 AI 也能独立复现、验证和回滚 |
| 关联仓库/项目（Related Repository / Project） | `mine-interest`（worktree：`mine-interest-source-hub`）；本文档位于当前项目 `docs/change-notes/`；改动对象是仓库外的全局配置 `/Users/mobius/.claude/` |
| 关联 Mission（Related Mission） | 无 |
| 关联会话（Related Session） | `bc24be92-e190-49c9-a8c6-249f455649ad`（`/Users/mobius/.claude/projects/-Users-mobius-Documents-111AAA-code-mine-interest-worktrees-mine-interest-source-hub/bc24be92-e190-49c9-a8c6-249f455649ad.jsonl`） |
| 当前状态（Status） | 已完成（脚本级验证通过；终端实际渲染未截图存档） |
| 文档边界（Scope / Boundary） | 非真相源；仅记录本次 statusline 改动；不覆盖同会话创建的 `change-handbook` skill；不代表已批准方案；不触发实现 |

> 文档位置：本文档位于当前项目的 `docs/change-notes/`，不写全局目录。改动对象全部在用户主目录（`/Users/mobius/.claude/`），不在仓库内，因此下文对改动对象使用绝对路径；仓库内路径才使用相对路径。
>
> 文件名沿用改动发生日期（2026-10-24）；文档实际创建于 2026-10-25 00:41。

## 一句话摘要

把 `~/.claude/statusline-command.sh` 从「用户名@主机 目录末级 | 剩余上下文 N%」的一行格式，改成 Codex 风格的两行：第一行「模型 推理强度 · Context N% left」，第二行完整路径（`$HOME` 显示为 `~`），并且不显示 Fast 段。

## 1. 改了什么

| 文件/对象 | 改动类型 | 改动前 | 改动后 |
|---|---|---|---|
| `/Users/mobius/.claude/statusline-command.sh` | 重写 | 一行：`<用户名>@<短主机名> <目录末级> \| 剩余上下文 <n>%`（1105 字节） | 两行：第一行 `<模型> <推理强度> · Context <n>% left`，第二行 `<完整路径>`（1664 字节） |
| `/Users/mobius/.claude/statusline-command.sh.bak` | 新增（备份） | 不存在 | 改动前原脚本的完整副本，1105 字节，时间 `2026-10-24 13:18:55` |
| `/Users/mobius/.claude/settings.json` | 本次对话未修改 | `statusLine` 已指向 `sh "$HOME/.claude/statusline-command.sh"` | 保持该接线不变。注意：该文件在 `2026-10-24 19:08:28` 还有一次与本次无关的变动，不在本文范围内 |
| Fast 段 | 未落地 | 规划阶段曾提议显示 `Fast on/off`（字段 `fast_mode`） | 用户明确要求去掉，最终脚本完全不读取 `fast_mode` |

补充事实：在 `13:19` 到 `13:37` 之间还存在过一个「单行 Codex 风格」的中间版本（`模型 · 路径 · Context`），随后被本次两行版本取代。`.bak` 保存的是最初的「用户名@主机」版，不是中间版。

## 2. 原理：为什么这样改会生效

Claude Code 的状态栏（status line）不是内置绘制的，而是**由它执行你配置的 shell 命令**：

```text
Claude Code 触发刷新
  → 读取 ~/.claude/settings.json 的 statusLine.command
  → 交给 shell 执行：sh "$HOME/.claude/statusline-command.sh"
  → 通过 stdin 传入当前会话 JSON
  → 读取脚本 stdout 的全部内容作为状态栏文本（支持多行、ANSI 颜色）
  → 在终端底部渲染
```

所以只要「配置指向这个脚本」且「脚本按约定读取 stdin、按约定输出 stdout」，改脚本内容就会改变状态栏样式，不需要动 `settings.json`。

脚本内部的数据流：

```text
stdin JSON
  ├─ .model.display_name（缺失回退 .model.id，再缺失显示 unknown）→ 第一行模型名
  ├─ .effort.level（缺失则省略）→ 第一行推理强度
  ├─ .context_window.remaining_percentage（缺失时用 100 - .used_percentage 换算，再缺失则省略）→ 第一行 Context N% left
  ├─ .workspace.current_dir（缺失回退 .cwd，再缺失用 pwd）→ 第二行路径
  └─ 路径前缀 $HOME 替换为 ~
        ↓
printf '%s\n%s\n' → 两行 stdout
```

关键点：

- `settings.json` 的命令是 `sh "$HOME/.claude/statusline-command.sh"`，即用 `sh` 显式执行，所以脚本**不需要可执行位**（当前权限 `644` 仍能工作）。
- `printf '%s\n%s\n'` 保证输出恰好两行；Claude Code 会把多行 stdout 原样渲染成多行状态栏。
- 分隔符 `\033[2m·\033[0m` 是「暗色（dim）圆点」，只影响中间点，主体保持纯色。

## 3. 为什么可以这么改（依据与边界）

- **依据**：
  - 官方文档 <https://docs.claude.com/en/docs/claude-code/statusline> 明确写明：脚本从 stdin 接收 JSON、stdout 即状态栏内容；支持多行、ANSI 转义；`model.display_name`、`workspace.current_dir`、`context_window.remaining_percentage`、`context_window.used_percentage`、`effort.level`、`fast_mode` 均为可用字段。
  - 本机 Claude Code 版本为 `2.1.202`（`claude --version`）。
  - 本次已用多组模拟 JSON 实测，输出与预期一致（见附录 B）。
- **前提条件**：
  - `jq` 在状态栏命令的 `PATH` 中（本机为 `/opt/homebrew/bin/jq`，版本 `jq-1.8.2`）。
  - `/bin/sh` 可用（macOS 上通常为 bash 3.2 的 POSIX 模式），脚本只用了 POSIX shell 语法。
  - `HOME` 环境变量已设置（用于把路径前缀替换为 `~`）。
  - 修改脚本后，状态栏不会立即重绘，需要等到下一次刷新触发（例如收到新的助手消息、`/compact` 完成、权限模式变化，或会话启动/恢复）。
- **风险与副作用**：
  - 状态栏脚本在本地执行，不消耗 API token。
  - 若 `jq` 缺失或不在 `PATH`，模型名会显示 `unknown`，其余片段被省略；不会影响 Claude Code 主流程。
  - 会话刚开始、尚未产生第一次 API 响应时，`remaining_percentage` 可能为 `null`，此时只显示「模型 [强度]」，Context 段自动省略。
  - 百分比用 `floor` 向下取整，`87.4` 会显示 `87`，与旧版直接打印 `87.4` 的行为不同。
  - 自定义模型的 `display_name` 若缺失，会回退显示原始 `model.id`（例如 `deepseek-v4.1-flash`），不是美化名称。
- **不适用范围**：
  - Codex 右下角的 `⚠ 1 warning · f2 to view` 无法复刻：该告警数量不在状态栏 JSON 中，脚本读不到（Claude Code 自己会在页脚显示告警）。
  - Windows 原生命令行/PowerShell 环境不适用本脚本（官方建议使用 PowerShell 或 Git Bash 单独配置）。
  - 若未来 Claude Code 更改 stdin 字段名，脚本需要同步调整；本文档基于 `2.1.202` 与当前官方文档。

## 4. 手动复现步骤

### 4.1 前置条件

- macOS（本机为 Darwin 25.2.0）。
- 已安装 `jq`：`jq --version` 应输出版本号。
- 已安装 Claude Code：`claude --version` 应输出版本号（本次为 `2.1.202`）。
- 对 `/Users/mobius/.claude/` 有读写权限。

### 4.2 步骤

1. 备份当前脚本。若 `.bak` 已存在，先确认它是不是你要保留的回滚源，不要直接覆盖。

   ```bash
   ls -l /Users/mobius/.claude/statusline-command.sh /Users/mobius/.claude/statusline-command.sh.bak 2>/dev/null
   [ -e /Users/mobius/.claude/statusline-command.sh.bak ] || cp /Users/mobius/.claude/statusline-command.sh /Users/mobius/.claude/statusline-command.sh.bak
   ```

   验证：两个文件都存在，`.bak` 是改动前的旧内容。如果 `.bak` 已存在，上面的命令不会覆盖它；确认它确实是你要保留的回滚源即可。

2. 执行「附录 A」里的完整写入命令。该命令用带引号的 `'EOF'` 创建 heredoc，避免 shell 提前展开 `$HOME` 等变量。

   验证：`sh -n /Users/mobius/.claude/statusline-command.sh && echo "syntax ok"` 输出 `syntax ok`。

   说明：不需要 `chmod +x`，因为 `statusLine.command` 显式用 `sh` 调用。长脚本放在附录 A 的顶层代码块里，避免列表嵌套导致 Markdown 把脚本里的 `#` 注释渲染成标题。

3. 确认 `settings.json` 已把状态栏接到这个脚本（本机已配置，通常只需核对）。

   ```bash
   jq '.statusLine' /Users/mobius/.claude/settings.json
   ```

   预期输出：

   ```json
   {
     "command": "sh \"$HOME/.claude/statusline-command.sh\"",
     "type": "command"
   }
   ```

   若为 `null`，先备份 `settings.json`，再精准合并这一段（不要整份覆盖）：

   ```bash
   cp /Users/mobius/.claude/settings.json /Users/mobius/.claude/settings.json.bak
   tmp=$(mktemp)
   jq '.statusLine = {"type":"command","command":"sh \"$HOME/.claude/statusline-command.sh\""}' \
     /Users/mobius/.claude/settings.json > "$tmp"
   jq empty "$tmp" && mv "$tmp" /Users/mobius/.claude/settings.json
   ```

   验证：再次执行 `jq '.statusLine' /Users/mobius/.claude/settings.json`，得到上面的 JSON。

4. 用模拟 JSON 离线验证，不依赖当前会话状态。

   ```bash
   printf '%s' '{"model":{"display_name":"DeepSeek V4.1 Flash"},"effort":{"level":"high"},"workspace":{"current_dir":"/Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub"},"context_window":{"remaining_percentage":87.4}}' | sh /Users/mobius/.claude/statusline-command.sh
   ```

   验证：输出两行，第一行形如 `DeepSeek V4.1 Flash high · Context 87% left`，第二行以 `~/Documents/111AAA-code/...` 开头。

5. 验证降级分支（无推理强度、无上下文数据）。

   ```bash
   printf '%s' '{"model":{"display_name":"DeepSeek V4.1 Flash"},"workspace":{"current_dir":"/Users/mobius"}}' | sh /Users/mobius/.claude/statusline-command.sh
   ```

   验证：输出为两行 `DeepSeek V4.1 Flash` 和 `~`，不出现 `Context`，也不报错。

### 4.3 最终验证

```bash
printf '%s' '{"model":{"display_name":"DeepSeek V4.1 Flash"},"effort":{"level":"high"},"workspace":{"current_dir":"/Users/mobius"},"context_window":{"remaining_percentage":87.4}}' \
  | sh /Users/mobius/.claude/statusline-command.sh \
  | perl -pe 's/\e\[[0-9;]*m//g' \
  | cat -n
```

预期结果（已实测）：

```text
     1	DeepSeek V4.1 Flash high · Context 87% left
     2	~
```

再回到 Claude Code 终端：随便发一条消息触发状态栏刷新，底部应看到两行，且第一行不再出现 `用户名@主机`、不再出现 `Fast` 字样。

## 5. 回滚方案

本次只改了脚本，`settings.json` 的 `statusLine` 无需回滚。

```bash
cp /Users/mobius/.claude/statusline-command.sh.bak /Users/mobius/.claude/statusline-command.sh
```

回滚后验证：

```bash
printf '%s' '{"model":{"display_name":"DeepSeek V4.1 Flash"},"workspace":{"current_dir":"/Users/mobius/Documents/x"},"context_window":{"remaining_percentage":60}}' | sh /Users/mobius/.claude/statusline-command.sh
```

预期：回到一行格式，形如 `mobius@<主机名> x | 剩余上下文 60`（旧版会保留小数，这里示例为整数）。状态栏在下次刷新时恢复旧样式。

注意：`.bak` 是本次改动前的「用户名@主机」版；如果之后又改过脚本，`.bak` 不会自动更新。

可选：如果连状态栏本身也不想要，可先备份 `settings.json`，再删除其中 `statusLine` 字段；这会关闭整个状态栏，影响范围大于本次改动，不建议作为默认回滚方式。

## 6. 已知限制与后续

- Fast 段：`fast_mode` 字段本身存在，但按用户要求未显示；若以后想加回，只需多读一个字段并在第一行拼接，不影响现有逻辑。
- 告警段（Codex 的 `⚠ 1 warning`）：状态栏 JSON 不提供告警数量，本轮不做，后续除非官方新增字段，否则无法实现。
- 百分比取整：当前 `floor` 向下取整；若希望四舍五入，把 `floor` 换成 `round` 即可（`jq` 1.6+ 支持）。
- 本次仅做离线模拟验证，终端里的真实渲染效果依赖下一次刷新触发；若出现模型名显示为原始 id，属于 `display_name` 缺失的回退行为，不是脚本错误。
- `settings.json` 在 `2026-10-24 19:08:28` 有过一次与本次无关的变动；本文只保证 `statusLine` 段仍指向该脚本，不对其他字段负责。
- 中间的单行 Codex 版本未单独备份，已被两行版本覆盖；如需追溯，可查会话记录（见 Metadata）。

## 附录 A：完整写入命令（含脚本全文）

把下面整段命令复制到终端执行即可写入脚本。heredoc 的结束标记 `EOF` 必须顶格。

```bash
cat > /Users/mobius/.claude/statusline-command.sh <<'EOF'
#!/bin/sh
# Claude Code 状态栏脚本（statusline），样式对齐 Codex CLI
#
# 输入：Claude Code 每次渲染时通过 stdin 传入的 JSON
#   .model.display_name                    当前模型名
#   .effort.level                          推理强度（low/medium/high/xhigh/max）
#   .workspace.current_dir                 当前工作目录
#   .context_window.remaining_percentage   上下文剩余百分比
#
# 输出（两行）：
#   第一行：<模型> <推理强度> · Context <n>% left
#   第二行：<完整路径>
#   路径中 $HOME 前缀替换为 ~，与 Codex 一致；
#   取不到推理强度或上下文百分比时，自动省略对应片段。

input=$(cat)

model=$(printf '%s' "$input" | jq -r '.model.display_name // .model.id // empty')
[ -n "$model" ] || model="unknown"
effort=$(printf '%s' "$input" | jq -r '.effort.level // empty')

# 路径：$HOME 前缀替换为 ~
cwd=$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // empty')
[ -n "$cwd" ] || cwd=$(pwd)
case "$cwd" in
  "$HOME") path="~" ;;
  "$HOME"/*) path="~${cwd#"$HOME"}" ;;
  *) path="$cwd" ;;
esac

# 上下文：优先剩余百分比，缺失时用已用百分比换算，都缺失则省略
remaining=$(printf '%s' "$input" | jq -r '
  if .context_window.remaining_percentage != null then .context_window.remaining_percentage
  elif .context_window.used_percentage != null then (100 - .context_window.used_percentage)
  else empty end | floor
')

sep=$(printf '\033[2m·\033[0m')
info="$model"
[ -n "$effort" ] && info="$info $effort"
[ -n "$remaining" ] && info="$info $sep Context ${remaining}% left"

printf '%s\n%s\n' "$info" "$path"
EOF
```

核对要点：模型读取 `.model.display_name`（回退 `.model.id`）、强度读取 `.effort.level`、路径读取 `.workspace.current_dir`（回退 `.cwd`）、上下文先读 `.context_window.remaining_percentage` 再用 `.context_window.used_percentage` 换算，最终用 `printf '%s\n%s\n'` 输出两行。

`/Users/mobius/.claude/settings.json` 的相关片段（其余字段未改动，且不在本文档中展开）：

```json
{
  "statusLine": {
    "command": "sh \"$HOME/.claude/statusline-command.sh\"",
    "type": "command"
  }
}
```

## 附录 B：命令与输出

本机环境取证：

```text
$ date '+%Y-%m-%d %H:%M:%S %Z'
2026-10-25 00:41:18 CST

$ stat -f '%N | size=%z | mtime=%Sm' /Users/mobius/.claude/statusline-command.sh /Users/mobius/.claude/statusline-command.sh.bak /Users/mobius/.claude/settings.json
/Users/mobius/.claude/statusline-command.sh | size=1664 | mtime=2026-10-24 13:37:46
/Users/mobius/.claude/statusline-command.sh.bak | size=1105 | mtime=2026-10-24 13:18:55
/Users/mobius/.claude/settings.json | size=2116 | mtime=2026-10-24 19:08:28

$ claude --version
2.1.202 (Claude Code)

$ jq --version
jq-1.8.2

$ sh -n /Users/mobius/.claude/statusline-command.sh && echo "syntax ok"
syntax ok
```

脚本复测（已去掉 ANSI 颜色）：

```text
[case1 正常]
DeepSeek V4.1 Flash high · Context 87% left
~/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub

[case2 HOME + 无 effort]
DeepSeek V4.1 Flash · Context 100% left
~

[case3 只有 used_percentage]
DeepSeek V4.1 Flash medium · Context 87% left
~/proj

[case4 无上下文数据]
deepseek-v4.1-flash
/tmp/demo

[case5 行数]
2
```

说明：`case1` 的完整命令见「4.3 最终验证」；其余用例省略了重复的完整 JSON 入参，只保留可观察输出。所有输出均为本次真实运行结果。
