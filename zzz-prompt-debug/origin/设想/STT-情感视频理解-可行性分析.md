# 视频/音频 STT + 情感理解 — 技术可行性分析

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| **创建时间** | 2026-06-10 |
| **作者** | ElYSIA |
| **目的** | 调研"视频/音频 → 带情感的文本描述"全链路技术栈可行性，给出推荐方案和实施路线 |
| **关联仓库** | mine-interest |
| **关联 Mission** | 无（当前为预研阶段） |
| **当前状态** | 候选项（Candidate） |
| **文档边界** | 本文件为技术预研文档，不代表已批准的实施方案；不会直接触发编码 |
| **关联需求** | `zzz-docs/设想/prompt.md` |

---

## 一、需求回顾

### 1.1 核心目标

将视频或音频中的文字提取出来，**带有情感**地表述——不仅仅是 STT（Speech-to-Text，语音转文字），还要捕捉：

- 说话人的**情绪/语气**（开心、愤怒、悲伤、讽刺等）
- 面部**表情**
- 视频中的**梗/内涵/文化语境**（meme、时事、领域梗）
- 结合 LLM 多模态分析进行修正和丰富

输出一个能**很好地用文字描述这段视频**的结果。

### 1.2 初步设想流程

```
视频/音频 → 去噪/人声分离 → 分角色/分音色提取文字
         → 每 5s 截图 → LLM 多模态分析 + 表情识别 → 带情感的文字对话列表
```

---

## 二、技术栈全景调研

### 2.1 音频去噪/人声分离（Denoising & Vocal Separation）

**目标**：去掉 BGM、背景噪音，保留干净的干声（人声）。

| 方案 | SDR（人声） | 速度 | 显存需求 | 易用性 | 推荐度 |
|------|:-----------:|------|----------|--------|:------:|
| **audio-separator** (BS-Roformer) | **12.9** | 中 | 4-6 GB | 极易（CLI+Python API） | ⭐⭐⭐ |
| **Demucs v4** (Meta) | 10.8 | 快 | ~4 GB | 易 | ⭐⭐ |
| **UVR5** (Ultimate Vocal Remover) | 11+ | 慢 | 4-8 GB | 中（GUI） | ⭐⭐ |
| Spleeter (Deezer) | ~8.5 | 极快 | ~2 GB | 易 | ⭐ |

**结论：完全可行。**

推荐 **`audio-separator`** + BS-Roformer 模型（`model_bs_roformer_ep_317_sdr_12.9755.ckpt`），是目前人声分离质量最高的开源方案（SDR 12.9）。备选 **Demucs v4** 用于速度优先场景。

```python
# 示例代码
from audio_separator.separator import Separator
separator = Separator()
separator.load_model('model_bs_roformer_ep_317_sdr_12.9755.ckpt')
output = separator.separate('input.mp3')  # → vocals.wav + instrumental.wav
```

---

### 2.2 说话人分离（Speaker Diarization）

**目标**：区分不同说话人，"谁在什么时候说了什么"。

| 方案 | 架构 | 重叠语音 | 显存 | 成熟度 |
|------|------|:------:|------|:------:|
| **WhisperX + pyannote.audio 3.1** | 级联管道（VAD→嵌入→聚类） | 一般 | 4-6 GB | ⭐⭐⭐ 最成熟 |
| NVIDIA Sortformer (NeMo) | 端到端 Transformer | 优秀 | 16-48 GB | ⭐ 门槛高 |
| **scribe-forge-ai** | 完整离线管道，自动选后端 | 一般 | <8 GB | ⭐⭐ Windows 友好 |

**结论：完全可行。**

推荐 **WhisperX + pyannote.audio 3.1**，这是 2025 年的黄金组合：
- WhisperX：比原生 Whisper 快 2-4 倍，输出词级时间戳
- pyannote.audio 3.1：端到端神经网络说话人分离，2-3 人场景最优

注意事项：
- pyannote 模型需要 Hugging Face Token 并接受用户协议
- Python 3.12+ 有兼容问题（可用 Resemblyzer 替代或降级到 Python 3.11）

---

### 2.3 语音识别 + 语音情感识别（ASR + Speech Emotion Recognition）

**目标**：将语音转文字，同时识别说话时的情绪状态。

#### 2.3.1 为什么选 SenseVoice？

SenseVoice-Small 是 **2025 年唯一同时支持 ASR + 情感识别（SER）+ 音频事件检测（AED）的主流开源模型**。

