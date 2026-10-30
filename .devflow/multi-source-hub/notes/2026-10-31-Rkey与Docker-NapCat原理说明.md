# 为什么 Docker 里的 NapCat 能拿到 Rkey，而 macOS 原生不行

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 01:43:00 +08:00
- 更新时间（Updated At）：2026-10-31 01:43:00 +08:00
- 作者（Author）：rin（Claude 协助）
- 目的（Purpose）：完整记录 QQ 图片下载失败的前因后果、运行环境、根因链、Docker 方案及其原理，供后续排障与交接使用。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）
- 关联 mission（Related Mission）：`.devflow/multi-source-hub/`
- 关联文档（Related Documents）：
  - `handoffs/2026-10-30-021-Docker-NapCat迁移与rkey修复.md`
  - `state.md`
  - `decision-log.md`
  - `qq-message-pipeline.md`
- 当前状态（Status）：原理说明（Explainer），已完成
- 文档边界（Scope / Boundary）：解释性文档，不是计划（Plan），不代表任何未批准的实施项；不包含 token、rkey 或完整鉴权 URL。

---

## 一、结论摘要

**Docker 并没有“修复 rkey”这个功能；它修复的是 NapCat 获取 rkey 的运行环境。**

- macOS 原生 NapCat 的 **Packet 后端（packetBackend）** 加载失败，导致它拿不到 QQ 原生签发的 rkey。
- 拿不到原生 rkey 后，NapCat 会尝试两个第三方远程 rkey 服务；这两个服务在当时都不可用。
- 两条路都失败后，NapCat 使用代码里写死的**占位 rkey（placeholder rkey）** 拼接图片 URL；腾讯 CDN 校验失败，返回 HTTP 400 `download url has expired`。
- 改用 Docker 后，容器是 Linux 用户态，没有 macOS 的硬运行时（Hardened Runtime）与库校验（Library Validation）限制，NapCat 的 Linux 原生模块 `napi2native.linux.arm64.node` 能正常加载，Packet 后端初始化成功，QQ 原生 rkey 通道恢复，图片 URL 变成带真实签名的 `multimedia.nt.qq.com.cn`，下载返回 HTTP 200。

一句话：**不是 Docker 有特殊能力，而是 Linux 容器里 NapCat 的 native Packet 通道能工作，rkey 就不再走占位符。**

---

## 二、问题现象

### 2.1 用户可见现象

- 群里合并转发 3 张图片，sourcehub 检查插件生成的 `content.md` 里有 3 个图片 URL，但 `envelope.json` 的 `gaps` 是：
  ```json
  ["media_failed", "media_failed", "media_failed"]
  ```
- `attachments` 为空，说明图片没有落盘。
- NapCat 控制台出现：
  ```text
  [error] 17号 | [Rkey] 所有服务均已禁用, 图片使用FallBack机制
  ```

### 2.2 图片 URL 的特征

失败时的 URL 形如：

```text
https://gchat.qpic.cn/download?appid=1407&fileid=<fileid>&rkey=<占位rkey>&spec=0
```

三个不同 `fileid` 的图片使用了**完全相同的 rkey**。真实 rkey 是按图片/账号/类型签发的短期令牌，不可能三张图完全相同。这说明 URL 里的 rkey 是常量占位符，不是腾讯签发的值。

### 2.3 服务端返回

直接请求失败 URL（绕过代理）返回：

```json
{"retcode":-5503007,"retmsg":"download url has expired","retryflag":0}
```

HTTP 状态码 `400`。这里的 “expired” 是腾讯对无效/未签发 URL 的统一错误，并不表示“等一会儿就好”。

---

## 三、运行环境

### 3.1 macOS 原生阶段

| 项 | 值 |
|---|---|
| 操作系统 | macOS（Darwin 25.2.0，Apple Silicon arm64） |
| QQ | `6.9.89-45758`（安装目录 `/Applications/QQ.app`） |
| NapCat | `4.18.42`，注入 `/Applications/QQ.app` |
| NapCat 配置 | `~/Library/Containers/com.tencent.qq/Data/Documents/napcat/` |
| AstrBot | `4.29.3` |
| sourcehub 检查插件 | `astrbot_plugin_sourcehub_inspector 0.6.5` |
| cc-qq 插件 | `astrbot_plugin_cc_qq 0.3.1` |
| 关键配置 | `packetBackend: "auto"`，`fileLog: false`，`consoleLogLevel: "info"` |

