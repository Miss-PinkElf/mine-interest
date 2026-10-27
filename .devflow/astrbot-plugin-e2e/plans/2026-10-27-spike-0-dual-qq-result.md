# Spike 0：同机双开 QQ 与 NapCat 验证结果

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 18:22:00 CST。
- 更新时间（Updated At）：2026-10-27 18:22:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录同机双开 QQ、双 NapCat、双向 OneBot 收发的验证结论、关键坑与证据。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 关联对齐稿（Related Align）：`2026-10-27-astrbot-plugin-e2e-align.md`。
- 关联计划（Related Plan）：`2026-10-27-astrbot-plugin-e2e-plan.md`。
- 当前状态（Status）：已完成（Completed），结论为通过（Passed）。
- 文档边界（Scope / Boundary）：Spike 0 结果真相源；不代表 Runner 或测试 AstrBot 已实现。

## 结论

**通过（PASS）**。在同一台 macOS 上可以同时运行两个 QQ 实例，并各自加载 NapCat：

- 两个 QQ 号同时在线；
- 两个 NapCat 使用独立工作目录与独立 WebUI 端口；
- 两个 OneBot WebSocket 通道可同时工作；
- 测试群内双向文本收发成功；
- 生产 AstrBot `6199` 全程保持连接，未被测试实例踢下线。

## 实例与账号

| 角色 | QQ 号 | 启动方式 | NapCat 工作目录 | WebUI | OneBot 通道 |
| --- | --- | --- | --- | --- | --- |
| 测试机器人（Bot） | 3254276668（17号） | 生产窗口，默认 QQ 容器 | `.../QQ/NapCat` | `6099` | 观察/发送 WS `6200`；到测试 AstrBot `6198` 的反向客户端（待测试 AstrBot 启动） |
| 测试发送者（Sender） | 1961618848（C#） | 测试窗口，`--user-data-dir=~/.qq-e2e` | `.../QQ/NapCat-e2e` | `6098` | 发送 WS `6201` |

- 专用测试群：`701292201`。
- 生产 AstrBot：`6185 / 6199`，生产 bot `3254276668` 仍连接 `6199`。
- 测试 AstrBot：尚未实现；`6198` 反向连接会持续重试，这是预期行为。

## 端口与通道

| 端口 | 用途 | 结果 |
| --- | --- | --- |
| `6099` | 生产/测试机器人 NapCat WebUI | 监听 |
| `6098` | 测试发送者 NapCat WebUI | 监听 |
| `6200` | 机器人 NapCat 观察/发送 WS 服务端 | 监听 |
| `6201` | 发送者 NapCat 发送 WS 服务端 | 监听 |
| `6199` | 生产 AstrBot OneBot 反向 WS | 保持连接 |
| `6198` | 测试 AstrBot OneBot 反向 WS | 尚未启动，机器人客户端重试中 |

## 关键坑与处理

1. **`write EIO` / `EPERM mkdir`**
   - 根因：QQ 在 macOS 上运行于 App Sandbox，`--no-sandbox` 只关闭 Chromium 沙箱，不关闭 macOS App Sandbox。
   - 把 `NAPCAT_WORKDIR` 放到 `~/.qq-e2e/NapCat` 会被拒绝写入。
   - 解决：改到容器内路径 `~/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ/NapCat-e2e`。

2. **两个窗口容易登录成同一个号**
   - 现象：两个窗口都登录 `1961618848（C#）`，或账号与配置写错位，导致 `6200/6201` 不监听。
   - 解决：明确窗口职责：
     - 生产窗口 → `3254276668（17号）`（测试机器人）
     - 测试窗口 → `1961618848（C#）`（测试发送者）

3. **NapCat native 模块警告**
   - `NativePacketClient / Napi2NativeLoader / FFmpegAddonAdapter` 加载失败，`PacketBackend` 报不支持当前 QQ 版本架构。
   - 结果：文本消息双向收发仍然成功；这些警告不阻断本轮文本链路。
   - 保留为风险：图片、文件、语音等富媒体能力可能受影响。

4. **生产 bot 配置改动**
   - 已在修改前备份：
     - `.../QQ/NapCat/config/onebot11_3254276668.json.bak-20261027-181413`
     - `.../QQ/NapCat-e2e/config/onebot11_1961618848.json.bak-20261027-181413`
   - 生产 bot 新增 `6200` 观察/发送服务与 `6198` 反向客户端；生产 `6199` 原有客户端保留。
   - 测试发送者新增 `6201` 发送服务。

5. **启动脚本本地化**
   - `~/.qq-e2e/start-production.sh` / `start-production-background.sh`：生产窗口。
   - `~/.qq-e2e/start-test.sh` / `start-test-background.sh`：测试窗口。
   - 脚本不入库；仓库只记录方法与约束。

## 验证证据

`get_login_info`：

```text
sender: {'user_id': 1961618848, 'nickname': 'C#'}
bot:    {'user_id': 3254276668, 'nickname': '17号'}
```

发送者 → 测试群 → 机器人：

```text
sender send: ok 0 {'message_id': 1635363506}
bot received sender message: True
text = e2e-sender-ping-1793096624
```

机器人 → 测试群 → 发送者：

```text
bot send: ok 0 {'message_id': 209377654}
sender received bot message: True
text = e2e-bot-ping-1793096625
```

综合结果：`RESULT: PASS`。

## 残留风险

- NapCat native addon / FFmpeg / PacketBackend 警告仍存在，文本链路可用，但富媒体链路未验证。
- 两个 QQ 实例仍共享同一个 macOS 容器 `com.tencent.qq`，只隔离了 NapCat 工作目录与端口；长时间运行、多账号并发和 QQ 自身数据一致性仍需观察。
- 测试 AstrBot `6198` 尚未启动；机器人实例会持续重试该连接。
- 生产 bot 的 NapCat 配置已改动；回滚时使用上述备份文件并重启生产 QQ。

## 下一步

进入 Task 1：创建 `tools/astrbot_e2e/` Runner 骨架与配置加载，按 Plan Task 1 的测试先行步骤实现。
