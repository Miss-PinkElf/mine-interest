# Metadata（元数据）

- 创建时间（Created At）：2026-09-26 01:50:00 +08:00
- 更新时间（Updated At）：2026-09-26 01:50:00 +08:00
- 作者（Author）：Claude Code
- 目的（Purpose）：完整记录「Windows 上终端窗口反复一闪而过（Flash Window）」问题的排查过程、核心原理、三条实际链路、实测日志证据、解决方案与遗留风险，便于日后复查、复发时快速定位，以及给他人参考。
- 关联仓库或项目（Related Repository / Project）：mine-interest。**注意：问题实际发生在用户本机环境（`~/.codex`、VS Code 扩展），与本仓库的代码无关**，仓库内不包含任何相关源码。
- 关联 mission（Related Mission）：无。原因：本次是本机环境排障（Environment Troubleshooting），不属于本仓库的业务需求，无需走 devflow 的需求对齐（Align）与实施门禁（Apply Gate）。
- 当前状态（Status）：已完成（Completed）——本地已实施三处规避，实测生效。
- 文档边界（Scope / Boundary）：本文是**排查记录（Investigation Record），不是真相源（Source of Truth）**。所有结论基于 2026-09-26 凌晨的现场实测，属于特定版本（codex 0.157.0）与特定机器环境；上游若修复，结论中的「遗留问题」部分可能失效。本文**不会触发任何实现（Apply）或配置修改**，是记录而非方案批准书。

---

# Windows 终端窗口闪窗问题排查报告

## 1. 一句话结论

> **核心原因不是 codex，而是 Windows 的一条既定行为：一个「没有控制台（Console）」的进程去启动「控制台程序」时，Windows 必须为这个子进程新建一个控制台窗口——新建的窗口会显示出来，于是你看到「一闪而过」。**

本机一共有**三个**程序踩了这个坑，且它们互相独立：

| 编号 | 触发者 | 频率 | 与 codex 的关系 | 贡献度 |
|---|---|---|---|---|
| **A** | **VS Code 的 MarsCode 扩展** | **每 10.25 秒一次，永不停止** | **完全无关** | ⭐ **主因** |
| B | codex 的常驻守护进程（app-server daemon） | 启动 codex 时 4~5 次 | codex 自身 | 次因 |
| C | codex 的提权沙箱（elevated sandbox） | 每次沙箱操作 | codex 自身 | 再次 |

**最容易误判的一点**：由于 A 与 codex 无关，用户很容易把「敲 codex 时看到的闪窗」全部归因给 codex。实际上**频率最高的那条链路来自一个 VS Code 扩展**。

---

## 2. 现象描述

用户的原始描述：

> 我在 VS Code 的终端里面输入 `codex` 启动，会一闪而过很多终端框，很像我运行了 codex 之后，同时启动了很多别的东西。

补充现象：

> 我在 pwsh 里面输入 codex 也会出现这个情况。

**第二条补充现象恰恰是关键线索**：闪出来的窗口是弹在 **Windows 桌面**上的，它跟你在**哪个终端**里敲命令毫无关系。只要 VS Code 和 MarsCode 扩展在后台运行着，那每 10 秒一次的闪窗就会在**整个桌面**上持续发生，你在 pwsh、Windows Terminal 还是 VS Code 终端里敲命令都一样。

---

## 3. 核心原理：为什么 Windows 会闪窗

### 3.1 两个基础概念

1. **控制台程序（Console Application）**：编译为控制台子系统（Console Subsystem）的程序，例如 `git.exe`、`cmd.exe`、`tasklist.exe`、`powershell.exe`。这类程序**必须依附一个控制台**才能运行。
2. **控制台窗口宿主（Console Host）**：在 Windows 10 上，每个传统控制台窗口背后都有一个 `conhost.exe` 进程在支撑。

### 3.2 决定「闪不闪」的那条规则

```
父进程【已有】控制台  →  子进程【继承】同一个控制台     →  ✅ 不新建窗口
父进程【没有】控制台  →  Windows【必须新建】一个控制台   →  ❌ 新窗口一闪而过
```

这是 Windows 的**既定行为**，不是 bug。问题出在：**有程序使用了「无控制台的父进程」这个危险前提，却没有做规避。**