对照安装包：

| QQ 版本 | `com.apple.security.cs.disable-library-validation` |
|---|---|
| `6.9.89-45758`（当前安装版） | **没有** |
| `7.0.2-53644`（本机 DMG，曾启动过） | **有** |

> `7.0.2` 在本机因启动问题未作为最终方案；它的 entitlement 差异是验证 macOS 根因的关键对照。

### 3.2 Docker 阶段

| 项 | 值 |
|---|---|
| 容器运行时 | OrbStack（Docker 28.5.2） |
| 镜像 | `mlikiowa/napcat-docker:latest`（linux/arm64，镜像构建于 2026-03-08） |
| 镜像内 NapCat | `4.17.46` |
| 镜像内 Linux QQ | `3.2.25-45758` |
| 容器名 | `napcat` |
| 登录账号 | 17号 `3254276668` |
| 端口 | `127.0.0.1:13000->3000`、`13001->3001`、`16099->6099` |
| 反向 WS | NapCat → AstrBot `Test-01`（`host.docker.internal:6199`） |
| 数据卷 | `~/napcat/ntqq`（QQ 登录态）、`~/napcat/config`（NapCat 配置） |
| 自启策略 | `restart: unless-stopped` |

---

## 四、关键概念

### 4.1 rkey 是什么

- rkey 是腾讯 CDN 对 QQ 媒体资源（图片、视频、文件）的**短期鉴权令牌**。
- 它通常按账号类型区分（私聊 / 群聊），有有效期（本次实测 `ttl=3420` 秒，约 57 分钟）。
- 同一个 rkey 不应在不同图片之间复用；每张图应有独立签名。
- 图片 URL 里带 rkey，因此 **URL 本身就是凭据**，不能提交 Git、不能贴到公开聊天、日志也要避免完整输出。

### 4.2 NapCat 获取 rkey 的三条路

NapCat 内部按优先级尝试：

1. **原生通道（native Packet）**
   - 通过 `Napi2Native` / `MoeHoo` 原生模块 hook QQ 的网络收发，调用 QQ 自带的 `FetchRkey`。
   - 需要 `packetBackend` 可用，且原生模块与 QQ 版本/架构匹配。
2. **远程 rkey 服务**
   - NapCat 打包时写死了两个第三方地址（一个 HTTP、一个 HTTPS）。
   - 每个 URL 失败 4 次后会被禁用一天；全部禁用时打印 `所有服务均已禁用`。
3. **硬编码占位 rkey**
   - 前两条都失败时，NapCat 使用打包产物里的常量占位 rkey。
   - 这个值不是腾讯签发的，只用于“让 URL 结构完整”，腾讯会拒绝。

### 4.3 两条 URL 分支

NapCat 生成图片 URL 时根据 `online_rkey` 走不同分支：

- `online_rkey = true`（原生 rkey 成功）：
  ```text
  https://multimedia.nt.qq.com.cn/download?appid=...&fileid=...&rkey=<真实rkey>
  ```
- `online_rkey = false`（回退占位 rkey）：
  ```text
  https://gchat.qpic.cn/download?appid=...&fileid=...&rkey=<占位rkey>&spec=0
  ```

因此，**看 URL 的域名和是否带 `spec=0`，就能判断 rkey 走的是真实通道还是回退通道。**

---

## 五、根因链（前因后果）

```text
macOS QQ 6.9.89-45758
  │  硬运行时（Hardened Runtime）开启
  │  entitlements 缺少 com.apple.security.cs.disable-library-validation
  ▼
NapCat 4.18.42 的 arm64 原生模块（napi2native，ad-hoc 签名）
  │  macOS 库校验（Library Validation）拒绝加载
  ▼
Napi2NativeLoader 未加载
  ▼
packetBackend 不可用 / NativePacketClient 不可用
  ▼
原生 rkey 通道被跳过
  │
  ├─ 远程 rkey 服务①：返回残缺 JSON（缺少 group_rkey/private_rkey）
  ├─ 远程 rkey 服务②：TLS unrecognized name，握手失败
  ▼
两条远程服务均被禁用（每个失败 4 次后禁用一天）
  ▼
getRkey() 抛错，NapCat 使用硬编码占位 rkey
  ▼
online_rkey = false
  ▼
生成 gchat.qpic.cn/download?...&rkey=<占位>&spec=0
  ▼
腾讯 CDN 校验失败：HTTP 400，retcode -5503007
  ▼
sourcehub 下载失败，记录 media_failed ×3
```

