# cc-qq 代理输出超长行导致 ValueError 修复计划（Align + Plan）

## Metadata（元数据）

- 创建时间（Created At）：2026-11-01 00:26:00 +08:00
- 更新时间（Updated At）：2026-11-01 00:26:00 +08:00
- 作者（Author）：Claude
- 目的（Purpose）：定位并修复 `[cc-qq] 消息处理失败：ValueError` 的真实根因，给出候选方案与修改点。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 当前状态（Status）：已批准、实施并发布 `0.3.2`（生产与测试安装目录已覆盖并重启）
- 文档边界（Scope / Boundary）：本文件是本次修复的 Align + Plan 真相源，含实施记录；发布动作需另行批准。

## 一、问题现象

- 生产 AstrBot 日志（本地时间）：

  ```
  [00:16:51.964] [astrbot_plugin_cc_qq] [ERRO] [v4.29.3] [astrbot_plugin_cc_qq.main:276]: [cc-qq] 消息处理失败：ValueError
  11-01 00:16:32 [info] 17号 | 接收 <- 群聊 [绘赢喵(209267585)] [鱼鱼猫(1961618848)] 对的
  11-01 00:16:51 [info] 17号 | 发送 -> 私聊 (1961618848) 处理消息时发生错误，请联系插件管理员查看日志。
  ```

- 用户侧表现：私聊发「用skill画」后长时间无回复，约 9 分半后收到通用报错文案，代理本轮工作全部丢失。

> 说明：`对的` 是群聊消息且未 @bot，按设计被忽略；真正失败的是私聊消息「用skill画」（见证据 1），报错文案因失败消息来自私聊而发到私聊，两条日志只是时间上相邻。

## 二、证据链

1. 插件数据库 `~/.astrbot/data/plugin_data/astrbot_plugin_cc_qq/cc_qq.sqlite3`
   - `message_receipts` 行 220：`message_id=1283608079`，私聊 `1961618848`，文本「用skill画」，`status=error`，`created_at=2026-10-31 16:07:14`（UTC，本地 00:07:14）。
   - `turns` 表**没有**该消息的记录：异常发生在记录轮次之前。
2. Claude Code 会话记录 `~/.claude/projects/-Users-mobius-Documents-111AAA-code----/36455ffd-204a-41aa-90ab-97dce0a3105b.jsonl`
   - 第 276 行：`tool_result`，**1,050,933 字节**，内容是一次 `Read` 返回的 PNG 图片 base64（预览头 `iVBORw0KGgo...`）。
   - 该行时间戳 `2026-10-31T16:16:51.152Z`，与插件报错 `16:16:51.964` 相差不足 1 秒。
   - 之后只有一条 `Read`（`artifacts/aeolian-lines/crop-sun.png`）与一条 10KB 的 `tool_result`，**没有任何 `result` 收尾事件** → 代理进程被插件终止。
3. 代码路径
   - `agents/process.py:82` 以 `limit=MAX_AGENT_OUTPUT_LINE_BYTES`（`1_048_576`，即 1 MiB）创建 stdout 的 `StreamReader`。
   - `agents/process.py:107-108` 使用 `await process.stdout.readline()` 逐行读取，只捕获 `asyncio.TimeoutError`。
   - Claude 以 `--print --output-format stream-json --verbose` 运行，工具结果（图片 base64）会作为单行 JSON 输出；单行超过 limit 时，asyncio 的 `readline()` 抛 `ValueError`。
4. 本机实验（使用 AstrBot 自带 Python 3.12.13 复现）
   - `StreamReader(limit=1MiB).readline()` 读到 1,050,000 字节单行 → `ValueError: Separator is found, but chunk is longer than limit`。
   - 捕获该异常后继续 `readline()`，仍能读到下一行完整 JSON → 超长行已被消费，流可继续使用。

## 三、根因

`ProcessRunner.run()` 使用 `asyncio.StreamReader.readline()` 读取代理 stdout，而 `StreamReader` 的 `limit` 只允许单行 ≤ 1 MiB。Claude Code 的 `stream-json` 会把工具结果（含图片 base64）作为**单行**输出；当单行超过 1 MiB，`readline()` 抛 `ValueError`。

该异常不在 `ProcessRunner` 的处理范围内（只捕获 `asyncio.TimeoutError`），也不会被 `ClaudeAdapter`（只捕获 `AgentProcessError`）或 `sessions._execute` 捕获，最终：

