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

# 🔮 GENIE: [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 轻量级推理引擎

**在 CPU 上体验近乎即时的语音合成**

[简体中文](./README_zh.md) | [English](./README.md)

</div>

> **📌 本仓库为社区 Fork**，上游项目为 [High-Logic/Genie](https://github.com/High-Logic/Genie)，
> 由 [@luckui](https://github.com/luckui) 维护。
> 本 Fork 新增：**跨语言语音合成**与 `auto` 自动语言检测，
> 无论参考音频是什么语言，都能以任意目标语言合成。
> 详见 [本 Fork 的改动](#-本-fork-的改动) 一节。

---

**GENIE** 是一个基于开源 TTS 项目 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 构建的轻量级推理引擎。它集成了 TTS
推理、ONNX 模型转换、API 服务端以及其他核心功能，旨在提供极致的性能和便利性。

* **✅ 支持的模型版本：** GPT-SoVITS V2, V2ProPlus
* **✅ 支持的语言：** 日语、英语、中文、韩语，以及 **`auto` 自动检测**（本 Fork 新增）
* **✅ 支持的 Python 版本：** >= 3.9

---

## 🎬 演示视频

- **[➡️ 观看演示视频（中文）](https://www.bilibili.com/video/BV1d2hHzJEz9)**

---

## 🚀 性能优势

GENIE 针对原始模型进行了优化，以实现出色的 CPU 性能。

| 特性         |  🔮 GENIE   | 官方 PyTorch 模型 | 官方 ONNX 模型 |
|:-----------|:-----------:|:-------------:|:----------:|
| **首次推理延迟** |  **1.13s**  |     1.35s     |   3.57s    |
| **运行时大小**  | **\~200MB** |    \~数 GB     | 与 GENIE 相似 |
| **模型大小**   | **\~230MB** |  与 GENIE 相似   |  \~750MB   |

> 📝 **延迟测试说明：** 所有延迟数据均基于 100 个日语句子（每句约 20 个字符）的测试集取平均值。测试环境为 CPU i7-13620H。

---

## 🏁 快速开始

> **⚠️ 重要提示：** 建议在 **管理员模式** 下运行 GENIE，以避免潜在的性能下降。

### 📦 安装

通过 pip 安装：

```bash
pip install genie-tts
```

## 📥 预训练模型

首次运行 GENIE 时，需要下载资源文件（**~391MB**）。您可以按照库的提示自动下载。

> 或者，您可以从 [HuggingFace](https://huggingface.co/High-Logic/Genie/tree/main/GenieData) 手动下载文件并将其放置在本地文件夹中。然后在导入库
**之前** 设置 `GENIE_DATA_DIR` 环境变量：

```python
import os

# 设置手动下载的资源文件路径
# 注意：请在导入 genie_tts 之前执行此操作
os.environ["GENIE_DATA_DIR"] = r"C:\path\to\your\GenieData"

import genie_tts as genie

# 库现在将从指定目录加载资源
```

如果你想启用**仅用于中文推理**、用于改善中文韵律的可选 Chinese RoBERTa 文本特征，也可以这样下载：

```python
import genie_tts as genie

# 只下载可选的 Chinese RoBERTa 资源
genie.download_roberta_data()

# 或者直接走内置的完整资源下载流程，
# 该流程现在也会顺带下载可选的 Chinese RoBERTa 资源
genie.download_genie_data()
```

这些 RoBERTa 特征仅用于**中文**路径，以改善中文韵律；
它们**不应该用于**日语 / 英语 / 韩语推理。

### ⚡️ 快速试用

还没有 GPT-SoVITS 模型？没问题！
GENIE 包含几个预定义的说话人角色，您可以立即使用 —— 例如：

* **Mika (聖園ミカ)** — *蔚蓝档案 (Blue Archive)* (日语)
* **ThirtySeven (37)** — *重返未来：1999 (Reverse: 1999)* (英语)
* **Feibi (菲比)** — *鸣潮 (Wuthering Waves)* (中文)

您可以在此处浏览所有可用角色：
**[https://huggingface.co/High-Logic/Genie/tree/main/CharacterModels](
https://huggingface.co/High-Logic/Genie/tree/main/CharacterModels)**

使用以下示例进行尝试：

```python
import genie_tts as genie
import time

# 首次运行时自动下载所需文件
genie.load_predefined_character('mika')

genie.tts(
    character_name='mika',
    text='どうしようかな……やっぱりやりたいかも……！',
    play=True,  # 直接播放生成的音频
)

genie.wait_for_playback_done()  # 确保音频播放完成
```

### 🎤 TTS 最佳实践

一个简单的 TTS 推理示例：

```python
import genie_tts as genie

# 第一步：加载角色语音模型
genie.load_character(
    character_name='<CHARACTER_NAME>',  # 替换为您的角色名称
    onnx_model_dir=r"<PATH_TO_CHARACTER_ONNX_MODEL_DIR>",  # 包含 ONNX 模型的文件夹
    language='<LANGUAGE_CODE>',  # 替换为语言代码，例如 'en', 'zh', 'jp', 'kr'
)

# 第二步：设置参考音频（用于情感和语调克隆）
genie.set_reference_audio(
    character_name='<CHARACTER_NAME>',  # 必须与加载的角色名称匹配
    audio_path=r"<PATH_TO_REFERENCE_AUDIO>",  # 参考音频的路径
    audio_text="<REFERENCE_AUDIO_TEXT>",  # 对应的文本
    # ref_language：参考音频文字的语言（本 Fork 新增）
    # 默认与模型语言一致；跨语言合成时请明确指定。
    ref_language='<LANGUAGE_CODE>',  # 如 'zh', 'en', 'ja', 'ko', 'auto'
)

# 第三步：运行 TTS 推理并生成音频
genie.tts(
    character_name='<CHARACTER_NAME>',  # 必须与加载的角色匹配
    text="<TEXT_TO_SYNTHESIZE>",  # 要合成的文本
    play=True,  # 直接播放音频
    save_path="<OUTPUT_AUDIO_PATH>",  # 输出音频文件路径
    # text_language：合成文本的语言（本 Fork 新增）
    # 'auto' 按句自动检测；或指定 'zh', 'en', 'ja', 'ko'。
    text_language='auto',
)

genie.wait_for_playback_done()  # 确保音频播放完成

print("🎉 Audio generation complete!")
```

---

## 🌍 跨语言合成 *(本 Fork 新增)*

本 Fork 实现了**参考音频语言**与**合成文本语言**的独立控制，
可以以一种语言的音色克隆另一种语言的语音，不损失音质。

### 新增参数

| 参数 | 位置 | 说明 |
|------|------|------|
| `text_language` | `tts()`, `tts_async()` | 合成文本的语言。`'auto'` 使用 [`langdetect`](https://pypi.org/project/langdetect/) 按句自动检测。 |
| `ref_language` | `set_reference_audio()` | 参考音频文字的语言，与 `text_language` 独立设置。 |
| `'auto'` | 两者均支持 | 自动路由到对应的 G2P + BERT 流水线。 |

### 示例：中文音色 → 日语语音

```python
import genie_tts as genie

genie.load_character(
    character_name='feibi',
    onnx_model_dir=r"<菲比 ONNX 模型目录>",
    language='auto',  # 现支持 'auto'
)

# 参考音频是中文，但要合成日语
genie.set_reference_audio(
    character_name='feibi',
    audio_path=r"<中文参考音频.wav>",
    audio_text="你好，这是一段中文参考音频。",
    ref_language='zh',     # 参考音频语言
)

genie.tts(
    character_name='feibi',
    text='こんにちは、今日はいい天気ですね。',
    play=True,
    text_language='ja',    # 合成文本语言
)
```

使用 `text_language='auto'` 处理中英混合文本：

```python
genie.tts(
    character_name='feibi',
    text='Hello，今天天気真好，let\'s go！',
    play=True,
    text_language='auto',  # 按句自动检测中文/英文
)
```

### 测试

```bash
pip install langdetect  # auto 检测所需依赖
python test_crosslang.py
```

---

## 🔧 模型转换

要将原始 GPT-SoVITS 模型转换为 GENIE 格式，请确保已安装 `torch`：

```bash
pip install torch
```

使用内置的转换工具：

> **提示：** `convert_to_onnx` 目前支持 V2 和 V2ProPlus 模型。

```python
import genie_tts as genie

genie.convert_to_onnx(
    torch_pth_path=r"<YOUR .PTH MODEL FILE>",  # 替换为您的 .pth 文件
    torch_ckpt_path=r"<YOUR .CKPT CHECKPOINT FILE>",  # 替换为您的 .ckpt 文件
    output_dir=r"<ONNX MODEL OUTPUT DIRECTORY>"  # 保存 ONNX 模型的目录
)
```

---

## 🌐 启动 FastAPI 服务

GENIE 包含一个轻量级的 FastAPI 服务器：

```python
import genie_tts as genie

# 启动服务
genie.start_server(
    host="0.0.0.0",  # 主机地址
    port=8000,  # 端口
    workers=1  # 工作进程数
)
```

> 关于请求格式和 API 详情，请参阅我们的 [API 服务教程](./Tutorial/English/API%20Server%20Tutorial.py)。

### 独立服务脚本 *(本 Fork 新增)*

本 Fork 提供两个额外的服务器脚本：

| 脚本 | 端口 | 适用场景 |
|------|------|----------|
| `api.py` | 9881 | **开发 / 测试** — 每次请求可上传任意参考音频，通过 `POST /load` 指定模型目录。 |
| `server.py` | 9882 | **生产部署** — 启动时预加载 `CharacterModels/`；启用推理锁和断连检测；与 [live2d-pet](https://github.com/luckui/live2d-pet) 集成兼容。 |

**开发快速启动：**

```bash
pip install fastapi uvicorn langdetect
uvicorn api:app --host 0.0.0.0 --port 9881
```

**生产部署快速启动：**

```bash
# 将角色 ONNX 模型放入 CharacterModels/v2ProPlus/<角色名>/tts_models/ 目录
pip install fastapi uvicorn pyyaml langdetect
uvicorn server:app --host 127.0.0.1 --port 9882
```


---

## 📝 路线图

* [x] **🌐 语言扩展**

    * [x] 添加对 **中文** 和 **英文** 的支持。
    * [x] **`auto` 自动语言检测** — 支持混合语言文本按句检测 *(本 Fork 新增)*。
    * [x] **跨语言音色克隆** — `ref_language` / `text_language` 参数独立控制 *(本 Fork 新增)*。

* [x] **🚀 模型兼容性**

    * [x] 支持 `V2ProPlus`。
    * [ ] 支持 `V3`、`V4` 等更多版本。

* [x] **📦 简易部署**

    * [ ] 发布 **官方 Docker 镜像**。
    * [x] 提供开筱即用的 **Windows 整合包**。
    * [x] 独立 FastAPI 适配服务器（`server.py`）*(本 Fork 新增)*。

---

## 🙏 致谢

本项目来自 **[GENIE](https://github.com/High-Logic/Genie)**
由 [High-Logic](https://github.com/High-Logic) 创建和维护。所有核心推理、模型转换与 ONNX 优化均源自上游项目。

如果你觉得 GENIE 有用，请给上游项目 ⭐：
**https://github.com/High-Logic/Genie**
