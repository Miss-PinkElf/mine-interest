# Docker NapCat 迁移与 Rkey 修复交接（2026-10-30）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 18:45:00 +08:00
- 更新时间（Updated At）：2026-10-30 18:45:00 +08:00
- 作者（Author）：rin（Claude 协助）
- 目的（Purpose）：记录 QQ 接入从 macOS 原生 NapCat 迁移到 Docker NapCat 的原因、变更、验证结果与运维策略，供后续会话与故障复盘使用。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）
- 关联 mission（Related Mission）：`.devflow/multi-source-hub/`
- 关联文档（Related Documents）：`state.md`、`decision-log.md`、`qq-message-pipeline.md`
- 当前状态（Status）：已完成（Completed）；转发 3 图端到端验证通过
- 文档边界（Scope / Boundary）：本轮环境变更与验证记录；不代替 `state.md`；不包含任何 token、rkey 或完整鉴权 URL。

## 结论

- **Mac 原生失败在「下载」**：macOS QQ `6.9.89-45758` 的签名 entitlements 缺少 `com.apple.security.cs.disable-library-validation`，NapCat `4.18.42` 的 arm64 `napi2native` 为 ad-hoc 签名，无法在硬运行时（Hardened Runtime）的库校验（Library Validation）下加载 → `packetBackend` 不可用 → 原生 rkey 失败 → 两个远程 rkey 服务也失效 → 回退硬编码占位 rkey → 腾讯返回 400 `download url has expired`。
- **Docker 失败在「转发展开」**：Docker NapCat 的 Packet/rkey 正常；失败是 AstrBot 侧保留了切换前原生 17号 的同 `self_id` 反向 WebSocket（reverse WebSocket）API 客户端，插件调 `get_forward_msg` 时拿不到可用客户端，异常被静默吞掉。
- **最终处置**：QQ 接入改用 `~/napcat` 的 Docker NapCat（Linux/arm64，NapCat `4.17.46`，登录 17号 `3254276668`）；切换账号后重启 AstrBot，转发 3 图完整落盘。

## 时间线（2026-10-30）

| 时间 | 事件 |
|---|---|
| 15:15 | 下载 macOS QQ `7.0.2-53644` 安装包 |
| 15:26 | 实际以 7.0.2 启动成功（该版本带 `disable-library-validation`） |
| 15:38–15:43 | 回退到 `6.9.89-45758`（该版本不带该 entitlement） |
| 17:47 | 群 `836229427` 的 3 图合并转发失败，`content.md` 三条 `media_failed` |
| 18:18 | Docker NapCat 启动，`Napi2NativeLoader`/`PacketHandler` 加载成功 |
| 18:19 | 扫码登录 17号；AstrBot `Test-01` 连接 Docker |
| 18:23 / 18:27 | 两次转发均「条目生成但未展开」，插件告警「转发消息获取失败」 |
| 18:33 | 用户重启 AstrBot；Docker NapCat 30 秒后自动重连 |
| 18:34 | 第三次转发成功：`attachments=3`、`gaps=[]` |

## 根因与证据

### 阶段一：原生 Mac 下载失败

- 三条图片 URL 使用**同一个** rkey，且与 `napcat.mjs` 内硬编码占位常量一致；真实 rkey 每张图不同。
- 直连（绕过代理）请求返回 `HTTP 400`，响应体 `{"retcode":-5503007,"retmsg":"download url has expired"}`。
- 调用 NapCat `get_rkey` 动作返回：`packetBackend不可用 ... NativePacketClient 不可用`。
- 两个远程 rkey 服务均不可用：一个只返回 `expired_time`/`name`，另一个 TLS `unrecognized name`。
- 系统代理（Proxy）关闭、无 TUN 默认路由；sourcehub 下载器本身使用 `ProxyHandler({})` 显式绕过代理 → **排除代理因素**。
- 只读挂载安装包对比：QQ `7.0.2-53644` 带 `disable-library-validation`，`6.9.89-45758` 不带。

### 阶段二：Docker 转发展开失败

- Docker 内 `[Napi2NativeLoader] 加载成功`、`[PacketHandler] 初始化成功`；`get_rkey` 返回 private/group 真实签名（ttl 3420 秒）。
- 直接用同一 NapCat 调 `get_forward_msg`：约 304ms 返回 3 张图，URL 域名为 `multimedia.nt.qq.com.cn`，实测下载 `HTTP 200`、89,412 字节、有效 JPEG。
- 插件日志明确：`转发消息获取失败：渊下宫分宫(836229427) forward_id=...`。
- 原因：原生 17号 与 Docker 17号 的 `self_id` 相同；aiocqhttp 反向 API 客户端以 `X-Self-ID` 为键，旧连接清理会删掉同名的新连接条目，插件调用 `get_forward_msg` 抛异常并被 `except Exception: continue` 吞掉。
- 用户重启 AstrBot 后只保留 Docker 一条连接，同一转发立即可展开。