```
ProcessRunner.run → ValueError
  → service.handle 标记 RECEIPT_ERROR 并重新抛出
  → main.py:276 记录「消息处理失败：ValueError」并回复 SERVICE_ERROR_REPLY
```

`finally` 中 `_terminate(process)` 终止代理进程，因此本轮工作丢失、无 `turns` 记录。

## 四、影响范围

- 所有通过该插件启动的 Claude 会话（群聊与私聊、只读/工作区/完全权限均相同）。
- 触发条件：代理单条输出行 > 1 MiB。实际最常见来源是 `Read` 图片（base64 约为原图 1.33 倍）、超大文件或超大工具输出。本次为 525 KB PNG → 1.05 MB JSON。
- Codex 适配器共用同一个 `ProcessRunner`，同样存在理论风险（`--json` 行通常较小，概率低）。
- 失败时用户只看到通用报错，代理已做的工作全部丢失，属于「静默丢工作」级别的缺陷。

## 五、候选方案

### 方案 A：只调大单行上限（最小改动）

- 做法：把 `MAX_AGENT_OUTPUT_LINE_BYTES` 从 1 MiB 调到如 8 MiB / 16 MiB。
- 优点：一行常量改动，风险最低。
- 缺点：只是把墙往后挪。更大的图片/工具输出仍会触发同样异常；`StreamReader` 会把整行缓存在内存中，上限越大内存峰值越高。
- 结论：不推荐单独使用，可作为方案 B 的配套上限。

### 方案 B：改为分块读取 + 有界行缓冲（推荐）

- 做法：不再用 `readline()`，改为 `await process.stdout.read(STDOUT_READ_CHUNK_BYTES)` 分块读取，在插件内按 `\n` 切行：
  - 正常行（≤ 上限）照常产出；
  - 超限行（> 上限）整行丢弃，并记录一条 warning（含丢弃字节数），继续读下一行；
  - 内存只保留「当前行」与一个读块，上限固定、可控。
- 优点：
  - 彻底消除 `ValueError`，与行长度无关；
  - 不依赖 CPython `readline()` 的内部行为；
  - 被丢弃的通常是插件本来就忽略的 `user`/`tool_result` 事件，不影响最终 `result` 文本。
- 缺点：需要在 `process.py` 新增约 25~35 行读取逻辑，并补单测。
- 默认上限建议：`MAX_AGENT_OUTPUT_LINE_BYTES = 8 * 1024 * 1024`（8 MiB），覆盖常见 QQ 图片 base64；超过才丢弃。

### 方案 C：捕获 `ValueError` 后继续（最小兜底）

- 做法：在 `readline()` 外层 `except ValueError`，记录 warning 后继续循环。
- 优点：约 5 行改动；实验证明超长行已被消费，流仍可继续读。
- 缺点：
  - 依赖 `StreamReader.readline()` 的当前实现语义；
  - 会吞掉该位置的所有 `ValueError`，可能掩盖其他缺陷；
  - 若超长行远大于上限，会连续多次抛错并丢弃多个 1 MiB 片段，日志噪声大。
- 结论：可作为临时热修，不建议作为长期方案。

## 六、推荐方案（方案 B）修改点清单

| 文件 | 函数/位置 | 行为变化 |
| --- | --- | --- |
| `integrations/astrbot/astrbot_plugin_cc_qq/constants.py` | `MAX_AGENT_OUTPUT_LINE_BYTES` | 1 MiB → 8 MiB，并补充注释说明「超限整行丢弃」语义 |
| `integrations/astrbot/astrbot_plugin_cc_qq/constants.py` | 新增 `STDOUT_READ_CHUNK_BYTES = 65_536` | 分块读取的块大小，避免魔法数字 |
| `integrations/astrbot/astrbot_plugin_cc_qq/agents/process.py` | 新增 `iter_stdout_lines(stream, max_line_bytes)`（模块级异步生成器） | 分块读取、按行切分、超长整行丢弃并 warning |
| `integrations/astrbot/astrbot_plugin_cc_qq/agents/process.py` | `ProcessRunner.run()` | 用 `iter_stdout_lines` 替代 `process.stdout.readline()`；超时控制改为对「读取一个块」设置 `DEFAULT_AGENT_TIMEOUT_SECONDS` |
| `integrations/astrbot/astrbot_plugin_cc_qq/tests/` | 新增 `test_process_stream.py` | 覆盖：正常行、超长行被丢弃后仍能读到后续 result、无换行 EOF 处理 |
| `integrations/astrbot/astrbot_plugin_cc_qq/metadata.yaml`、`constants.py` | 版本号 | `0.3.1` → `0.3.2`（是否升版见第九节，待确认） |
| `.devflow/cc-qq-full-migration/` | `bug-log.md`、`state.md`、`checkpoints.md` | 修复实施并验证后同步记录 |

