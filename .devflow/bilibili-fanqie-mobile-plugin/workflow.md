# B站 + 番茄小说 手机插件 Workflow（工作流）

## Metadata（元数据）

- 更新时间（Updated At）：2026-08-07 17:45:25 CST
- 关联 mission：bilibili-fanqie-mobile-plugin
- 当前状态（Status）：Apply 完成源码，待 Verify
- 文档边界：当前流程快照。

## 路径

- 重型路径；分支 `rin-bilibili-fanqie-mobile/dev`

## 主线

```text
Align -> Plan -> Propose -> Apply(源码) -> Verify(待) -> Close(待用户)
```

## 当前阶段

| 阶段 | 状态 |
|------|------|
| Align / Plan / Propose | 完成 |
| Apply | 源码完成（12 Task） |
| Verify | 阻塞：SDK Platform |
| Close | 未开始 |

## 里程碑

1. 对齐与延期边界 — 完成  
2. Plan + spec 三件套 — 完成  
3. android 多模块实现 — 完成（未编译验证）  
4. 真机 APK 验收 — 未开始  
5. 完整 Close — 未开始  

## 下一步

装 Platform → gradle 测试与 APK → 真机 → 用户允许后 Close