| 能力 | SenseVoice-Small | OpenAI Whisper | Paraformer |
|------|:---:|:---:|:---:|
| 中文 ASR | ✅ | ✅ | ✅ |
| **情感识别（SER）** | **✅ 原生内置** | ❌ | ❌ |
| **音频事件检测** | **✅（BGM/掌声/笑声/哭声等）** | ❌ | ❌ |
| 多语言（50+ 语言） | ✅ | ✅ | 仅普通话 |
| 推理速度 | 10s 音频仅需 70ms | 较慢 | 快 |
| 逆文本正则化（ITN） | ✅ | ❌ | ✅ |
| 流式识别 | ❌ | ❌ | ✅ |

**结论：完全可行。SenseVoice-Small 是唯一需要的方案。**

```python
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

model = AutoModel(
    model="iic/SenseVoiceSmall",
    device="cuda",  # 或 "cpu"
)

res = model.generate(
    input="audio.wav",
    language="auto",  # 自动检测语言（中文/英文/日文等）
    use_itn=True,     # 逆文本正则化："一百二十三" → "123"
)

text = rich_transcription_postprocess(res[0]["text"])
# 输出示例: "大家好欢迎收听|<HAPPY>| 今天的节目非常精彩|<bgm>|"
# 情感标签: <HAPPY>, <SAD>, <ANGRY>, <SURPRISED>, <FEARFUL>, <DISGUSTED>, <NEUTRAL>
# 事件标签: <bgm>, <applause>, <laughter>, <crying>, <cough>, <sneeze>
```

**关键优势**：
- 情感标签 + 音频事件标签**直接嵌入**到转录文本中
- 对中英文均有良好表现，在未微调的多数据集上超过其他开源 SER 模型
- 无需额外的情感分析管道，一步到位

#### 2.3.2 备选/补充方案

如果 SenseVoice 的情感粒度不够，可补充：
- **emotion2vec+**（FunASR 生态）：专注情感分类，4 类情感，300M 参数
- **speechbrain**：更灵活的情感识别框架，支持自定义类别

---

### 2.4 面部表情识别（Facial Expression Recognition）

**目标**：从视频截图中识别说话人的面部表情，补充 LLM 的多模态分析。

| 方案 | 精度 | 速度 | 功能 |
|------|:---:|------|------|
| **DeepFace** | 表情 ~97% | 中 | 表情 + 年龄 + 性别 + 种族 |
| **FER** | ~66%（FER2013） | 快 | 8 类表情（MTCNN 检测） |
| **MediaPipe Face Mesh** | 检测 468 点 | 极快 | 面部网格（不含表情分类） |

**结论：完全可行。**

推荐 **DeepFace + MediaPipe 混合架构**（2025 年主流模式）：
- **MediaPipe**：快速人脸检测 + 468 点面部网格
- **DeepFace**：基于检测结果做表情分类（7 类：Happy/Sad/Angry/Surprise/Fear/Disgust/Neutral）

```python
# DeepFace 表情分析
from deepface import DeepFace
result = DeepFace.analyze("frame.jpg", actions=['emotion'])
print(result[0]['dominant_emotion'])  # happy / sad / angry / surprise / fear / disgust / neutral
print(result[0]['emotion'])           # {'happy': 0.85, 'sad': 0.02, ...}
```

**适用边界**：
- 人脸清晰可见时效果好（正面、光照充足）
- 人脸较小/侧脸/遮挡场景精度下降（此时更依赖 SenseVoice 的语音情感 + LLM 多模态推测）

---

### 2.5 多模态 LLM 分析（Multimodal LLM）

**目标**：对视频截图进行综合分析——场景、人物关系、文字、暗示、梗、文化语境等。

| 模型 | 综合能力 | 视频理解 | 成本 | 上下文窗口 |
|------|:---:|:---:|------|:---:|
| **GPT-4o** | 最强 | 最好（InfiniBench 47.1%） | $5-15/1M tokens | 128K |
| **Gemini 2.0/2.5 Flash** | 强 | 原生视频输入 | **$0.35/1M tokens（最便宜）** | **1M-2M tokens** |
| **Claude 3.7/Opus 4** | 强 | 帧采样 | 较高 | 200K |

**结论：完全可行，且是关键组件。**

推荐组合策略：
- **Gemini 2.0 Flash**：主力——长上下文 + 最便宜 + 原生视频理解，可一次处理较长片段
- **GPT-4o**：高精度补充——当 Gemini 分析质量不足时，用 GPT-4o 做二次分析
- **Claude**：备选——文档/图表理解优秀，但无法识别个体人物