### 3.3 判定方法（本次排查的核心手段）

> **监控 `conhost.exe` 进程的创建，等价于监控「新控制台窗口的出现」。**

这条判定规则是本次排查能成功的关键。因为窗口「一闪而过」人眼抓不住，但 `conhost.exe` 进程是可以被程序捕获的。

**补充**：VS Code 内置终端使用的是 **ConPTY** 技术，它对应的是 `OpenConsole.exe` 而不是 `conhost.exe`。所以监控到的 `conhost.exe` **基本可以确定是真实弹到桌面上的窗口**，而不是某个终端内部的进程——这让结论更可信。

---

## 4. 三条链路逐一拆解（含实测日志）

以下所有日志均为 2026-09-26 凌晨本机实测抓取，格式为 `[时刻 +启动后秒数] 进程名 pid=xx | 父进程 pid=yy -> 父进程身份`。

### 4.1 链路 A：MarsCode 扩展（主因，与 codex 完全无关）

**触发者身份**：

```
C:\Users\Mobius\.marscode\ai-chat\binary\1.7.0\modules\ai-agent\ai-agent.exe --ideType vscode-external
```

该进程（PID 142132）由 VS Code 扩展 **`marscode.marscode-extension-1.7.0`**（豆包 MarsCode）启动。

**它执行的命令**：

```
tasklist /NH /FI "PID eq 142244"
```

即：**每 10 秒用它 `tasklist` 探测一次宿主进程是否存活。**

**实测日志（这一轮完全没有运行 codex）**：

```
[01:25:31.826 +11.0s] tasklist ppid=142132     ← 探测开始
[01:25:32.051 +11.3s] conhost                  ← 新的控制台窗口
[01:25:42.075 +21.3s] tasklist ppid=142132     ← 间隔 10.25s
[01:25:42.273 +21.5s] conhost
[01:25:52.299 +31.5s] tasklist ppid=142132     ← 间隔 10.22s
[01:25:52.524 +31.7s] conhost
[01:26:02.532 +41.7s] tasklist ppid=142132     ← 间隔 10.23s
[01:26:02.736 +41.9s] conhost
```

**为什么它没有控制台**：`ai-agent.exe` 是 VS Code 扩展的后台服务进程，由扩展宿主以无控制台方式拉起。

**结论**：**每 10.25 秒必闪一次，永不停止。这才是「一闪而过很多终端框」这个描述最大的贡献者。**

---

### 4.2 链路 B：codex 守护进程探测 git

**背景**：codex 从 0.155/0.156 版本起，架构从「单体 CLI」改为**客户端-服务器（Client-Server）架构**：

```
codex CLI（客户端）
      ↓ 通过命名管道 / unix socket 连接
codex.exe app-server --listen unix:// --managed-daemon（常驻后台守护进程）
```

好处是 CLI、VS Code 扩展、多个会话能共享同一个后端。

**问题所在**：这个守护进程是用 `--managed-daemon` 启动的，它**主动脱离控制台**运行。于是它每次去拉 `git.exe` 探测仓库时，Windows 就新建一个控制台窗口。

**实测日志（带父进程身份，链条闭环）**：

```
[01:36:01.099 +72.5s] git pid=154564
    父进程 144608 -> codex.exe ["\\?\C:\Users\Mobius\.codex\packages\app-server-daemon\
                                  releases\0.157.0-x86_64-pc-windows-msvc\bin\codex.exe"]

[01:36:01.572 +73.0s] conhost pid=153404
    父进程 151068 -> git.exe ["git" -c safe.bareRepository=explicit
                              -c core.hooksPath=NUL -c core.fsmonitor=false rev-parse HEAD"]
```

**完整链路**：

```
codex.exe  app-server-daemon (PID 144608，脱离控制台)
   └─ git.exe  rev-parse HEAD / rev-parse --git-dir
        └─ conhost.exe   ← 新控制台窗口一闪而过
```

**为什么发生在启动时**：codex 启动时要集中做一批仓库探测（判断当前目录是不是 git 仓库、HEAD 是什么），于是一次性闪 4~5 个窗口。实测约 6 秒内 5 个 `git` + 5 个 `conhost`。