### 5.1 为什么原生 rkey 通道在 macOS 上不可用

直接证据是调用 NapCat 的 `get_rkey` 动作返回：

```text
packetBackend不可用，请参照文档 ... 检查 packetBackend 状态或进行配置！
错误堆栈信息：Error: [Core] [Packet] NativePacketClient 不可用，NapCat.Packet将不会加载！
```

这说明失败发生在 NapCat **本地模块加载阶段**，不是网络、不是腾讯接口、也不是代理。

关键差异：

- QQ `6.9.89-45758` 的 entitlements **没有** `com.apple.security.cs.disable-library-validation`；
- NapCat 的 `napi2native.darwin.arm64.node` 是 **ad-hoc 签名**（没有 Tencent Team ID）；
- macOS 硬运行时开启时，库校验只允许 Apple 或同一 Team ID 签名的库；ad-hoc 模块会被拒绝。

> 当时的 NapCat 配置是 `fileLog: false`，没有抓到 `dlopen` 的原始错误行；但 `packetBackend不可用` 的返回、entitlements 对比、以及同类公开案例三者相互印证，根因链是完整的。

### 5.2 为什么远程 rkey 服务也救不了

实测两条远程服务当时都不可用：

- 一个只返回 `{"expired_time": ..., "name": "rkeys"}`，缺少 `group_rkey` / `private_rkey`；
- 另一个 TLS 报 `unrecognized name`，握手就失败。

它们不是“慢”，而是“返回结构不对/服务不可达”。所以即使把 NapCat 重启（清空内存里的失败计数），远程通道仍然拿不到 rkey。

### 5.3 为什么不是代理（Proxy）

这是当时最容易误判的方向，必须明确排除：

- `scutil --proxy` 显示 HTTP/HTTPS/SOCKS 全部关闭；
- 默认路由在 `en1`，没有 TUN 的 `utun` 默认路由；
- sourcehub 的下载器 `sourcehub/download.py` 使用 `ProxyHandler({})`，**显式绕过代理**；
- 直连（`--noproxy '*'`）请求失败 URL 仍然返回 400；
- 失败发生在 NapCat 本地模块加载阶段，与网络代理无关。

**结论：代理不是原因。** 后续再遇到类似“图片打不开”，先看 URL 域名和 rkey 是否为占位值，不要先怀疑 Clash。

---

## 六、为什么 Docker 容器里就正常

### 6.1 容器是 Linux 用户态

macOS 上的 Docker/OrbStack 会运行一个 Linux 虚拟机，容器共享这个 Linux 内核。容器内部是完整的 Linux 用户态：

- Linux QQ（`/opt/QQ`）
- NapCat（`/app/NapCat.Shell.zip` 解压到 `/app/napcat`）
- Xvfb、Node、ffmpeg、系统库

**macOS 的代码签名与库校验规则不适用于容器内的 Linux 进程。** NapCat 的 Linux 原生模块 `napi2native.linux.arm64.node` 可以正常 `dlopen`。

### 6.2 Packet 后端初始化成功

Docker 启动日志：

```text
[Napi2NativeLoader] 加载成功
[PacketHandler] 加载成功
[PacketHandler] 初始化成功
[NapCat] [Core] NapCat.Core Version: 4.17.46
```

`get_rkey` 返回真实签名：

```json
[
  {"type": "private", "rkey": "&rkey=<真实值>", "created_at": ..., "ttl": 3420},
  {"type": "group",   "rkey": "&rkey=<真实值>", "created_at": ..., "ttl": 3420}
]
```

此时 URL 变成：

```text
https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=<fileid>&rkey=<真实rkey>
```

实测下载：

```text
HTTP 200
size=89412
file type: JPEG image data
```

`online_rkey = true`，占位 rkey 分支不会被触发。

### 6.3 版本不是越新越好，平台配对更重要

镜像里的 NapCat 是 `4.17.46`，比 macOS 上的 `4.18.42` 旧，但它仍然能工作，因为：

- 镜像内 Linux QQ 是 `3.2.25-45758`，与镜像内 NapCat 的 Packet 映射是配套构建/验证的；
- Linux 没有 macOS 的库校验问题；
- Packet 通道能初始化，rkey 就能由 QQ 原生签发。

