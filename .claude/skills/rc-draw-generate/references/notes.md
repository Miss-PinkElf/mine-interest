# Right Code 画图接口速查

> 来源：<https://github.com/1198722360/rcdoc/tree/main/src/docs/rc_draw>
> 下载日期：2026-10-23，本地副本见 `.devflow/rc-draw-skill/references/`。

## 基础信息

| 项 | 值 |
| --- | --- |
| 基础地址（Base URL） | `https://rightapi.ai` |
| 鉴权头（Authorization） | `Authorization: Bearer sk-xxxxx` |
| 请求格式 | `application/json`；OpenAI 图片编辑也支持 `multipart/form-data` |
| 结果形态 | 图片 URL，不返回 base64 |

## 异步任务（Async Task）

1. 提交请求，请求体带 `"async": true`
2. 立即返回 `task_id`
3. 轮询 `GET /v1/tasks/{task_id}`
4. 完成判据：出现 `data`（OpenAI）或 `candidates`（Gemini）
5. `failed` / `expired` / `canceled` 按失败处理

> 不带 `async: true` 时最多等 60 秒，超时仍返回 `task_id`。本 skill 始终异步提交。

## 模型别名（平台展示名）

| 别名 | 实际模型 / 协议 |
| --- | --- |
| `nano-banana` | Gemini（`gemini-2.5-flash-image`） |
| `nano-banana-2` | Gemini（`gemini-3.1-flash-image-preview`） |
| `nano-banana-2-lite` | Gemini（`gemini-3.1-flash-image-lite`） |
| `nano-banana-pro` | Gemini（`gemini-3-pro-image-preview`） |
| `gpt-image-2-vip` | OpenAI |
| `gpt-image-2.5` | OpenAI |

`nano-banana*` 必须走 Gemini `generateContent` 端点，不能按 OpenAI 协议发送。
别名可由 `.env` 档案的 `RC_PROFILE_<SLUG>_ALIASES` 覆盖。

## 两套协议

| 对比项 | OpenAI 生成 | Gemini 生成 |
| --- | --- | --- |
| 模型 | `gpt-image-2`、`gpt-image-2.5-flare`、`gpt-image-2.5-sunburst` | `gemini-3-pro-image-preview`、`gemini-nano-banana-2.1` |
| 模型位置 | 请求体 `model` | 路径 `/v1beta/models/{model}:generateContent` |
| 文生图 | `POST /v1/images/generations` | 同一 `generateContent` 接口 |
| 图片编辑 | `POST /v1/images/edits` | 同一接口，`parts` 里加 `inline_data` |
| 尺寸 | `size` 像素值，如 `1024x1024` | `generationConfig.imageConfig.aspectRatio` + `imageSize`（`1K` / `2K` / `4K`） |
| 质量 | `quality`：`auto` / `low` / `medium` / `high`；2.5 模型另有 `xhigh` / `max` | 通过 `imageSize` 档位控制 |
| 多图参考 | 原生支持，`image` 数组 | 原生支持，多个 `inline_data` part |
| 结果位置 | `data[].url` | `candidates[].content.parts[].text`（文本即 URL） |

## OpenAI 请求要点

### 文生图

```json
{
  "model": "gpt-image-2.5-flare",
  "prompt": "...",
  "n": 1,
  "size": "1024x1024",
  "quality": "auto",
  "output_format": "png",
  "async": true
}
```

### 图片编辑（JSON 传图，多图原生）

```json
{
  "model": "gpt-image-2.5-sunburst",
  "prompt": "把第一张图的商品放进第二张图的场景里",
  "image": [
    "data:image/png;base64,....",
    "data:image/png;base64,...."
  ],
  "async": true
}
```

也可以用公网 URL 作为 `image` 元素。文档说明 `image` 与 `images` 等价。

### 尺寸约束（OpenAI）

- 最大边长 ≤ 3840
- 宽、高均为 16 的倍数
- 长边 : 短边 ≤ 3:1
- 总像素 655,360 – 8,294,400
- 超过 `2560x1440` 属实验性大图，耗时与失败率更高

## Gemini 请求要点

```json
{
  "async": true,
  "contents": [
    {
      "role": "user",
      "parts": [
        { "text": "把第二张图的帽子戴到第一张图的人物头上" },
        { "inline_data": { "mime_type": "image/png", "data": "{BASE64}" } },
        { "inline_data": { "mime_type": "image/png", "data": "{BASE64}" } }
      ]
    }
  ],
  "generationConfig": {
    "imageConfig": { "aspectRatio": "3:4", "imageSize": "1K" }
  }
}
```

- `inline_data.data` 是纯 base64，不带 `data:image/...;base64,` 前缀
- `imageSize` 的 `K` 必须大写
- 不支持 `:streamGenerateContent`

## 任务查询响应

处理中：

```json
{ "task_id": "task_xxx", "status": "in_progress", "progress": 45 }
```

完成（OpenAI）：无 `status`，返回 `{"data":[{"url":"..."}]}`
完成（Gemini）：无 `status`，返回 `{"candidates":[...]}`

失败：

```json
{ "status": "failed", "error": { "message": "上游生成失败" } }
```

## 已知限制

- `mask`（局部重绘）参数会被接收但**不生效**，需在提示词里描述修改区域
- `variations`（图片变体）不支持
- `response_format` 不生效，结果固定为 URL
- 参考图过大时建议先压缩再上传
- 多图参考按传入顺序指代：提示词写「第一张图」「第二张图」

## 常见 HTTP 错误

| 状态码 | 原因 | 处理 |
| --- | --- | --- |
| 400 | JSON / 表单错误，或 `size` / `aspectRatio` 取值不支持 | 用最小请求验证后逐个加参数 |
| 401 | Key 缺失、无效或过期 | 检查 `RC_API_KEY` |
| 403 | Key 被禁用，或分组未开通该模型 | 检查 Key 分组 |
| 404 | 模型名或路径错误 | 核对模型名 |
| 429 | 限流或余额不足 | 降并发、查余额 |
| 5xx | 上游临时不可用 | 稍后重试 |