**关键发现**：
- 截图分析（文档、场景、文字）已经非常成熟，可直接用于生产
- 长视频理解（>50 分钟）仍然只有 ~50% 准确率，建议分段处理
- 多模态 LLM **过度依赖预训练知识**（只看标题就能答对不少），所以截图分析时建议给出具体的分析指令

---

### 2.6 梗/文化语境识别（Meme/Cultural Context Detection）

**目标**：识别视频中的梗、meme、时事引用、领域行话。

| 方法 | 可行性 | 说明 |
|------|:---:|------|
| **LLM 内置知识** | ⭐⭐⭐ | GPT-4o/Gemini 本身了解大量流行梗（训练数据已包含） |
| **Google Cloud Vision API** | ⭐⭐ | 提取标签/Web Entity，部分理解图片含义 |
| **反向图片搜索** | ⭐⭐ | 用截图搜互联网，找到原始梗的来源和含义 |
| **感知哈希（pHash）匹配梗库** | ⭐ | 需要自建梗图库，维护成本高 |
| **评论区抓取** | ⭐⭐ | 从视频来源平台抓取评论，LLM 分析社区解读 |

**结论：部分可行，但非 100% 可靠。**

推荐策略：
1. **LLM 直接判断**：在 prompt 中要求 LLM 检测是否包含梗/meme/时事引用，LLM 自带的知识能覆盖大部分流行梗
2. **反向图片搜索**：对关键截图做反向搜索，找到网络上对该画面的讨论——但**没有官方 API**，需用 Selenium 爬取或用 Bing Image Search API（1000 次/月免费）
3. **评论区辅助**：如果可以获取原视频评论区，LLM 能从中提取社区对该视频的解读
4. **接受不完美**：文化梗的识别本质上没有 100% 方案，Syracuse 大学的研究也证实了这一点

**保底思路**：对特别抽象的或无法识别的画面，LLM 应标记为 `<UNCLEAR>` 或给出"可能包含未识别的文化引用"的说明，而非强行猜测。

---

## 三、整体架构设计

### 3.1 方案 A：Agent 架构（推荐）

基于 **LangGraph + LangChain** 构建一个流水线 Agent。

```
                          ┌─────────────────────────┐
                          │   输入：视频/音频文件      │
                          └──────────┬──────────────┘
                                     │
                          ┌──────────▼──────────────┐
                          │  Step 1: 音频分离         │
                          │  audio-separator         │
                          │  → 干声.wav + 背景.wav    │
                          └──────────┬──────────────┘
                                     │
                          ┌──────────▼──────────────┐
                          │  Step 2: 说话人分离       │
                          │  WhisperX + pyannote      │
                          │  → [{speaker, segment}]  │
                          └──────────┬──────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                                 │
          ┌─────────▼─────────┐          ┌────────────▼──────────┐
          │ Step 3a: STT+情感  │          │ Step 3b: 视频截图分析  │
          │ SenseVoice-Small  │          │ 每5s截图 → 帧列表     │
          │ → 带情感标签的文字  │          └────────────┬──────────┘
          └─────────┬─────────┘                       │
                    │                   ┌─────────────▼──────────┐
                    │                   │ Step 4: 多模态 LLM 分析 │
                    │                   │ GPT-4o / Gemini 2.0    │
                    │                   │ → 场景/表情/梗/文字描述  │
                    │                   └─────────────┬──────────┘
                    │                                 │
                    └────────────┬────────────────────┘
                                 │
                      ┌──────────▼──────────────┐
                      │ Step 5: 融合对齐          │
                      │ LLM 整合所有信息           │
                      │ 对齐时间轴 + 角色 + 情感   │
                      └──────────┬──────────────┘
                                 │
                      ┌──────────▼──────────────┐
                      │ Step 6: 输出              │
                      │ 带情感/表情/语境标注的     │
                      │ 富文本对话/描述列表        │
                      └──────────────────────────┘
```

#### Agent 架构优势
- **灵活性高**：每个 Step 是一个 LangGraph Node，可独立调试、替换、并行执行
- **条件路由**：根据内容自动决定是否需要额外的梗搜索或二次分析
- **状态管理**：LangGraph 内置状态图，天然支持长任务的状态恢复
- **可扩展**：后续可轻松加入新节点（如翻译、摘要、多视频对比）

#### 技术栈
```
核心框架:  LangGraph + LangChain
STT+情感:  SenseVoice-Small (FunASR)
去噪:      audio-separator (BS-Roformer)
说话人:    WhisperX + pyannote.audio 3.1
表情:      DeepFace + MediaPipe
多模态LLM: GPT-4o / Gemini 2.0 Flash
搜索增强:  Bing Image Search API / Tavily Search
视频处理:  OpenCV (ffmpeg 截图)
存储:      SQLite / Postgres（任选）
```