**结论：决定成败的是“NapCat 能不能在当前平台加载 native Packet 模块”，而不是版本号大小。**

### 6.4 镜像为什么“拉下来就能用”

镜像不是单一程序，而是一份完整的 Linux 文件系统快照，包含：

- Linux QQ 运行时；
- NapCat Shell 压缩包与启动脚本；
- Xvfb、Node、ffmpeg、系统库。

容器启动时 `entrypoint.sh` 会：

1. 按需解压 NapCat；
2. 生成默认配置；
3. 按 `NAPCAT_UID/GID` 调整权限；
4. 启动 Xvfb 虚拟屏幕；
5. 启动 `/opt/QQ/qq --no-sandbox`。

所以宿主机不需要安装 QQ/NapCat/Xvfb。唯一需要持久化的是：

- QQ 登录态卷（`/app/.config/QQ`）
- NapCat 配置卷（`/app/napcat/config`）

---

## 七、解决方案

### 7.1 最终拓扑

```text
macOS 宿主机
  ├─ AstrBot 生产实例（WebUI 6185 / 反向 WS 6199）
  ├─ AstrBot 测试实例（WebUI 6186 / 反向 WS 6198）
  ├─ sourcehub 检查插件、cc-qq 插件
  └─ OrbStack / Docker
       └─ 容器 napcat（Linux/arm64）
            ├─ Linux QQ 3.2.25-45758
            ├─ NapCat 4.17.46，登录 17号（3254276668）
            ├─ 反向 WS → host.docker.internal:6199（生产 AstrBot）
            └─ 端口：13000/13001/16099
```

- 17号 迁到 Docker；个人号 C#（1961618848）留在原生 QQ。
- 同一 QQ 账号不能同时在原生 QQ 与 Docker 上登录，否则腾讯会踢掉一个。

### 7.2 Docker 配置要点

- 端口避开本机其他服务（例如 multica 占用的 3000），所以用 `13000/13001/16099`。
- `restart: unless-stopped`：OrbStack 启动后容器自动恢复；手动 `docker compose down` 后不会自动拉起。
- 登录态在 `~/napcat/ntqq`，容器重启不需要重新扫码。
- WebUI 只绑定 `127.0.0.1`，不暴露到局域网。

### 7.3 切换账号后必须重启 AstrBot

Docker 接管 17号 后，原生 17号 的反向 WebSocket 连接可能没有干净地从 AstrBot 的 API 客户端表里移除。aiocqhttp 以 `X-Self-ID` 为键管理反向 API 客户端；同 `self_id` 的旧连接清理可能把新连接的同名条目删掉，导致插件主动调用 `get_forward_msg` 失败，而消息接收仍然正常。

**处理：切换同 `self_id` 的 NapCat 后重启 AstrBot，并等待最多 30 秒让 NapCat 重连。** 本次实测重启后转发 3 图立即恢复正常。

---

## 八、验证步骤

### 8.1 检查 Packet 后端

```bash
docker logs napcat 2>&1 | grep -E "Napi2NativeLoader|PacketHandler|NapCat.Core"
```

期望看到：

```text
[Napi2NativeLoader] 加载成功
[PacketHandler] 初始化成功
```

### 8.2 检查 rkey

通过本地探针 WebSocket 调用 `get_rkey`，期望返回 `private` 与 `group` 两条，且 `ttl > 0`。

### 8.3 检查图片 URL

对转发消息调用 `get_forward_msg`，观察图片 URL：

- 正常：`https://multimedia.nt.qq.com.cn/...`，不带 `spec=0`；
- 异常：`https://gchat.qpic.cn/...&spec=0`，说明仍在回退占位 rkey。

### 8.4 检查下载

直接请求图片 URL（直连即可，不要走代理）：

```bash
curl -sS --noproxy '*' -o /tmp/probe.jpg -w "HTTP %{http_code} size=%{size_download}\n" "<图片URL>"
file /tmp/probe.jpg
```

期望 `HTTP 200` 且 `file` 识别为 JPEG/PNG。

### 8.5 检查 sourcehub 条目

新转发条目应满足：

```text
gaps = []
attachments = 3
content.md 内嵌 3 个媒体链接
```

---

## 九、常见误区与排障

### 9.1 “是不是代理问题？”

不是。见第 5.3 节。先看：

