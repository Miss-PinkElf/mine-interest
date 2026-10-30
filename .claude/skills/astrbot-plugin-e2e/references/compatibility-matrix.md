# 兼容性矩阵（Compatibility Matrix）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:45:00 CST。
- 更新时间（Updated At）：2026-10-30 14:45:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录已验证的 AstrBot / NapCat 组合、依赖接口与未知组合的处理方式。
- 关联仓库或项目（Related Repository / Project）：`person-config` 与本仓库 `tools/astrbot_e2e/`。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：实施中（In Progress）。
- 文档边界（Scope / Boundary）：参考说明，非真相源；不触发实现。

## AstrBot 4.x

| 能力 | 依赖点 | 说明 |
| --- | --- | --- |
| 初始化 | `astrbot init -y` | 在 `test_root` 下生成 `.astrbot` 与数据目录 |
| WebUI 密码 | `astrbot password --username <name>` | 通过 stdin 输入两次密码 |
| 主配置 | `<test_root>/data/cmd_config.json` | 写入 `dashboard`、`platform`、`plugin_set` 等 |
| Dashboard | `dashboard.enable/host/port` | 测试实例默认 `127.0.0.1:6186` |
| 平台适配 | `platform[]`，`type=aiocqhttp`，`ws_reverse_host/port/token` | 对应测试实例反向 OneBot WS `6198` |
| 日志 | `<test_root>/data/logs/astrbot.log` | 断言日志与采集证据的默认路径 |
| 登录接口 | `POST /api/v1/auth/login` | JSON `{username, password}`；成功返回 `status=ok` 与 `data.token` |
| 重载接口 | `POST /api/v1/plugins/reload` | 带 `Authorization: Bearer <token>`；Body `{plugin_id}`；`status` 为 `ok` 或 `success` |

注意事项：

- 本地 WebUI 使用 `127.0.0.1` 时，Cookie 需要 `CookieJar(unsafe=True)`，否则 Secure Cookie 不回传。
- 重载失败时由执行引擎重启测试实例兜底；不要直接修改生产实例。

## NapCat 4.x

| 能力 | 依赖点 | 说明 |
| --- | --- | --- |
| 安装目录 | `~/Library/Containers/com.tencent.qq/Data/Documents/napcat` | 版本读取 `package.json` |
| 工作目录 | `NAPCAT_WORKDIR` | macOS 双开时用于隔离两个实例的数据 |
| 配置文件 | `<QQ 容器>/NapCat/config/onebot11_<qq>.json` | 含 `network.websocketClients` |
| WebUI 端口 | 生产 `6099`、测试发送者 `6098` | 以本机实际配置为准 |
| 反向 OneBot WS | 生产 AstrBot `6199`；测试 AstrBot `6198` | 测试客户端名常见为 `AstrBot-E2E` |
| OneBot 正向 WS | 机器人 `6200`、发送者 `6201` | 执行引擎通过这些地址收发消息 |

注意事项：

- NapCat 只在启动时读取网络配置；修改配置后必须重启 QQ/NapCat。
- macOS 下两个 QQ 共用一个沙盒容器，只隔离 `NAPCAT_WORKDIR` 与端口。
- NapCat 可能输出 native addon、FFmpeg、PacketBackend 警告；文本链路通常不受影响。

## 已验证组合

| AstrBot | NapCat | 平台 | 状态 |
| --- | --- | --- | --- |
| `4.29.3` | `4.18.28` | macOS（Darwin `25.2.0`），Python `3.9.6` | 已验证双 QQ 文本链路 |

## 未知组合

1. 先运行 `scripts/probe_env.py`，确认路径、版本与端口。
2. 再运行 `doctor`，确认两个 QQ 账号匹配、插件源可用、测试端口归属正确。
3. 不要假设 WebUI 登录/重载接口、日志路径、配置文件结构完全一致。
4. 接口不一致时停止并记录差异，不要在生产实例上试探。