## 环境变更

### Docker 容器

- 目录：`~/napcat`
- 镜像：`mlikiowa/napcat-docker:latest`（linux/arm64，NapCat `4.17.46`）
- 容器名：`napcat`
- 账号：17号 `3254276668`

### 端口映射（避免与本机 multica 的 3000 冲突）

| 主机 | 容器 | 用途 |
|---|---|---|
| `127.0.0.1:13000` | `3000` | NapCat HTTP 预留 |
| `127.0.0.1:13001` | `3001` | 本地探针 WebSocket（token 不入文档） |
| `127.0.0.1:16099` | `6099` | NapCat WebUI |

### 自启与持久化

- `restart: unless-stopped`：OrbStack 启动后容器自动恢复。
- 登录态持久化：`~/napcat/ntqq`。
- 配置持久化：`~/napcat/config`；本轮新增：
  - `napcat_3254276668.json`
  - `onebot11_3254276668.json`（反向 WS 指向 `ws://host.docker.internal:6199/ws`，token 与 AstrBot `Test-01` 现有配置一致）
- 备份：`~/napcat/compose.yaml.bak-20261030-181758`

### AstrBot

- 适配器 `Test-01`：`ws://0.0.0.0:6199`，先启 AstrBot 或后启均可；NapCat 每 30 秒重连。
- 个人号 C# `1961618848` 仍留在原生 QQ，不迁 Docker。
- **切换同 `self_id` 的 NapCat 实例后必须重启 AstrBot**，否则旧反向 API 客户端残留会导致插件主动调用失败。

## 验证结果

- 新条目：`qq:forward:1747617391`
- `gaps = []`
- `attachments = 3`
- `content.md` 内嵌 3 个媒体链接
- 三个媒体文件均为有效 JPEG（约 87K / 199K / 196K）
- 转发展开 JSON 已生成于 `~/.astrbot/data/sourcehub-inspector/forwards/`

## 运维手册

1. 启动顺序：先启动 AstrBot（或 Docker），NapCat 每 30 秒重连；也可 `docker restart napcat` 立即重连。
2. 查看状态：`docker ps`、`docker logs -f napcat`。
3. 登录：WebUI `http://127.0.0.1:16099`；二维码同时保存到容器 `/app/napcat/cache/qrcode.png`。
4. 切换账号：确保同一 QQ 账号不在原生 QQ 与 Docker 双端同时在线；切换同 `self_id` 后重启 AstrBot。
5. 排障优先级：先看插件日志「转发消息获取失败」，再直接对该 NapCat 调 `get_forward_msg`；若直接调用成功，优先检查 AstrBot 反向 WS 连接是否残留/重复。
6. 未决清理：探针端口 `13001` 可关闭；`~/napcat/qrcode.png` 可删除。

## 回滚

- 停止 Docker：`cd ~/napcat && docker compose down`
- 恢复编排：`cp compose.yaml.bak-20261030-181758 compose.yaml`
- 原生 Mac 侧当前仍因 QQ `6.9.89` 缺 entitlement 而无法获取真实 rkey；回滚到原生意味着转图片继续失败，仅在 Docker 完全不可用时考虑。

## 后续 / 延期

- **插件转发展开健壮性（待写 Plan，未批准）**：`fetch_forward_messages` 增加短重试（建议 3 次、间隔 1 秒），最终失败写入 `forward_unexpanded` gap，避免静默吞异常。详见 `state.md` 的「本轮不做 / 后续阶段」。
- 前两次失败条目 `转发-1130815284`、`转发-726518115` 为半成品，可删除或重新转发覆盖。
- Docker 镜像内 NapCat 为 `4.17.46`（2026-03 构建），当前可用；后续可按需升级镜像并重新验证。
- 旧的原生 NapCat 配置与测试实例保留，不影响 Docker 生产路径。

## 安全边界

- 本文档不记录任何 token、rkey、完整鉴权 URL 或真实聊天内容。
- `~/.astrbot/data/sourcehub/` 与 `~/.astrbot/data/sourcehub-inspector/` 含真实消息与媒体，禁止提交或外传。