---

### 4.3 链路 C：codex 的提权沙箱

**背景**：codex 在 Windows 上提供三种沙箱实现（下文 5.1 详述），其中 `elevated` 需要额外的提权辅助进程。

**实测日志**：

```
[00:42:38.604] codex.exe                            sandbox -- cmd.exe
[00:42:38.604] codex-windows-sandbox-setup.exe      ← 提权辅助进程
[00:42:38.863] cmd.exe                              cmd.exe C:/ "echo hi"
[00:42:38.863] conhost.exe                          ← 新控制台窗口
```

**对照组（同一命令，把沙箱改成 `unelevated` 后）**：

```
[00:44:03 +4s] node.exe codex.js sandbox -- cmd.exe /c "echo hi"
（无 codex-windows-sandbox-setup.exe、无 cmd.exe、无 conhost）
```

---

## 5. 关键配置项说明

本次涉及两个配置项，它们管的是**完全不同的两件事**，都在 `~/.codex/config.toml` 中。

### 5.1 `[windows] sandbox` —— 用哪种沙箱跑命令

**作用**：指定 codex 执行命令时用哪种沙箱（Sandbox）来隔离，限制它能读写哪些目录、能否联网。

**合法取值（从 codex 报错中直接取得，权威）**：

```text
unknown variant `__invalid__`, expected one of `elevated`, `unelevated`, `mxc`
in `windows.sandbox`
```

| 取值 | 含义 | 代价 |
|---|---|---|
| `elevated` | **提权**沙箱，隔离最强 | 需 `codex-windows-sandbox-setup.exe` 提权辅助进程，**每次带出新控制台窗口** |
| `unelevated` | **非提权**沙箱，用受限令牌（Restricted Token）运行 | 不弹窗，隔离强度略低 |
| `mxc` | 基于 Windows 沙箱容器的实现，更重 | 未实测 |

**这个值是怎么来的**：不是用户手写的。用户 2 月的旧配置（`config.toml.bak`）中有：

```toml
[features]
elevated_windows_sandbox = true
```

codex 0.157.0 把这个旧特性「转正」成了 `[windows] sandbox = "elevated"`，在更新时自动迁移写入。

### 5.2 `[features] daemon_auto_start` —— 是否自动拉起守护进程

**作用**：控制 codex 启动时**要不要自动拉起那个常驻后台的守护进程**。

**它是特性开关（Feature Flag），不是普通设置**，因此只能用 `codex features list` 查看：

```text
禁用前：  daemon_auto_start    stable    true      ← 默认值
禁用后：  daemon_auto_start    stable    false
```

**关掉的代价**：失去「CLI 与 VS Code 扩展共享同一个后端」的能力。每次启动 codex 是独立会话。

---

## 6. 排查方法论（为什么第一次会误判）

这一节记录排查过程中的弯路，因为它比结论本身更有复用价值。

### 6.1 第一次误判

第一次只测试了「沙箱命令」这一条路径，**确实抓到了** `codex-windows-sandbox-setup.exe` → `cmd.exe` → `conhost.exe` 的完整链条，于是下了「根因是 `elevated` 沙箱」的结论并修改了配置。

**但修改后用户反馈「没有消失」** —— 说明判断不完整。

### 6.2 误判的两个原因

| 原因 | 说明 |
|---|---|
| **采样盲区** | 第一版监控用轮询方式（约 300~500ms 一次），而控制台窗口存活常常不足 150ms，会被漏掉 |
| **信号淹没** | codex 启动那一瞬间进程密集爆发，把「每 10 秒一次」的规律性信号淹没了，导致周期性没被识别出来 |

### 6.3 突破点：对照组（Control Group）

真正的突破是设计了**对照组**：

> **在完全不运行 codex、不做任何操作的情况下，观察 45 秒。**

结果直接抓到 MarsCode 那条 `tasklist → conhost` 的链路，**周期精确到 10.25 秒**。这一步把「codex 因果」和「一直存在但被忽视的背景现象」彻底分开了。

### 6.4 方法论沉淀

