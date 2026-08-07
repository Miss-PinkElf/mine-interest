# B站 + 番茄小说 手机插件 Workflow（工作流）

## Metadata（元数据）

- 更新时间（Updated At）：2026-08-07 18:28:48 CST
- 关联 mission：bilibili-fanqie-mobile-plugin
- 当前状态（Status）：Verify 部分通过；bug 修复迭代
- 文档边界：当前流程快照。

## 路径

- 重型；分支 `rin-bilibili-fanqie-mobile/dev`

## 主线

```text
Align → Plan → Propose → Apply → Verify(B站主路径通过) → 修 BUG-001 → …
```

## 当前阶段

| 阶段 | 状态 |
|------|------|
| Apply | 完成 |
| Verify B站下载/目录 | **用户确认通过** |
| Verify 音质/音量 | **未通过**（音量小） |
| 番茄完整体验 | 延期（自配端点 MVP） |
| Close | 未开始 |

## 下一步

1. 新会话修音频音量  
2. 不启动 Official-API 延期包  