---

### 3.2 方案 B：n8n 工作流架构

n8n 支持通过自定义节点或 HTTP Webhook 调用 Python 脚本，适合流程固定、需要可视化编排的场景。

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌────────┐
│ Webhook │───►│ Python   │───►│ Python    │───►│ LLM      │───►│ Merge  │
│ Trigger │    │ 音频分离  │    │ STT+情感   │    │ 截图分析  │    │ Output │
└─────────┘    └──────────┘    └───────────┘    └──────────┘    └────────┘
```

#### n8n 方案适用场景
- 流程固定、不需要频繁调整
- 需要 Web 可视化界面操作
- 与外部服务（YouTube API、Telegram、Google Drive）有大量集成需求

#### n8n 方案局限
- 视频处理（OpenCV）和本地模型推理（SenseVoice、DeepFace）需要自定义 Python 节点或 Code Node
- 多步 Agent 的动态决策不如 LangGraph 灵活
- 调试和状态追踪在复杂分支场景下不如代码直观

---

### 3.3 方案对比与推荐

| 维度 | Agent 架构（A） | n8n 工作流（B） |
|------|:---:|:---:|
| 灵活性 | ⭐⭐⭐ | ⭐⭐ |
| 开发门槛 | 中（需要写 Python） | 中（需要配置节点） |
| 调试能力 | ⭐⭐⭐（代码调试） | ⭐⭐（节点日志） |
| 可视化 | ⭐ | ⭐⭐⭐ |
| 外部集成 | ⭐⭐（需自己写） | ⭐⭐⭐（大量内置连接器） |
| 长期维护 | ⭐⭐ | ⭐⭐⭐ |
| 适合阶段 | **研发/迭代阶段** | 稳定运行阶段 |

**推荐：先 Agent 架构（A）做研发验证，稳定后可导出为 n8n 工作流（B）做生产部署。**

两者的本质并不冲突——Agent 架构的核心逻辑可以封装成 FastAPI 服务，然后被 n8n 的 HTTP Webhook 节点调用。

---

## 四、实施路线（Roadmap）

### Phase 1：核心链路 MVP（预计 2-3 周）

**目标**：跑通"音频 → 带情感的文本"的最小闭环。

| 步骤 | 内容 | 验证标准 |
|------|------|----------|
| 1.1 | 搭建 Python 环境，安装 `funasr`、`audio-separator`、`whisperx` | `import` 无报错 |
| 1.2 | 接入 SenseVoice-Small，测试单段音频 ASR + 情感 | 输出带 `<HAPPY>` 等标签的文本 |
| 1.3 | 接入 audio-separator 人声分离 | 分离后干声可被 SenseVoice 正常识别 |
| 1.4 | 接入 WhisperX + pyannote 说话人分离 | 不同说话人被正确标记 |
| 1.5 | **整合管道**：音频 → 去噪 → 分角色 → STT+情感 → 文本输出 | 跑通端到端 |

**Phase 1 产出**：一个命令行脚本，输入音频文件，输出带角色和情感的文本对话列表。

---

### Phase 2：视觉+多模态增强（预计 2-3 周）

**目标**：加入视频截图、表情识别和 LLM 多模态分析。

| 步骤 | 内容 | 验证标准 |
|------|------|----------|
| 2.1 | 用 OpenCV/ffmpeg 每 5s 从视频中截图 | 截图文件生成，时间戳正确 |
| 2.2 | 接入 DeepFace 对每帧做表情识别 | 输出每帧的主导情绪 |
| 2.3 | 接入 GPT-4o / Gemini 对关键帧做多模态分析 | 输出场景描述、人物关系、可能的文化引用 |
| 2.4 | LLM 融合：将 STT 结果 + 表情结果 + 多模态分析合并为统一文本 | 输出 "带情感和表情的对话/描述" |

**Phase 2 产出**：一个支持视频输入、输出带情感描述文本的 Agent。

---

### Phase 3：深度理解增强（预计 2-3 周）

**目标**：加入梗识别、搜索增强、评论区分析。

| 步骤 | 内容 | 验证标准 |
|------|------|----------|
| 3.1 | 接入 Google/Bing 反向图片搜索，对关键帧搜互联网 | 能返回相关网页和讨论 |
| 3.2 | 加入感知哈希（pHash）梗库匹配（可选） | 已知梗图被正确识别 |
| 3.3 | 评论区抓取（YouTube API 等）+ LLM 分析 | 提取社区对视频的解读 |
| 3.4 | LangGraph 条件路由：自动判断是否需要二次搜索/分析 | Agent 能自主决策 |

---

### Phase 4：产品化（预计 2-4 周）

**目标**：封装为可用的服务。

| 步骤 | 内容 |
|------|------|
| 4.1 | FastAPI 封装：提供 REST API |
| 4.2 | n8n 工作流封装（可选） |
| 4.3 | 前端界面（可选） |
| 4.4 | 性能优化：GPU 推理加速、批处理 |

---

## 五、风险与注意事项

### 5.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **pyannote Python 3.12+ 兼容问题** | 说话人分离功能不可用 | 使用 Python 3.11 或 scribe-forge-ai 的 Resemblyzer 后端 |
| **SenseVoice 不支持流式** | 只能离线处理，非实时 | 当前需求为离线分析，非实时，影响可控 |
| **长视频 Token 成本高** | GPT-4o 处理大量截图费用昂贵 | 优先用 Gemini Flash（$0.35/1M tokens）；选择性截图（关键帧） |
| **面部表情在暗光/侧脸场景不准** | 表情数据不完整 | 不单一依赖表情，SenseVoice 语音情感 + LLM 多模态交叉验证 |
| **梗识别无 100% 可靠方案** | 部分文化梗无法识别 | 标记为 UNCLEAR，不做强行猜测 |

### 5.2 成本估算

| 组件 | 类型 | 月成本估算 |
|------|------|------------|
| SenseVoice-Small | 本地 | 免费（需 GPU） |
| WhisperX + pyannote | 本地 | 免费（需 GPU） |
| audio-separator | 本地 | 免费（需 GPU） |
| DeepFace | 本地 | 免费（CPU 可运行） |
| GPT-4o API | 云端 | $10-50/月（取决于视频量和截图数） |
| Gemini 2.0 Flash API | 云端 | $1-5/月（极便宜） |
| Bing Image Search | 云端 | 1000 次/月免费 |

**总体月成本**：本地 GPU 电费 + API $10-50/月（取决于用量）

### 5.3 GPU 需求

- **最低**：8 GB VRAM（Model 推理分时加载）
- **推荐**：12-16 GB VRAM（可同时加载多模型）
- **极限**：CPU-only 也可运行（速度慢 5-10x，但功能完整）

---

## 六、本轮不做 / 后续阶段（Deferred Scope）

| 项目 | 原因 | 触发条件 |
|------|------|----------|
| **实时流式处理** | 当前需求为离线分析，实时方案复杂度高 3-5 倍 | 有实时场景需求时进入 |
| **自建梗图数据库** | 维护成本高，先用搜索+LLM 替代 | Phase 3 验证搜索方案不足后 |
| **前端可视化界面** | MVP 阶段优先验证核心链路 | Phase 4 产品化阶段 |
| **多视频对比分析** | 超出当前单视频理解范围 | 单视频链路稳定后 |
| **Fine-tune 情感模型** | SenseVoice 预训练已基本满足需求 | 特定领域情感识别率不达标时 |

---

## 七、总结

### 核心结论

**整体可行性：高（⭐⭐⭐⭐⭐）**

- 人声分离、说话人分离、STT+情感识别这三个核心环节都有成熟的开源方案，各自独立可用
- SenseVoice-Small 是整个链路的**关键节点**：它原生内置情感识别 + 音频事件检测，大幅简化了架构
- 多模态 LLM（GPT-4o/Gemini）的截图分析能力已经非常成熟，可以填补纯 STT 在视觉和文化理解上的空白
- 唯一定性为"部分可行"的是梗/文化语境识别（5.3 节），需要接受一定的不完美

### 推荐技术栈速览

```
人声分离:     audio-separator (BS-Roformer)
说话人分离:   WhisperX + pyannote.audio 3.1
STT+情感:     SenseVoice-Small (FunASR)
表情识别:     DeepFace + MediaPipe
多模态 LLM:   Gemini 2.0 Flash（主力）+ GPT-4o（补充）
Agent 框架:   LangGraph + LangChain
视频截图:     OpenCV / ffmpeg
搜索增强:     Bing Image Search / Tavily
```

### 下一步

如果确认进入实施阶段，建议走 **devflow** 流程：
1. **Align（对齐）**：确认需求边界和成功标准
2. **Plan（计划）**：输出详细实施方案（基于本文档深化）
3. **Apply（实施）**：按 Phase 1 → Phase 2 → Phase 3 → Phase 4 推进
