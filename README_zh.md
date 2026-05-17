<div align="center">
<pre>
██████╗  ███████╗███╗   ██╗██╗███████╗
██╔════╝ ██╔════╝████╗  ██║██║██╔════╝
██║  ███╗█████╗  ██╔██╗ ██║██║█████╗  
██║   ██║██╔══╝  ██║╚██╗██║██║██╔══╝  
╚██████╔╝███████╗██║ ╚████║██║███████╗
 ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚══════╝
</pre>
</div>

<div align="center">

# 🔮 GENIE Cross-Lingua

**[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) CPU 推理 · 跨语言音色克隆 · 自动语言检测**

[简体中文](./README_zh.md) | [English](./README.md)

</div>

> [High-Logic/Genie](https://github.com/High-Logic/Genie) 的社区 Fork，由 [@luckui](https://github.com/luckui) 维护

---

## ✨ 本 Fork 新增了什么

原版 GENIE 要求参考音频语言与合成文本语言保持一致。本 Fork 去除了这一限制：

| 功能 | 上游 GENIE | 本 Fork |
|------|:---------:|:-------:|
| 支持中 / 英 / 日 / 韩 TTS | ✅（仅限模型语言） | ✅ |
| `text_language` — 每次请求指定合成语言 | — | ✅ |
| `ref_language` — 参考音频语言独立设置 | — | ✅ |
| `'auto'` — 按句自动语言检测 | — | ✅ |
| 生产 FastAPI 适配服务器（`server.py`） | — | ✅ |
| 开发测试服务器（`api.py`） | — | ✅ |

---

## ⚡ 快速示例

### 跨语言：中文音色 → 日语语音

```python
import genie_tts as genie

genie.load_character('feibi', r"CharacterModels/v2ProPlus/feibi/tts_models", language='auto')

# 参考音频为中文，合成日语——音色跨越语言障碍克隆
genie.set_reference_audio(
    'feibi', r"ref.wav",
    "在此之前，请您务必继续享受旅居拉许那的时光。",
    ref_language='zh',       # ← 参考音频语言
)
genie.tts('feibi', 'こんにちは、今日はいい天気ですね。', play=True, text_language='ja')
genie.wait_for_playback_done()
```

### 混合语言自动检测

```python
genie.tts('feibi', "Hello！今天天气真好，let's go！", play=True, text_language='auto')
genie.wait_for_playback_done()
```

### 更多跨语言组合

```python
# 日语音色 → 中文
genie.set_reference_audio('mika', 'ref.wav', '私も昔、これを持ってたなぁ。', ref_language='ja')
genie.tts('mika', '你好，我是米卡。', play=True, text_language='zh')

# 英语音色 → 韩语
genie.set_reference_audio('37', 'ref.wav', 'And now, I belong to this set.', ref_language='en')
genie.tts('37', '안녕하세요！', play=True, text_language='ko')
```

### 启动生产服务器

```bash
uvicorn server:app --host 127.0.0.1 --port 9882
```

```bash
curl -X POST http://localhost:9882/tts/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは！", "speaker": "feibi", "language": "ja"}' \
  --output output.wav
```

---

## 🔮 关于 GENIE 上游项目

> 完整文档、模型转换教程等详见[上游仓库](https://github.com/High-Logic/Genie)。

GENIE 是 [High-Logic](https://github.com/High-Logic) 基于 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 构建的轻量级 CPU 推理引擎，通过将模型转换为 ONNX 格式，在 CPU 上实现近乎即时的 TTS 合成。

**性能（i7-13620H · 100 条约 20 字日语句子）：**

| | 🔮 GENIE | 官方 PyTorch | 官方 ONNX |
|:--|:--:|:--:|:--:|
| 首次推理延迟 | **1.13s** | 1.35s | 3.57s |
| 运行时大小 | **~200MB** | ~数 GB | 相近 |
| 模型大小 | **~230MB** | 相近 | ~750MB |

**安装：**

```bash
pip install genie-tts          # 上游版本（不含跨语言功能）
# 或
pip install -e .               # 本 Fork，从源码安装
pip install langdetect          # 'auto' 检测所需依赖
```

**预置角色**（无需自备模型）：

```python
import genie_tts as genie

genie.load_predefined_character('feibi')   # 也可用 'mika'（日语）、'thirtyseven'（英语）
genie.tts(character_name='feibi', text='请好好珍惜这段时光。', play=True)
genie.wait_for_playback_done()
```

> 浏览所有可用角色：[HuggingFace Model Hub →](https://huggingface.co/High-Logic/Genie/tree/main/CharacterModels)

---

## 🌍 跨语言 API 参考

### 新增参数

| 参数 | 位置 | 说明 | 默认值 |
|------|------|------|--------|
| `text_language` | `tts()`, `tts_async()` | 合成文本的语言。`'auto'` 使用 [`langdetect`](https://pypi.org/project/langdetect/) 按句自动检测。 | `None`（使用模型语言） |
| `ref_language` | `set_reference_audio()` | 参考音频文字的语言，与 `text_language` 独立设置。 | `None`（回退到 `language`） |
| `language='auto'` | `load_character()` | 支持 `'auto'` — 将语言决策推迟到推理时。 | — |

支持的语言代码（均已归一化）：`'zh'` / `'en'` / `'ja'` / `'ko'` / `'auto'` — `'japanese'`、`'Chinese'` 等别名同样有效。

---

## 🌐 生产服务器（`server.py`）

`server.py` 是一个生产级 FastAPI 适配器，特性如下：

- 启动时扫描 `CharacterModels/v2ProPlus/` 并预加载所有角色
- **asyncio 推理锁** — 串行化请求，防止 CPU 资源竞争
- **按块断连检测** — 客户端断开时立即中止推理
- `/tts/generate` 接口与 [live2d-pet](https://github.com/luckui/ai-live2d-go) 兼容

### 目录结构

```
<仓库根目录>/
├── CharacterModels/
│   └── v2ProPlus/
│       ├── feibi/
│       │   ├── tts_models/          ← ONNX 模型文件
│       │   ├── prompt_wav/          ← 参考音频 .wav 文件
│       │   └── prompt_wav.json      ← 预设：{"Normal": {"wav": "...", "text": "..."}}
│       └── mika/ ...
├── GenieData/                       ← 共享推理资源（约 391MB）
└── config.yaml                      ← 可选配置
```

**`config.yaml`（可选）：**

```yaml
genie:
  default_character: feibi   # speaker 字段为空时使用的角色
  default_preset: Normal     # 从 prompt_wav.json 读取的预设项

server:
  host: "127.0.0.1"
  port: 9882
```

**启动：**

```bash
pip install fastapi uvicorn pyyaml langdetect
uvicorn server:app --host 127.0.0.1 --port 9882
```

**接口：**

```
POST /tts/generate   {"text": "...", "speaker": "feibi", "language": "auto"}  → audio/wav
GET  /speakers       → 已加载角色列表
GET  /health         → {"status": "ok", "characters": [...]}
```

---

## 🛠 开发测试服务器（`api.py`）

`api.py` 是一个轻量级开发服务器，无需预置角色：

```bash
pip install fastapi uvicorn langdetect
uvicorn api:app --host 0.0.0.0 --port 9881
```

```bash
# 加载任意 ONNX 模型
curl -X POST http://localhost:9881/load \
  -F "model_dir=CharacterModels/v2ProPlus/feibi/tts_models" -F "language=auto"

# 合成（每次请求上传参考音频）
curl -X POST http://localhost:9881/tts \
  -F "text=こんにちは！" -F "text_language=ja" \
  -F "ref_audio=@ref.wav" \
  -F "ref_text=在此之前，请您务必继续享受旅居拉许那的时光。" -F "ref_language=zh" \
  --output output.wav
```

---

## 📝 路线图

* [x] **🌐 语言扩展**
    * [x] 中文、英语、日语、韩语
    * [x] **`auto` 自动语言检测** — 按句检测，使用 `langdetect` *(本 Fork 新增)*
    * [x] **跨语言音色克隆** — `ref_language` + `text_language` 独立控制 *(本 Fork 新增)*

* [x] **🚀 模型兼容性**
    * [x] GPT-SoVITS V2、V2ProPlus
    * [ ] V3、V4 及更多

* [x] **📦 部署**
    * [x] Windows 整合包 *(上游)*
    * [x] 生产 FastAPI 服务器 `server.py` *(本 Fork 新增)*
    * [ ] Docker 镜像

---

## 🙏 致谢

本项目为 **[GENIE](https://github.com/High-Logic/Genie)** 的社区 Fork，上游项目由 [High-Logic](https://github.com/High-Logic) 创建和维护。所有核心 CPU 推理优化、ONNX 转换及模型架构工作均源自上游项目。

如果你觉得 GENIE 有用，请给上游项目 ⭐：
**https://github.com/High-Logic/Genie**
