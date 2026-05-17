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

**[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) on CPU · Cross-lingual voice cloning · Auto language detection**

[简体中文](./README_zh.md) | [English](./README.md)

</div>

> Community fork of [GENIE](https://github.com/High-Logic/Genie) by [High-Logic](https://github.com/High-Logic) · maintained by [@luckui](https://github.com/luckui)

---

## ✨ What This Fork Adds

The original GENIE requires the reference audio language and the synthesis text language to match.
This fork removes that constraint:

| Feature | Upstream GENIE | This Fork |
|---------|:--------------:|:---------:|
| Synthesize in zh / en / ja / ko | ✅ (model language only) | ✅ |
| `text_language` — per-request language override | — | ✅ |
| `ref_language` — decouple reference audio language | — | ✅ |
| `'auto'` — per-sentence language detection | — | ✅ |
| Production FastAPI adapter (`server.py`) | — | ✅ |
| Development test server (`api.py`) | — | ✅ |

---

## ⚡ Quick Examples

### Cross-lingual: Chinese voice → Japanese speech

```python
import genie_tts as genie

genie.load_character('feibi', r"CharacterModels/v2ProPlus/feibi/tts_models", language='auto')

# Reference audio is Chinese; synthesize in Japanese — voice clones across the language barrier
genie.set_reference_audio(
    'feibi', r"ref.wav",
    "在此之前，请您务必继续享受旅居拉许那的时光。",
    ref_language='zh',       # ← reference audio language
)
genie.tts('feibi', 'こんにちは、今日はいい天気ですね。', play=True, text_language='ja')
genie.wait_for_playback_done()
```

### Auto-detect mixed language

```python
genie.tts('feibi', "Hello! 今天天气真好，let's go！", play=True, text_language='auto')
genie.wait_for_playback_done()
```

### More cross-lingual combinations

```python
# Japanese voice → Chinese
genie.set_reference_audio('mika', 'ref.wav', '私も昔、これを持ってたなぁ。', ref_language='ja')
genie.tts('mika', '你好，我是米卡。', play=True, text_language='zh')

# English voice → Korean
genie.set_reference_audio('37', 'ref.wav', 'And now, I belong to this set.', ref_language='en')
genie.tts('37', '안녕하세요！', play=True, text_language='ko')
```

### Start the production server

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

## 🔮 About GENIE (Upstream)

> For full documentation, model conversion guides, and more, see the [upstream repository](https://github.com/High-Logic/Genie).

GENIE is a lightweight CPU inference engine for [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS), built by
[High-Logic](https://github.com/High-Logic). It achieves near-instantaneous TTS on CPU by converting GPT-SoVITS
models to ONNX.

**Performance (i7-13620H · 100 × ~20-char sentences):**

| | 🔮 GENIE | Official PyTorch | Official ONNX |
|:--|:--:|:--:|:--:|
| First inference | **1.13s** | 1.35s | 3.57s |
| Runtime size | **~200MB** | ~GB+ | similar |
| Model size | **~230MB** | similar | ~750MB |

**Installation:**

```bash
pip install genie-tts          # upstream (no cross-lingual features)
# or
pip install -e .               # this fork, from source
pip install langdetect          # required for 'auto' detection
```

**Predefined characters** (no custom model needed):

```python
import genie_tts as genie

genie.load_predefined_character('feibi')   # also: 'mika' (Japanese), 'thirtyseven' (English)
genie.tts(character_name='feibi', text='请好好珍惜这段时光。', play=True)
genie.wait_for_playback_done()
```

> Browse all available characters: [HuggingFace Model Hub →](https://huggingface.co/High-Logic/Genie/tree/main/CharacterModels)

---

## 🌍 Cross-Lingual API Reference

### New parameters

| Parameter | Where | Description | Default |
|-----------|-------|-------------|---------|
| `text_language` | `tts()`, `tts_async()` | Language of the synthesis text. `'auto'` detects per-sentence via [`langdetect`](https://pypi.org/project/langdetect/). | `None` (uses model language) |
| `ref_language` | `set_reference_audio()` | Language of the reference audio transcript. Independent of `text_language`. | `None` (falls back to `language`) |
| `language='auto'` | `load_character()` | Accepts `'auto'` — delays language decision to inference time. | — |

Accepted language codes (all normalized): `'zh'` / `'en'` / `'ja'` / `'ko'` / `'auto'` — aliases like `'japanese'`, `'Chinese'` also work.

---

## 🌐 Production Server (`server.py`)

`server.py` is a production-grade FastAPI adapter that:

- Scans `CharacterModels/v2ProPlus/` at startup and pre-loads every available character
- Uses an **asyncio inference lock** — serializes requests to prevent CPU contention
- Performs **per-chunk disconnect detection** — aborts immediately if the client disconnects
- Exposes a `/tts/generate` endpoint compatible with [live2d-pet](https://github.com/luckui/ai-live2d-go)

### Directory layout

```
<repo root>/
├── CharacterModels/
│   └── v2ProPlus/
│       ├── feibi/
│       │   ├── tts_models/          ← ONNX model files
│       │   ├── prompt_wav/          ← reference audio .wav files
│       │   └── prompt_wav.json      ← presets: {"Normal": {"wav": "...", "text": "..."}}
│       └── mika/ ...
├── GenieData/                       ← shared inference resources (~391MB)
└── config.yaml                      ← optional configuration
```

**`config.yaml` (optional):**

```yaml
genie:
  default_character: feibi   # used when speaker field is empty
  default_preset: Normal     # which preset entry from prompt_wav.json

server:
  host: "127.0.0.1"
  port: 9882
```

**Start:**

```bash
pip install fastapi uvicorn pyyaml langdetect
uvicorn server:app --host 127.0.0.1 --port 9882
```

**Endpoints:**

```
POST /tts/generate   {"text": "...", "speaker": "feibi", "language": "auto"}  → audio/wav
GET  /speakers       → list of loaded characters
GET  /health         → {"status": "ok", "characters": [...]}
```

---

## 🛠 Development Server (`api.py`)

`api.py` is a lightweight server for testing — no pre-configured characters needed:

```bash
pip install fastapi uvicorn langdetect
uvicorn api:app --host 0.0.0.0 --port 9881
```

```bash
# Load any ONNX model
curl -X POST http://localhost:9881/load \
  -F "model_dir=CharacterModels/v2ProPlus/feibi/tts_models" -F "language=auto"

# Synthesize (upload reference audio each request)
curl -X POST http://localhost:9881/tts \
  -F "text=こんにちは！" -F "text_language=ja" \
  -F "ref_audio=@ref.wav" \
  -F "ref_text=在此之前，请您务必继续享受旅居拉许那的时光。" -F "ref_language=zh" \
  --output output.wav
```

---

## 📝 Roadmap

* [x] **🌐 Language Support**
    * [x] Japanese, English, Chinese, Korean
    * [x] **`auto` language detection** — per-sentence via `langdetect` *(this fork)*
    * [x] **Cross-lingual voice cloning** — independent `ref_language` + `text_language` *(this fork)*

* [x] **🚀 Model Compatibility**
    * [x] GPT-SoVITS V2, V2ProPlus
    * [ ] V3, V4, and more

* [x] **📦 Deployment**
    * [x] Windows bundles *(upstream)*
    * [x] Production FastAPI server `server.py` *(this fork)*
    * [ ] Docker image

---

## 🙏 Acknowledgements

This is a community fork of **[GENIE](https://github.com/High-Logic/Genie)**, created and maintained by
[High-Logic](https://github.com/High-Logic). All core CPU inference optimization, ONNX conversion, and model
architecture work originates from their project.

Please ⭐ the upstream repository if you find GENIE useful:
**https://github.com/High-Logic/Genie**