```text
1. 判定闪窗：监控 conhost.exe 的创建（而不是试图用肉眼抓窗口）
2. 归因：必须同时记录【父进程 PID + 父进程身份】，只有 PID 不够
3. 分离混淆变量：一定要做「不触发嫌疑对象」的对照组
4. 提高采样率：短命进程要求高频采样（本次最终为约 50ms 级）
5. 警惕周期性信号被突发信号淹没：先找规律，再看爆发
```

---

## 7. 解决方案（已实施）

| # | 针对链路 | 措施 | 具体操作 | 状态 |
|---|---|---|---|---|
| 1 | **A：MarsCode** | **禁用扩展** | VS Code 扩展面板禁用 `marscode.marscode-extension`，然后 `Developer: Reload Window` | ✅ 已完成 |
| 2 | B：codex 守护进程 | 关闭自动拉起 | `codex features disable daemon_auto_start` | ✅ 已完成 |
| 3 | C：codex 提权沙箱 | 改为非提权 | `~/.codex/config.toml` 中 `[windows] sandbox = "unelevated"` | ✅ 已完成 |

**注意第 1 项的操作细节**：禁用扩展后**必须重载 VS Code 窗口**，否则已在后台运行的 `ai-agent.exe` 不会被停掉，闪窗仍会继续。

### 7.1 当前配置状态

```toml
# ~/.codex/config.toml
[windows]
sandbox = "unelevated"

[features]
daemon_auto_start = false
```

### 7.2 回滚方式

| 想恢复 | 操作 |
|---|---|
| 恢复提权沙箱 | `sandbox = "elevated"` |
| 恢复守护进程自启 | `codex features enable daemon_auto_start` |
| 全部还原 | 使用备份 `config.toml.bak-20260926-sandbox` / `config.toml.bak-20260926-daemon` |
| 恢复 MarsCode | VS Code 扩展面板中「启用」 |

---

## 8. 验证结果

### 8.1 禁用 MarsCode 后：静置 65 秒零闪窗

```
[01:34:51.504 +2.9s]   ← 最后一条记录
        ↓  整整 65 秒，无任何 conhost / tasklist
[01:35:56.377 +67.8s]  ← 这里才是用户敲 codex 的时刻
```

同时 `tasklist` **完全消失**（此前稳定 10 秒一次）。

### 8.2 关闭守护进程后：git 照跑，但不再产生窗口

关闭后的一段监控中，`git` 进程仍在正常运行（5 个），但**没有任何一个产生 conhost 窗口**，也没有任何 conhost 挂到 git 名下。

> **这正是预期的效果**：仓库探测工作回到由 CLI 自己做，而 CLI 是从终端启动、**继承终端控制台**的，它拉起的 `git` 继承同一个控制台，因此无需新建窗口。

### 8.3 用户主观确认

> 没有了。

---

## 9. 遗留问题与风险

### 9.1 重要：以上全部是「规避」，不是「修复」

| | 说明 |
|---|---|
| **真正的修复** | 由程序作者在启动子进程时加上 `CREATE_NO_WINDOW` 标志，显式告诉 Windows「不要开窗口」 |
| **本次所做** | 把「触发条件」拆掉（禁用扩展 / 关掉无控制台的守护进程 / 换掉提权沙箱），**并没有修正程序本身的行为** |

### 9.2 上游状态（codex 侧）

这是 OpenAI Codex 一个**已被广泛报告**的 Windows 问题：

