---
name: rc-draw-generate
description: |
  自包含画图 skill：使用 Right Code（rightapi.ai）异步任务接口生成或编辑图片，
  支持 OpenAI 协议（gpt-image-2 / gpt-image-2.5-flare / gpt-image-2.5-sunburst）
  与 Gemini 协议（gemini-3-pro-image-preview / gemini-nano-banana-2.1）。
  用户说「生成图片」「画一张」「出图」「文生图」「图生图」「改图」「参考图」
  「多图融合」「rightcode」「rc-draw」「nano banana」或给出画面意图 / 本地参考图时使用。
  支持多 key / 多平台档案（RC_PROFILE_*），--profile 选择，--fallback 可选提交阶段容灾。
  流程：检查 .env 与 Python、提交异步任务、轮询 task_id、下载图片 URL 到 gen-images/；
  支持重复 --image 原生多图参考（不做拼接）；失败不自动重提，避免重复扣费。
---

# Right Code 画图（rc-draw-generate）

本 skill **独立完整**，不依赖旧 skill `gpt-image-generate`，也不向上解析仓库根路径。

## 双路径（Claude / Codex）

| 场景 | 路径 |
| --- | --- |
| Claude Code（真相源） | `.claude/skills/rc-draw-generate/` |
| Codex | `.codex/skills/rc-draw-generate/` |

改完后需同步到另一侧（同步 `SKILL.md`、`run.sh`、`run.cmd`、`lib/`、`prompts/`、`references/`、`.env.example`；**不同步** `.env`、`gen-images/`）。

## 目录结构

```text
rc-draw-generate/
├── SKILL.md
├── run.sh                  # macOS / Linux 入口
├── run.cmd                 # Windows 入口
├── lib/
│   └── rc_draw.py          # 提交 / 轮询 / 下载（仅 Python 标准库）
├── .env.example
├── .env                    # 本地创建，勿提交
├── gen-images/             # 输出目录（自动创建）
├── prompts/
│   └── prompt-image.md     # 无提示词时的默认模板
└── references/
    └── notes.md            # 接口速查
```

## 何时使用

- 生成 / 画 / 出图 / 文生图
- 改图 / 参考图 / 图生图 / 多图融合
- 用户提到 Right Code、rightapi.ai、rc-draw、Nano Banana
- 用户给了视觉描述或本地参考图，需要本地图片文件

> 旧的 `gpt-image-generate`（wyzlab 平台）保持不动；本 skill 是 Right Code 的独立实现。

## 模型选择

| 模型 | 协议 | 适用场景 |
| --- | --- | --- |
| `gpt-image-2` | OpenAI | **默认**，基础模型，兼容性最稳，质量档位最高 `high` |
| `gpt-image-2.5-flare` | OpenAI | 日常出图、速度优先 |
| `gpt-image-2.5-sunburst` | OpenAI | 图片编辑、多图融合、细节与文字要求高 |
| `gemini-3-pro-image-preview` | Gemini | Nano Banana Pro，画质与理解优先 |
| `gemini-nano-banana-2.1` | Gemini | Nano Banana 2，速度优先 |

`xhigh` / `max` 质量档位**只能**用于两个 `gpt-image-2.5-*` 模型。

**模型别名**：`nano-banana`、`nano-banana-2`、`nano-banana-2-lite`、`nano-banana-pro` 都路由到 Gemini 协议；`gpt-image-2-vip`、`gpt-image-2.5` 按 OpenAI 协议。别名可由档案 `ALIASES` 覆盖。

## 多 key / 多平台（Profile）

### 配置

在 `.env` 里为每个 key 建一个档案：

