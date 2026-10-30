# 环境探测（Environment Probe）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:45:00 CST。
- 更新时间（Updated At）：2026-10-30 14:45:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：说明 `scripts/probe_env.py` 的探测项、输出字段、判定规则与跨平台差异。
- 关联仓库或项目（Related Repository / Project）：`person-config` 与本仓库 `tools/astrbot_e2e/`。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：实施中（In Progress）。
- 文档边界（Scope / Boundary）：参考说明，非真相源；不触发实现。

## 用途与用法

```bash
python3 scripts/probe_env.py --config <config.local.json> --output environment.json
```

- `--config` 可选；提供时会把配置摘要与端口写入结果。
- `--output` 可选；不提供时只打印到 stdout。
- 退出码：`0` 表示探测流程完成（不代表环境可用）；未捕获异常返回 `1`。

## macOS 路径

| 对象 | 路径 |
| --- | --- |
| QQ 应用 | `/Applications/QQ.app` |
| QQ 沙盒容器 | `~/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ` |
| NapCat 安装目录 | `~/Library/Containers/com.tencent.qq/Data/Documents/napcat` |
| AstrBot 生产数据根 | `~/.astrbot` |
| AstrBot 生产插件目录 | `~/.astrbot/data/plugins` |
| AstrBot 测试数据根（配置项） | `~/.astrbot-e2e`（默认） |

## 探测项与输出字段

| 探测项 | JSON 字段 | 说明 |
| --- | --- | --- |
| 操作系统 | `platform.system/release/machine/is_macos` | `is_macos=false` 时停止并说明仅验证 macOS |
| Python | `python.version/executable` | 当前运行探测脚本的解释器 |
| AstrBot | `astrbot.command/available/version/data_root/data_root_exists` | 通过 `astrbot --version` 读取版本；找不到时仍返回结果 |
| NapCat | `napcat.install_dir/available/version/workdirs` | 版本来自 `package.json`；`workdirs` 扫描 `NapCat`、`NapCat-e2e` |
| QQ 进程 | `qq.app/app_exists/running` | 用 `ps -axo command=` 判断 QQ 是否在运行 |
| 生产插件 | `plugins.production_dir/available` | 只列出目录名，不读取插件源码 |
| 端口 | `ports.<name>.port/open` | 见下表 |
| 配置摘要 | `config.path/error/test_root/bot_qq/sender_qq/group_id/webui_port/reverse_ws_port` | `config.error` 非空表示配置读取失败 |

## 默认端口

| 名称 | 端口 | 用途 |
| --- | --- | --- |
| `production_webui` | `6185` | 生产 AstrBot WebUI |
| `production_onebot` | `6199` | 生产 AstrBot 反向 OneBot WS |
| `production_napcat` | `6099` | 生产 NapCat WebUI |
| `test_webui` | `6186` | 测试 AstrBot WebUI（可由配置覆盖） |
| `test_onebot` | `6198` | 测试 AstrBot 反向 OneBot WS（可由配置覆盖） |
| `test_sender_napcat` | `6098` | 测试发送者 NapCat WebUI |
| `test_bot_onebot` | `6200` | 测试机器人 OneBot WS |
| `test_sender_onebot` | `6201` | 测试发送者 OneBot WS |

## 判定规则

1. `platform.is_macos=false`：停止，说明本 skill 只在 macOS 验证过。
2. `astrbot.available=false`：停止，给出安装或将 `astrbot` 加入 PATH 的修复建议。
3. `napcat.available=false`：停止，检查 NapCat 是否安装在 QQ 容器目录。
4. `config.error` 非空：停止，先修复 JSON 格式、编码或路径。
5. 测试端口已被占用：区分「测试实例已运行」与「未知进程占用」；未知进程只报告，不终止。
6. 生产端口 `6185/6199` 出现在测试探测结果中：视为配置冲突，停止并交给用户确认。

## Linux / Windows 差异

- Linux：AstrBot 数据根通常为 `~/.astrbot`；NapCat 多由 systemd 或 Docker 管理；进程检查用 `ps`/`systemctl`，端口检查用 `ss`。
- Windows：路径与进程检查不通用；QQ/NapCat 通常不在 macOS 沙盒容器中；需替换 `_paths()` 与 `qq_info()` 的实现。
- 未适配平台不要直接套用 macOS 端口与路径，先跑等价探测并人工确认。

## 注意

- `probe_env.py` 只读：不启动、不停止任何服务，不修改配置。
- 端口探测是短超时连接，可能受本机防火墙影响；`open=false` 不等于服务一定不可用。
