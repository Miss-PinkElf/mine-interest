# Handoff：B站主路径已通，音频音量待修

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 18:28:48 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 上下文过长新开对话；记录验收进展与下次优先 bug |
| 关联 mission | bilibili-fanqie-mobile-plugin |
| handoff 编号 | 2026-08-07-003 |
| 是否 superseded 上一份 | 是（002 不再作为最新恢复入口） |
| 当前状态（Status） | 交接用（Handoff） |
| 文档边界 | 不表示 mission Close；不替代 state/bug-log |
| 开发分支 | `rin-bilibili-fanqie-mobile/dev` |

---

## 当前目标

个人用 Android App：B站可配置导出 + 番茄 TXT（自配端点）。

## 当前阶段

| 项 | 状态 |
|----|------|
| Align/Plan/Propose/Apply | 完成 |
| B站下载 | **用户确认成功** |
| 切换保存目录 | **用户确认实现** |
| 音频音量 | **偏小（BUG-001）— 下次修** |
| 番茄 Official-API/搜书名/零配置 | **延期**（结构化单条） |
| 完整 Close | 禁止，待音量等收口 |

## 本轮对话完成摘要

- [x] 恢复 mission；Propose + 全 Task Apply 源码  
- [x] 番茄 `changdunovel.com/t/` 短链识别与解跳  
- [x] B站 403 缓解（WBI、CDN Referer、多候选）  
- [x] APK 打包与多次 push dist  
- [x] 模拟器配置说明（无需过度调参）  
- [x] 澄清 Tomato Official-API ≠ 番茄开放平台 API；延期落盘  
- [x] 用户验收：B站能下、目录可切换  
- [ ] 音量偏小修复  
- [ ] mission 完整 Close  

## 关键决策

| ID | 内容 |
|----|------|
| D016 | 先 Propose 再 Apply |
| D018 | 番茄 Official-API/搜书名/零配置单独延期；主线先 B站 |
| （验收） | B站主路径用户确认通过 |

## 关键路径

| 路径 | 作用 |
|------|------|
| `android/` | 产品代码 |
| `dist/MineMedia-debug.apk` | 安装包（远端分支 dist/） |
| `bug-log.md` | **BUG-001 音量** |
| `deferred/番茄-Official-API与搜书名零配置正文.md` | 番茄增强延期 |
| `deferred/mvp-与延期范围总表.md` | MVP/延期索引 |

## 风险 / 开放

- 音量问题根因未实锤（源增益 vs 导出链路）  
- 番茄正文仍依赖用户端点  
- B站接口仍可能再漂移（yt-dlp 仍延期）  

## 立即下一步

1. 读 `state.md` + `checkpoints.md` + **本 handoff** + `bug-log.md`  
2. **优先修 BUG-001**（B站导出音量偏小）  
3. 勿启动 Official-API 延期包  
4. 修完可再打 APK / 按用户要求 push  

## 恢复指引

热路径：state → checkpoints → handoff 003 → bug-log  
范围：deferred 总表  

## 可移出活跃上下文

- Align 长讨论、Tomato 闭源细节全文、模拟器 Add Device 逐步说明  