| Issue | 内容 |
|---|---|
| [#48059](https://github.com/openai/codex/issues/48059) | [Windows][Codex CLI 0.157.0] Terminal windows repeatedly pop up during normal use。报告的进程链为 `codex.exe → app-server --managed-daemon → powershell.exe → conhost.exe`，**与本次实测链路一致** |
| [#48074](https://github.com/openai/codex/issues/48074) | Windows: terminal windows repeatedly flash during requests **after installing the Codex daemon** |
| [#48120](https://github.com/openai/codex/issues/48120) | 0.157.0 spawns blank Windows Terminal windows during sandbox setup refresh。其配置正是 `[windows] sandbox = "elevated"` |
| #48070（已作为重复关闭） | 对比结论：0.157.0 与 0.156.x 都会弹窗，**降级到 0.155.0 后消失** |

### 9.3 已知复发风险

**VS Code 的 `openai.chatgpt` 扩展自己也运行着一个 `codex.exe app-server`**（命令行：`-c features.code_mode_host=true app-server --analytics-enabled`）。它有可能**绕开 `daemon_auto_start` 开关、自行把守护进程重新拉起来**。

**复发时的检查步骤**：

```bash
codex app-server daemon version        # 看守护进程是否又跑起来了
codex features list | grep daemon      # 确认开关状态是否仍为 false
```

若确认是扩展拉起的，需要进一步排查扩展侧配置。

### 9.4 未处理的独立问题

- `~/.codex/logs_2.sqlite` 已达 **1.4 GB**（但仅 6,448 行，说明单行载荷极大），`~/.codex` 目录总计 **3.0 GB**。本次**未做任何处理**。
- codex 守护进程日志中存在大量网络重试报错（`chatgpt.com/backend-api/ps/mcp` 返回 `HTTP 502`、`tls handshake eof`），与代理链路有关，本次未处理。

---

## 10. 附录

### 10.1 本次涉及的环境信息

| 项目 | 值 |
|---|---|
| 操作系统 | Windows 10 Enterprise LTSC 2021（10.0.19044） |
| codex 版本 | codex-cli 0.157.0（2026-09-25 22:44 更新） |
| 安装方式 | npm 全局安装 |
| 涉事扩展 | `marscode.marscode-extension-1.7.0` |
| 排查工具 | PowerShell 轮询脚本（监控 `[System.Diagnostics.Process]::GetProcesses()` 新进程 + CIM 解析父进程身份） |

### 10.2 复现排查用的监控脚本思路

```powershell
# 核心逻辑（ASCII 纯英文，避免 PowerShell 5.1 按 GBK 解析无 BOM 的 .ps1 导致语法错误）
1. 先对所有现存进程做一次快照，作为「已见」种子
2. 循环（高频，约 50ms）枚举全部进程
3. 对每个【新出现】的 PID：
     - 记录时刻、进程名
     - 用 CIM 查询它的父进程 PID，并解析父进程的【名字 + 命令行】
4. 只输出关心的进程名（conhost / git / cmd / tasklist）
```

### 10.3 踩过的坑（供他人参考）

| 坑 | 后果 | 规避 |
|---|---|---|
| `.ps1` 文件含中文且无 BOM，用 Windows PowerShell 5.1 执行 | 按 GBK 解析导致语法错误，脚本根本没跑起来，白等 120 秒 | 脚本内容全用 ASCII；或改用 PowerShell 7；或保存为带 BOM 的 UTF-8 |
| 只记录父进程 PID，不记录父进程身份 | PID 会被复用，短命进程的父进程归因不可靠 | 同时解析父进程的名字与命令行 |
| 没有对照组 | 把「一直存在的背景闪窗」误判为「被触发对象引起的」 | 必须做「不触发嫌疑对象」的对照实验 |
| 第一轮 curl 直连 `downloads.claude.ai` 超时 | 与本次问题无关，是另一件事（`claude update` 的版本检查失败） | — |

---

## 11. 最终链路总图

```text
【根因层】Windows 既定行为
    无控制台的父进程 + 启动控制台子程序  →  必须新建控制台窗口（显示出来 = 一闪而过）
                              ↑
                              │  谁踩了这个坑
                              │
【触发层】  ① MarsCode 扩展  ai-agent.exe → tasklist      每 10.25 秒，永不停止   ← 主因
            ② codex 守护进程  app-server-daemon → git      启动时 4~5 次
            ③ codex 提权沙箱  sandbox-setup.exe → cmd      每次沙箱操作
                              │
                              │  对应的解法
                              ↓
【规避层】  ① 禁用 MarsCode 扩展（+ 重载 VS Code 窗口）
            ② codex features disable daemon_auto_start
            ③ [windows] sandbox = "unelevated"
                              │
                              │  但都不是根治
                              ↓
【根治层】  需程序作者在启动子进程时加 CREATE_NO_WINDOW
            codex 侧：上游 issue #48059 / #48074 跟踪中，等 OpenAI 修复
            MarsCode 侧：需向豆包反馈，当前只能禁用
```
