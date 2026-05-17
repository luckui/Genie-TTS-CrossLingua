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

# 🔮 GENIE: [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) Lightweight Inference Engine

**Experience near-instantaneous speech synthesis on your CPU**

[简体中文](./README_zh.md) | [English](./README.md)

</div>

> **📌 This is a community fork** of [GENIE](https://github.com/High-Logic/Genie) by
> [High-Logic](https://github.com/High-Logic), maintained by
> [@luckui](https://github.com/luckui). Added in this fork:
> **cross-lingual synthesis** with `auto` language detection — synthesize in any
> language regardless of the reference audio's language.
> See the [Changes in this Fork](#-changes-in-this-fork) section for details.

---

**GENIE** is a lightweight inference engine built on the open-source TTS
project [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS). It integrates TTS inference, ONNX model conversion, API
server, and other core features, aiming to provide ultimate performance and convenience.

* **✅ Supported Model Version:** GPT-SoVITS V2, V2ProPlus
* **✅ Supported Language:** Japanese, English, Chinese, Korean, and **`auto` detection** (this fork)
* **✅ Supported Python Version:** >= 3.9

---

## 🎬 Demo Video

- **[➡️ Watch the demo video (Chinese)](https://www.bilibili.com/video/BV1d2hHzJEz9)**

---

## 🚀 Performance Advantages

GENIE optimizes the original model for outstanding CPU performance.

| Feature                     |  🔮 GENIE   | Official PyTorch Model | Official ONNX Model |
|:----------------------------|:-----------:|:----------------------:|:-------------------:|
| **First Inference Latency** |  **1.13s**  |         1.35s          |        3.57s        |
| **Runtime Size**            | **\~200MB** |      \~several GB      |  Similar to GENIE   |
| **Model Size**              | **\~230MB** |    Similar to GENIE    |       \~750MB       |

> 📝 **Latency Test Info:** All latency data is based on a test set of 100 Japanese sentences (\~20 characters each),
> averaged. Tested on CPU i7-13620H.

---

## 🏁 QuickStart

> **⚠️ Important:** It is recommended to run GENIE in **Administrator mode** to avoid potential performance degradation.

### 📦 Installation

Install via pip:

```bash
pip install genie-tts
```

## 📥 Pretrained Models

When running GENIE for the first time, it requires downloading resource files (**~391MB**). You can follow the library's
prompts to download them automatically.

> Alternatively, you can manually download the files
> from [HuggingFace](https://huggingface.co/High-Logic/Genie/tree/main/GenieData)
> and place them in a local folder. Then set the `GENIE_DATA_DIR` environment variable **before** importing the library:

```python
import os

# Set the path to your manually downloaded resource files
# Note: Do this BEFORE importing genie_tts
os.environ["GENIE_DATA_DIR"] = r"C:\path\to\your\GenieData"

import genie_tts as genie

# The library will now load resources from the specified directory
```

If you want the optional Chinese RoBERTa text features used only for **Chinese inference**
to improve Chinese prosody, you can also download them with:

```python
import genie_tts as genie

# Download only the optional Chinese RoBERTa assets
genie.download_roberta_data()

# Or use the built-in full resource download flow,
# which now also downloads the optional Chinese RoBERTa assets
genie.download_genie_data()
```

These RoBERTa features are intended only for the **Chinese** path to improve Chinese prosody.
They **should not be used** for non-Chinese inference (Japanese / English / Korean).

### ⚡️ Quick Tryout

No GPT-SoVITS model yet? No problem!
GENIE includes several predefined speaker characters you can use immediately —
for example:

* **Mika (聖園ミカ)** — *Blue Archive* (Japanese)
* **ThirtySeven (37)** — *Reverse: 1999* (English)
* **Feibi (菲比)** — *Wuthering Waves* (Chinese)

You can browse all available characters here:
**[https://huggingface.co/High-Logic/Genie/tree/main/CharacterModels](
https://huggingface.co/High-Logic/Genie/tree/main/CharacterModels)**

Try it out with the example below:

```python
import genie_tts as genie
import time

# Automatically downloads required files on first run
genie.load_predefined_character('mika')

genie.tts(
    character_name='mika',
    text='どうしようかな……やっぱりやりたいかも……！',
    play=True,  # Play the generated audio directly
)

genie.wait_for_playback_done()  # Ensure audio playback completes
```

### 🎤 TTS Best Practices

A simple TTS inference example:

```python
import genie_tts as genie

# Step 1: Load character voice model
genie.load_character(
    character_name='<CHARACTER_NAME>',  # Replace with your character name
    onnx_model_dir=r"<PATH_TO_CHARACTER_ONNX_MODEL_DIR>",  # Folder containing ONNX model
    language='<LANGUAGE_CODE>',  # Replace with language code, e.g., 'en', 'zh', 'jp', 'kr'
)

# Step 2: Set reference audio (for emotion and intonation cloning)
genie.set_reference_audio(
    character_name='<CHARACTER_NAME>',  # Must match loaded character name
    audio_path=r"<PATH_TO_REFERENCE_AUDIO>",  # Path to reference audio
    audio_text="<REFERENCE_AUDIO_TEXT>",  # Corresponding text
    # ref_language: language of the reference audio text (this fork)
    # Defaults to the model language; set explicitly for cross-lingual use.
    ref_language='<LANGUAGE_CODE>',  # e.g. 'zh', 'en', 'ja', 'ko', 'auto'
)

# Step 3: Run TTS inference and generate audio
genie.tts(
    character_name='<CHARACTER_NAME>',  # Must match loaded character
    text="<TEXT_TO_SYNTHESIZE>",  # Text to synthesize
    play=True,  # Play audio directly
    save_path="<OUTPUT_AUDIO_PATH>",  # Output audio file path
    # text_language: language of the synthesis text (this fork)
    # 'auto' detects per-sentence; or specify 'zh', 'en', 'ja', 'ko'.
    text_language='auto',
)

genie.wait_for_playback_done()  # Ensure audio playback completes

print("🎉 Audio generation complete!")
```

---

## 🌍 Cross-Lingual Synthesis *(this fork)*

This fork adds independent control over the **reference audio language** and the
**synthesis text language**, enabling cloning a voice in one language and
synthesizing speech in another — without quality degradation.

### New parameters

| Parameter | Where | Description |
|-----------|-------|-------------|
| `text_language` | `tts()`, `tts_async()` | Language of the text to synthesize. `'auto'` detects per-sentence using [`langdetect`](https://pypi.org/project/langdetect/). |
| `ref_language` | `set_reference_audio()` | Language of the reference audio transcript. Decoupled from `text_language`. |
| `'auto'` | both | New language value accepted everywhere; auto-routes to the correct G2P + BERT pipeline. |

### Example: Chinese voice → Japanese speech

```python
import genie_tts as genie

genie.load_character(
    character_name='feibi',
    onnx_model_dir=r"<PATH_TO_FEIBI_ONNX_DIR>",
    language='auto',  # 'auto' is now accepted
)

# Reference audio is Chinese, but we synthesize in Japanese
genie.set_reference_audio(
    character_name='feibi',
    audio_path=r"<PATH_TO_CHINESE_REF.wav>",
    audio_text="你好，这是一段中文参考音频。",
    ref_language='zh',     # reference audio language
)

genie.tts(
    character_name='feibi',
    text='こんにちは、今日はいい天気ですね。',
    play=True,
    text_language='ja',    # synthesis text language
)
```

Use `text_language='auto'` to handle mixed-language text automatically:

```python
genie.tts(
    character_name='feibi',
    text='Hello, 今天天气真好，let\'s go！',
    play=True,
    text_language='auto',  # detects zh / en per sentence
)
```

### Testing

Run the included test suite to verify cross-lingual output:

```bash
pip install langdetect  # required for auto detection
python test_crosslang.py
```

---

## 🔧 Model Conversion

To convert original GPT-SoVITS models for GENIE, ensure `torch` is installed:

```bash
pip install torch
```

Use the built-in conversion tool:

> **Tip:** `convert_to_onnx` currently supports V2 and V2ProPlus models.

```python
import genie_tts as genie

genie.convert_to_onnx(
    torch_pth_path=r"<YOUR .PTH MODEL FILE>",  # Replace with your .pth file
    torch_ckpt_path=r"<YOUR .CKPT CHECKPOINT FILE>",  # Replace with your .ckpt file
    output_dir=r"<ONNX MODEL OUTPUT DIRECTORY>"  # Directory to save ONNX model
)
```

---

## 🌐 Launch FastAPI Server

GENIE includes a lightweight FastAPI server:

```python
import genie_tts as genie

# Start server
genie.start_server(
    host="0.0.0.0",  # Host address
    port=8000,  # Port
    workers=1  # Number of workers
)
```

> For request formats and API details, see our [API Server Tutorial](./Tutorial/English/API%20Server%20Tutorial.py).

### Alternative standalone servers *(this fork)*

This fork ships two additional server scripts:

| Script | Port | Best for |
|--------|------|----------|
| `api.py` | 9881 | **Development / testing** — upload any reference audio per request; specify any ONNX model dir via `POST /load`. No pre-configured characters needed. |
| `server.py` | 9882 | **Production deployment** — pre-loads a `CharacterModels/` directory at startup; asyncio inference lock; per-chunk disconnect detection; compatible with [live2d-pet](https://github.com/luckui/live2d-pet) integration. |

**Quick start (development):**

```bash
pip install fastapi uvicorn langdetect
uvicorn api:app --host 0.0.0.0 --port 9881
```

**Quick start (production):**

```bash
# Place character ONNX dirs under CharacterModels/v2ProPlus/<char_name>/tts_models/
pip install fastapi uvicorn pyyaml langdetect
uvicorn server:app --host 127.0.0.1 --port 9882
```


---

## 📝 Roadmap

* [x] **🌐 Language Expansion**

    * [x] Add support for **Chinese** and **English**.
    * [x] **`auto` language detection** — per-sentence language detection for
          mixed-language text *(this fork)*.
    * [x] **Cross-lingual voice cloning** — independent `ref_language` /
          `text_language` parameters *(this fork)*.

* [x] **🚀 Model Compatibility**

    * [x] Support for `V2ProPlus`.
    * [ ] Support for `V3`, `V4`, and more.

* [x] **📦 Easy Deployment**

    * [ ] Release **Official Docker images**.
    * [x] Provide out-of-the-box **Windows bundles**.
    * [x] Standalone FastAPI adapter server (`server.py`) *(this fork)*.

---

## 🙏 Acknowledgements

This project is a community fork of
**[GENIE](https://github.com/High-Logic/Genie)** created and maintained by
[High-Logic](https://github.com/High-Logic). All core inference, model
conversion, and ONNX optimization work originates from their project.

Please ⭐ the upstream repository if you find GENIE useful:
**https://github.com/High-Logic/Genie**

---