```bash
RC_DEFAULT_PROFILE=IMAGE

# 默认档案：Image
RC_PROFILE_IMAGE_NAME=Image
RC_PROFILE_IMAGE_BASE_URL=https://rightapi.ai
RC_PROFILE_IMAGE_KEY=sk-...
RC_PROFILE_IMAGE_MODEL=gpt-image-2
RC_PROFILE_IMAGE_MODELS=gpt-image-2,gpt-image-2-vip,gpt-image-2.5

# 可选：高质量分组，需要时用 -p IMAGE_HIGH 显式选择
RC_PROFILE_IMAGE_HIGH_NAME=Image 高质量
RC_PROFILE_IMAGE_HIGH_BASE_URL=https://rightapi.ai
RC_PROFILE_IMAGE_HIGH_KEY=sk-...
RC_PROFILE_IMAGE_HIGH_MODEL=gpt-image-2
RC_PROFILE_IMAGE_HIGH_MODELS=gpt-image-2,gpt-image-2.5-flare,gemini-3-pro-image-preview
RC_PROFILE_IMAGE_HIGH_ALIASES=nano-banana-pro:gemini
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `RC_PROFILE_<SLUG>_NAME` | 否 | 展示名，可中文 |
| `_BASE_URL` | 否 | 缺省回退全局 `RC_BASE_URL` |
| `_KEY` | 否 | 缺省回退全局 `RC_API_KEY` |
| `_MODEL` | 否 | 该档案默认模型 |
| `_MODELS` | 否 | 可用模型列表；不在列表时**警告**，不阻断 |
| `_ALIASES` | 否 | `模型:openai\|gemini`，逗号分隔 |

`SLUG` 建议用大写字母、数字、下划线，例如 `IMAGE_HIGH`；大小写不敏感，脚本内部统一转大写。

### 选择与容灾

- 默认档案：`RC_DEFAULT_PROFILE`（本仓库配置为 `IMAGE`，即「Image」分组）；未设置时用 `.env` 中第一个档案
- 需要高质量分组时显式加 `-p IMAGE_HIGH`，不要依赖默认值
- `--profile <SLUG 或展示名>` 显式选择
- `--list-profiles` 查看所有档案（不显示 key）
- `--fallback`：仅在**提交阶段**按档案顺序切换
  - **会切换**：401 / 403 / 404 / 429、5xx、网络错误
  - **不会切换**：400、提交返回 `failed`、已拿到 `task_id`、轮询失败
  - **不切换模型**：所有候选档案使用同一模型与同一请求体，避免语义漂移

单 key 配置（只填 `RC_API_KEY`）仍然可用，脚本会自动生成一个 `DEFAULT` 档案。

## Preflight（必须按序）

### 1. Python 3

```bash
command -v python3 || command -v python
```

没有 Python 3：**停止**，提示安装（macOS 可用 `brew install python`）。

### 2. 同级 `.env`

```bash
# Claude
.claude/skills/rc-draw-generate/.env
# Codex
.codex/skills/rc-draw-generate/.env
```

若不存在，从 `.env.example` 复制：可以只填一个 `RC_API_KEY`，也可以配置多个 `RC_PROFILE_*` 档案。
**不要**把 key 写进 git、命令历史或长日志。

### 3. 可执行权限

```bash
chmod +x .claude/skills/rc-draw-generate/run.sh
# 或
chmod +x .codex/skills/rc-draw-generate/run.sh
```

## 提示词策略

1. 用户给出完整提示词 → 原样使用
2. 用户只给意图 → 按「主体 → 场景 → 风格 → 细节」扩写
3. 图中文字用引号括起来，并说明位置与字体风格
4. 编辑时**先说保留什么，再说改什么**
5. 多图参考按传入顺序指代：「第一张图的商品」「第二张图的场景」
6. 完全没说画什么 → 先问一句

## 执行

### 纯文生图

```bash
.claude/skills/rc-draw-generate/run.sh --no-open "一只戴太空头盔的橘猫，电影级光影"
# Codex：
.codex/skills/rc-draw-generate/run.sh --no-open "一只戴太空头盔的橘猫，电影级光影"
```

### 单图编辑

```bash
.claude/skills/rc-draw-generate/run.sh --no-open \
  -i "path/to/char.png" \
  "保持人物面部和姿势不变，只把背景换成夜晚的雪山"
```

### 多图参考（原生直传，不拼接）

```bash
.claude/skills/rc-draw-generate/run.sh --no-open \
  -i "path/to/product.png" \
  -i "path/to/scene.jpg" \
  -m gpt-image-2.5-sunburst \
  "把第一张图的商品放进第二张图的场景里，保持商品标签清晰锐利"
```

- 每个 `-i` 对应一张参考图，可重复任意张
- 脚本**不会**把多张图拼接；OpenAI 走 `image` 数组，Gemini 走多个 `inline_data`
- 公网图片可直接用 `--image-url https://...`（可重复）
- 文档明确 `mask` 局部重绘暂不生效，局部修改请写进提示词

### Gemini 协议

```bash
.claude/skills/rc-draw-generate/run.sh --no-open \
  -m gemini-3-pro-image-preview \
  --ratio 16:9 --image-size 2K \
  "未来城市雨夜，霓虹倒影，电影海报构图"
```

### 指定 key 档案 / 容灾

```bash
# 使用 IMAGE_HIGH 档案
.claude/skills/rc-draw-generate/run.sh --no-open -p IMAGE_HIGH "一只橘猫"

# 该档案提交失败时，依次尝试其他档案
.claude/skills/rc-draw-generate/run.sh --no-open -p IMAGE_HIGH --fallback "一只橘猫"

# 查看已配置档案（不显示 key）
.claude/skills/rc-draw-generate/run.sh --list-profiles
```

### 续查已有任务

```bash
.claude/skills/rc-draw-generate/run.sh --task-id task_0123456789abcdef
# 任务由某个档案提交时，续查要带上同一个档案：
.claude/skills/rc-draw-generate/run.sh -p IMAGE_HIGH --task-id task_0123456789abcdef
```

轮询超时或中断后，用返回的 `task_id` 续查，**不要重新提交**。

### 预览请求体

```bash
.claude/skills/rc-draw-generate/run.sh --dry-run -m gpt-image-2 "测试提示词"
```