- URL 域名是 `gchat.qpic.cn` 还是 `multimedia.nt.qq.com.cn`；
- rkey 是否三张图完全相同；
- `get_rkey` 是否返回 `packetBackend不可用`。

### 9.2 “重启 QQ 就好了？”

重启只能清空远程 rkey 服务的失败计数；如果 native Packet 仍不可用、远程服务仍不可用，重启后依然会回退占位 rkey。**能力缺失不是重启能修的。**

### 9.3 “升级到最新 NapCat 就好了？”

不一定。macOS 的问题在签名/库校验与 QQ 版本匹配；Docker 镜像里的 NapCat 更旧但能用，说明平台配对比版本号更重要。

### 9.4 “Docker 能多开吗？”

能，但**一个容器一个 QQ 账号**。多开 = 多个容器，各自独立：

- `container_name`
- 宿主端口
- QQ 数据卷（`/app/.config/QQ`）
- NapCat 配置卷

同一个 QQ 账号不能同时在线于两个容器或原生 QQ。

---

## 十、边界与后续

- **macOS 原生路径未继续修复**：QQ `7.0.2` 在本机启动失败；重签 QQ 副本（加 `disable-library-validation`）是可行但维护成本高的备选。当前不采用。
- **远程 rkey 服务不可依赖**：本次两条服务均失效；不要把“等第三方服务恢复”当方案。
- **Docker 镜像版本较旧**：`mlikiowa/napcat-docker:latest` 本地镜像为 2026-03 构建，NapCat `4.17.46`；后续可升级镜像并重新验证 Packet/rkey。
- **插件健壮性**：`fetch_forward_messages` 目前会静默吞掉转发获取异常；建议增加短重试并写入 `forward_unexpanded` gap。该改动待写 Plan、待批准，未实施。
- **E2E 双容器脚本**：`tools/napcat_e2e/` 的 compose 与启动脚本尚未落盘，待用户确认账号/端口后按 devflow 推进。

---

## 十一、操作手册（速查）

```bash
# 启动
cd ~/napcat
docker compose up -d

# 状态
docker ps
docker logs -f napcat

# 停止
cd ~/napcat
docker compose down

# 重启（登录态保留，通常不需要重新扫码）
docker restart napcat
```

- WebUI：`http://127.0.0.1:16099`（token 在 `~/napcat/config/webui.json`）
- 二维码：容器内 `/app/napcat/cache/qrcode.png`
- 切账号 / 切 NapCat 后：重启 AstrBot，等 30 秒让 NapCat 重连

---

## 十二、术语表

| 术语 | 含义 |
|---|---|
| rkey | 腾讯 CDN 媒体资源的短期鉴权令牌 |
| 占位 rkey（placeholder rkey） | NapCat 打包产物里的硬编码常量，不是腾讯签发 |
| Packet 后端（packetBackend） | NapCat 通过原生模块 hook QQ 网络收发的通道 |
| Napi2Native | NapCat 的原生桥接模块，按平台/架构提供 `.node` 文件 |
| 库校验（Library Validation） | macOS 硬运行时对加载动态库的签名校验 |
| 硬运行时（Hardened Runtime） | macOS 的应用加固机制 |
| 反向 WebSocket（reverse WebSocket） | NapCat 主动连接 AstrBot 的 WS 连接 |
| OneBot | QQ 机器人协议标准；NapCat 是其实现之一 |

---

## 十三、参考

- NapCat Releases（版本与 QQ 兼容性）：`https://github.com/NapNeko/NapCatQQ/releases`
- NapCat macOS 原生支持与 entitlement 说明：见 NapCat `v4.18.35`–`v4.18.37` 发布说明
- 同类公开排查案例（HTTP 400 / 占位 rkey）：`https://damodev.csdn.net/6ae2ef37e5f4ca4eff8d1c19.html`
- 本地交接：`handoffs/2026-10-30-021-Docker-NapCat迁移与rkey修复.md`
- 当前状态：`state.md`

---

## 十四、安全边界

- 本文档不记录任何 token、真实 rkey、完整鉴权 URL 或真实聊天内容。
- `~/.astrbot/data/sourcehub/`、`~/.astrbot/data/sourcehub-inspector/` 含真实消息与媒体，禁止提交或外传。
- 图片 URL 含 rkey，属于短期凭据；排障时只保留域名/结构，不要完整粘贴。