> 超时语义说明：原实现对每次 `readline()` 设置 1800 秒超时。方案 B 对每次 `read(块)` 设置同样的超时，等价于「持续无输出才中断」；代理有输出时不会误杀。

### 可选附带改动（需用户确认）

- `main.py:275-277` 当前只记录异常类型（`type(exc).__name__`），导致本次排查只能靠反查数据库与会话 JSONL。建议改为记录异常类型 + 异常消息，或 `exc_info=True` 输出完整堆栈。属于可观测性改进，不影响功能；是否纳入本次由用户决定。

## 七、验证方式

1. **单测**：新增 `test_process_stream.py`，覆盖超长行丢弃、超长行之后的 JSON 仍被解析、EOF 尾行处理；全量单测需保持 159/159 以上通过（新增后总数增加）。
2. **定向复现**：用 AstrBot 自带 Python 启动脚本，向 `ProcessRunner.run` 喂一条 1.05 MiB 单行 + 一条 `{"type":"result","result":"ok"}`，断言不抛 `ValueError` 且能收到 `ok`。
3. **真机复测**：在私聊重复图片读取场景（让代理 `Read` 一张 >750 KB 的图片），确认：
   - 无 `ValueError`；
   - 能正常返回最终回复；
   - 数据库 `message_receipts` 状态为 `done`、`turns` 有记录。
4. **回归**：媒体 suite 6/6、基础命令 suite 4/4 的既有结论不回归（若时间允许）。
5. **发布（待批准）**：生成 `0.3.2` ZIP，覆盖生产与测试安装目录，重启/重载后确认日志出现「已加载 v0.3.2」。

## 八、风险与回滚

- 风险：分块读取实现错误可能造成输出粘包/丢行；通过单测 + 复现脚本 + 真机复测降低。
- 风险：8 MiB 上限仍可能被极端输出击穿；但此时只丢该行并继续，不再整轮失败。
- 回滚：保留当前 `0.3.1` 安装包与备份（`~/.astrbot/data/plugin-backup-20261030-165521/`），出现回归时可整目录回滚。

## 九、版本与发布建议

- 本修复属于缺陷修复，建议版本 `0.3.1 → 0.3.2`。
- 是否立即生成 ZIP、覆盖安装目录、重启生产实例，需用户单独确认；未确认前只做代码与单测。

## 十、实施记录（Apply）

批准方案：方案 B + 可观测性增强；范围限定「只改代码 + 单测」。

- `constants.py`：`MAX_AGENT_OUTPUT_LINE_BYTES` 改为 `8 * 1024 * 1024`，新增 `STDOUT_READ_CHUNK_BYTES = 65_536`。
- `agents/process.py`：新增 `iter_stdout_lines()`（分块读取、按换行切分、超限整行丢弃并告警、EOF 尾行处理）；`ProcessRunner.run()` 改用它，超时仍为每次读块 1800 秒。
- `main.py`：消息处理失败的日志改为记录「异常类型：异常消息」并带 `exc_info=True`。
- `tests/test_process_stream.py`：新增 5 个用例（正常行、CRLF、超长行丢弃、超长行跨块、EOF 尾行、读超时透传）。
- 验证结果：AstrBot Python 3.12.13 全量单测 **164/164 通过**；真实子进程复现 1,050,000 字节单行 + `result` 行，未再抛 `ValueError`，后续事件正常产出。
- 发布：版本升为 `0.3.2`；ZIP `integrations/astrbot/astrbot_plugin_cc_qq-v0.3.2-upload.zip`；生产与测试安装目录已覆盖（备份 `plugin-backup-20261101-005050`）；两实例重启后日志均为「已加载 v0.3.2」。
- 待做：真机复测「读取大图」场景，确认不再出现 `ValueError`。

## 十一、本轮不做 / 后续阶段（Deferred Scope）

- **不改变**代理输出协议（继续使用 `--verbose --output-format stream-json`）。
- **不引入**流式输出（沿用既有延期项）。
- 超长行内容不做持久化或回放；仅记录丢弃日志。后续若发现被丢弃的是关键文本，再单独对齐「截断保留头部」策略。