## 异步任务生命周期

1. 提交 → 立即返回 `task_id`
2. 每 5 秒轮询 `GET /v1/tasks/{task_id}`，打印进度
3. 出现 `data`（OpenAI）或 `candidates`（Gemini）→ 完成
4. `failed` / `expired` / `canceled` → 立即失败
5. 整体等待上限默认 600 秒；超时保留 `task_id`

**防重复扣费**：提交失败、任务失败、轮询超时都**不会自动重提**。

## 常用选项

| 选项 | 说明 |
| --- | --- |
| `-p, --profile` | 选择配置档案 |
| `--fallback` | 提交阶段失败时切换其他档案；拿到 `task_id` 后不切换 |
| `--list-profiles` | 列出档案与可用模型，不显示 key |
| `-m, --model` | 模型名，默认 `gpt-image-2` |
| `-i, --image PATH` | 本地参考图，可重复；原生多图，不拼接 |
| `--image-url URL` | 公网参考图，可重复 |
| `--size` | OpenAI 像素尺寸，如 `1024x1024`；`auto` 交给模型 |
| `--ratio` | Gemini 宽高比；OpenAI 会映射到常用像素尺寸 |
| `--image-size` | Gemini 档位 `1K` / `2K` / `4K` |
| `-q, --quality` | OpenAI 质量：`auto` / `low` / `medium` / `high` / `xhigh` / `max` |
| `--no-quality` | 不发送 `quality` 字段 |
| `-n` | OpenAI 生成数量，默认 1 |
| `--format` | `png` / `jpeg` / `webp`（仅 OpenAI） |
| `--out-dir` | 输出目录，默认 skill 内 `gen-images/` |
| `--timeout` / `--poll-interval` | 轮询上限（默认 600s）/ 间隔（默认 5s） |
| `--task-id` | 跳过提交，续查已有任务 |
| `--no-download` | 只打印 URL，不下载 |
| `--open` / `--no-open` | 下载后打开 / 不打开（默认不打开） |
| `--dry-run` | 只打印请求体，不发送 |
| `--no-proxy` | 忽略 `HTTP(S)_PROXY` 直连 |
| `--base-url` | 覆盖基础地址 |

配置优先级：**CLI 参数 > 已导出环境变量 > 同级 `.env` > 脚本默认值**。

## 成功后必须汇报

解析输出中的 `---RESULT---` 块，用中文报告：

1. **耗时**（`elapsed_text`）
2. **图片大小**（`bytes` / `human_size`）
3. **图片路径**（`path_rel`）
4. **模式**（`mode`）、**协议**（`protocol`）、**模型**（`model`）
5. 若有：`task_id`、`url`

模板：

```markdown
已生成图片。

- 耗时：{elapsed_text}
- 大小：{human_size}（{bytes} bytes）
- 路径：`{path_rel}`
- 模式：{mode} · 协议：{protocol} · 模型：{model}
- 档案：{profile}（容灾切换：{fallback_used}）
- 任务：`{task_id}`

提示词摘要：{一句话}
```

多图输出时逐张列出 `path_rel_1`、`path_rel_2`……

## 失败处理

| 情况 | 处理 |
| --- | --- |
| 无 Python 3 | 停止并给安装说明 |
| 无 `RC_API_KEY` | 指向 skill 同级 `.env` |
| HTTP 401 / 403 | 检查该档案的 Key 是否有效、分组是否开通该模型；需要自动切换时加 `--fallback` |
| HTTP 400 | 参数不被支持；先用最小请求验证，再逐个加参数 |
| HTTP 429 | 限流或余额不足；降并发、查余额 |
| 任务 `failed` / `expired` / `canceled` | 摘录 `error.message`，**不自动重提** |
| 轮询超时 | 用返回的 `task_id` 加 `--task-id` 续查 |
| 下载失败 | 加 `--no-download` 先拿 URL，再手动下载 |
| 参考图过大 | 先压缩再上传；文档说明可明显加快生成 |
| 代理导致连接失败 | 加 `--no-proxy` 直连 |
| 局部重绘不生效 | `mask` 上游暂不支持，改为在提示词里描述区域 |

## 接口约束（务必记住）

- 结果是**图片 URL**，不是 base64；本 skill 会自动下载到本地
- OpenAI 尺寸：边长 ≤ 3840、16 的倍数、长短边比 ≤ 3:1、总像素 655,360–8,294,400
- `xhigh` / `max` 仅限 `gpt-image-2.5-flare` 与 `gpt-image-2.5-sunburst`
- Gemini `imageSize` 的 `K` 必须大写
- `mask`、`variations`、`:streamGenerateContent` 不支持
- 多图参考原生支持，按传入顺序用「第一张图 / 第二张图」指代
- 平台展示名与协议：`nano-banana*` → Gemini；`gpt-image-2-vip`、`gpt-image-2.5` 等 → OpenAI

接口详情见 `references/notes.md`。
