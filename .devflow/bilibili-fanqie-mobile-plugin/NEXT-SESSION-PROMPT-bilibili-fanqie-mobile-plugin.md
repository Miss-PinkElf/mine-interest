# 下一次对话提示词（Next Session Prompt）

## Metadata（元数据）

- 更新时间（Updated At）：2026-10-11 12:03:00 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：直接复制下方内容，恢复番茄下载探索并对齐首版。
- 关联仓库或项目（Related Repository / Project）：mine-interest-bilibili。
- 关联任务（Related Mission）：`.devflow/bilibili-fanqie-mobile-plugin/`。
- 原始需求：`zzz-prompt-debug/下载番茄b站/prompt-1.md`。
- 当前状态（Status）：可用于续接；技术路线仍待讨论。
- 文档边界（Scope / Boundary）：恢复提示词，不是批准计划，不触发直接实现。

## 可直接复制

继续 `.devflow/bilibili-fanqie-mobile-plugin/` 的番茄小说下载探索。

请先读 `state.md` 和 `checkpoints.md`，再读 `handoffs/2026-10-11-004-fanqie-explore-handoff.md`。需要完整调查内容时，读 `番茄小说下载探索与本次对话总结-2026-10-11.md`，以及 `development-overview.md`；不用一开始加载全部参考源码。

我希望理解并复用番茄小说下载全过程，放到自己的软件里或做成命令行工具（CLI），不是只获得一个第三方接口地址。最终目标包含批量下载。

上轮已克隆 11 个参考项目、写 4 份调研和独立详细总结。关键纠正：POf-L 当前核心私有，但公开历史 `5a8f8752b46379db24fb85b4baa3713ddab90aeb` 有 Python 下载器及批量 CLI；Tomato 当前下载编排公开，缺口是官方模式外部取文依赖或第三方正文服务。yinian / Gavin 的正文来自第三方，不能当作它们自行实现底层取文。网页直接请求与字体还原有公开方法，但未验证全文范围和还原正确性。

POf-L 作者公开回复提供了书架端点；具体登录凭据提取保存尚未知。上轮没有实际登录、运行 CLI、验证第三方、完成全本或批量验收；只有示例官网页面结构请求成功。不要重复把 HTTP 200 当作全文成功。

请先和我讨论这三项：

1. 第一版是否必须客户端独立取正文，还是允许第三方服务？
2. 是否必须整本全文，还是可以接受官网开放章节？
3. 先做独立 CLI，还是直接扩展当前 Kotlin Android App？

然后确认语言、输入书单 / 批量范围、TXT 或 EPUB、持久恢复、缺章报告，以及登录书架 / 搜索是否第一版做。未讨论的内容不能当作我已经同意延期。候选顺序可以是正文样章 → 单本 → 小书单；这还不是批准方案。

首版议题与后续触发条件见 `deferred/番茄下载探索待讨论与后续阶段-2026-10-11.md`。原 D018 的 Official-API / 搜索 / 内置地址池等仍有延期记录，重新调查不等于全部恢复实施，也不是永久放弃。原 B站 BUG-001 音量小仍未修，请保留，不默认转移本次讨论目标。

确认方向后，按开发流程（devflow）先对齐（Align）、再把强相关计划（Plan）落在本任务 `plans/`，随后规格（Specification）与实施（Apply）；不要跳过讨论和计划直接改业务代码。

本机 HTTP 代理为 `http://127.0.0.1:10808`，可命令级使用。参考克隆留在本地 `references/`，没有作为嵌套 Git 仓库提交；若新环境缺失，按总结版本表恢复。原 `Tomato-Novel-Downloader/` 源码副本未覆盖。仓库内路径用相对路径，Python 使用 `backend/.venv`。

上轮提交授权仅用于上轮收尾；新代码修改按当前指令处理。根 `devflow-handoff.md` 是只读指导。不要提交无关 `zzz-prompt-debug/mac-win键盘/`；默认不提交 `config.ts`、`.gitignore`、`tsconfig.json`。
