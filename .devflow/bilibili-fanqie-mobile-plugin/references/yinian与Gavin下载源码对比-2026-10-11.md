# yinian 与 Gavin 下载源码对比

## Metadata（元数据）

- 创建时间（Created At）：2026-10-11 11:36:38 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：核验新增两个仓库的公开下载实现、正文依赖及命令行工具（CLI）复用价值。
- 关联仓库或项目（Related Repository / Project）：mine-interest-bilibili。
- 关联任务（Related Mission）：`.devflow/bilibili-fanqie-mobile-plugin/`。
- 原始需求（Raw Requirement）：`zzz-prompt-debug/下载番茄b站/prompt-1.md`；本轮用户提供两新增 GitHub 链接。
- 当前状态（Status）：候选项（Candidate），源码调查完成，运行未验证。
- 文档边界（Scope / Boundary）：源码事实与候选判断，不代表已批准计划（Plan），不触发实施（Apply）。

## 核验范围

两仓库均已通过本机代理克隆到本任务 `references/`：

| 仓库 | 本地目录 | 核验提交 / 日期 |
| --- | --- | --- |
| [yinian0406/Fanqie-novel-Downloader](https://github.com/yinian0406/Fanqie-novel-Downloader) | `yinian0406-Fanqie-novel-Downloader/` | `98c59b4e6a42274cb2a329bbdfae4912661dd665` / 2025-04-06 |
| [Gavin-2023-tech/Fanqie-Tomato-Downloader](https://github.com/Gavin-2023-tech/Fanqie-Tomato-Downloader) | `Fanqie-Tomato-Downloader/` | `dd5606097c15350163b8252c437df10406308e00` / 2025-03-22 |

GitHub 标记 yinian 仓库为 Gavin 仓库的分支（Fork）。两者当前都公开 Python 下载源码，无需到历史版本找核心。

## yinian：请求模块独立，正文仍来自第三方

源码：[request_handler.py](https://github.com/yinian0406/Fanqie-novel-Downloader/blob/98c59b4e6a42274cb2a329bbdfae4912661dd665/request_handler.py)。

- `get_book_info:79`：官网书页提取书名、作者与简介。
- `extract_chapters:109`：请求 `api5-normal-lf.fqnovel.com/reading/bookapi/search/{book_id}/v`，然后用 BeautifulSoup 查找 HTML 节点 `div.chapter-item`。请求的是接口路径，但解析按 HTML 目录处理，存在响应契约不匹配的疑点，未实测。
- `down_text:143`：请求 `https://api.cengui.cn/api/tomato/content.php?item_id=<章节编号>`，期待业务码 `200` 和 `data.content`，再清理 HTML、重复标题和段落空行。
- `gui.py:240` 的 `download_novel`：先下载前五章，再并发下载其余章节；缓存章节结果，最终按 `index` 顺序写入 TXT。

复用价值：网络请求与界面已有初步分离，可研究请求适配器（Request Adapter）及“并发获取、顺序导出”的模式。当前没有独立批量 CLI；主下载编排仍在图形界面（GUI）中。

需要修正的具体问题：`down_text` 只在抛出异常时增加重试计数，正常 JSON 的业务码不是 `200` 时会继续循环，可能无限请求。正常成功响应正文为空时则会跳出循环并报失败。README 宣称断点续传，但本次查到的下载集合和正文缓存都在内存，任务启动时清空；未找到持久恢复链路，不能据文档认定断点恢复已实现。

许可：独立 LICENSE 文件为 MIT，版权注明 POf-L；实际复用需保留其许可与版权信息。

## Gavin：有可调用核心与交互入口

源码：[2.py](https://github.com/Gavin-2023-tech/Fanqie-Tomato-Downloader/blob/dd5606097c15350163b8252c437df10406308e00/2.py)。

- `Run:203`：接受书籍编号和保存路径，从官网书页取章节目录，用线程池下载章节。
- `down_text:88`：请求 `http://rehaofan.jingluo.love/content?item_id=<章节编号>`，期待业务码 `0` 和 `data.content`，然后清理文本。
- `interpreter:79`：定义静态字符还原函数，但源码搜索只找到定义，没有调用；当前下载链路依赖第三方服务返回正文，不能把该函数视作运行中的独立解密能力。
- `main:348`：通过 `input()` 交互输入，属于交互式命令行入口，尚无标准参数解析（Argument Parsing）与结构化输出（JSON）。
- `.github/workflows/download-novel.yml:68`：使用 `importlib` 导入 `2.py`，设置线程数和输出格式，再调用 `Run`；证明核心有明确的程序调用入口。

复用价值：可研究“CLI 解析参数后调用 Run”的入口方式，以及 TXT/分章文本/EPUB 导出组织。现有实现不能直接当成熟下载内核使用。

具体问题：业务码不是 `0` 且无异常时，重试计数不增加，可能无限循环；多个工作线程在 `download_chapter:169` 直接向同一个 TXT 追加，未见顺序汇总或写锁，存在章节乱序与写入竞争；未找到持久断点恢复。`Run` 还为每章重复调用 `get_headers`，进而生成 Cookie，增加请求成本。

许可：没有独立 LICENSE 文件，README 的许可证部分仍是占位文本。正式复制源码前需确认授权。

## 对当前目标的判断

这两个项目进一步证明：公开下载流程可以参考，但正文获取仍是外部接口依赖。它们没有补齐“独立实现平台鉴权和正文解密”的缺口，且正文服务当前可用性未验证。

候选优先级：研究轻量请求模块与顺序导出可看 yinian；研究已有 CLI 与批量编排仍优先看 POf-L 历史版；研究完整恢复和分组机制可看 Tomato Rust 版。不要将 README 宣称的能力直接认定为已实现且可运行。

## 本轮不做 / 后续阶段

本轮没有执行第三方程序、访问正文服务或修改业务代码。接口可用性、小章节内容校验、新 CLI、恢复与顺序写入修复后续继续：先确认正文服务依赖是否可接受，再进入对齐（Align）和计划（Plan）。若必须独立获取正文，则继续研究直接协议或网页适配，不视为放弃此目标。
