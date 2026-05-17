"""
Genie-TTS 最小化测试 API
========================
解决了原版两个核心问题：
  1. 参考音频语言（ref_language）与目标文本语言（text_language）可独立设置
  2. 新增 "auto" 模式：根据字符特征自动检测语言

用法示例：
  uvicorn api:app --port 9881

接口：
  POST /load       加载模型
  POST /tts        合成语音，返回 WAV 流
  GET  /           接口说明

测试跨语言克隆（中文参考音频 + 日语目标文本）：
  curl -X POST http://localhost:9881/tts \
    -F "text=こんにちは、今日はいい天気ですね。" \
    -F "text_language=ja" \
    -F "ref_audio=@/path/to/chinese_ref.wav" \
    -F "ref_text=你好，这是一段中文参考音频。" \
    -F "ref_language=zh" \
    --output output.wav
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# GenieData 路径：优先用环境变量，否则自动找打包版目录
_default_genie_data = os.path.join(os.path.dirname(__file__), "GenieData")
os.environ.setdefault("GENIE_DATA_DIR", os.path.abspath(_default_genie_data))

import asyncio
import io
import struct
import wave
import logging
import tempfile
from typing import Optional

from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import numpy as np

import genie_tts.Internal as genie

logger = logging.getLogger("genie-api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Genie-TTS Test API", version="0.1.0")

# 全局状态：已加载的角色名和模型路径
_loaded_model: Optional[str] = None
CHAR_NAME = "default"


# ─── 帮助函数 ────────────────────────────────────────────────────────────────

def numpy_to_wav_bytes(audio: np.ndarray, sample_rate: int = 32000) -> bytes:
    """将 float32 numpy 音频数组转换为 WAV bytes"""
    buf = io.BytesIO()
    audio_int16 = (audio.squeeze() * 32767).astype(np.int16)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    return buf.getvalue()


def pcm_chunks_to_wav_stream(chunks: list[bytes], sample_rate: int = 32000):
    """把 PCM int16 bytes 列表拼接成 WAV，以 bytes 返回"""
    pcm = b"".join(chunks)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buf.getvalue()


# ─── 路由 ────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    return {
        "description": "Genie-TTS 最小化测试 API",
        "loaded_model": _loaded_model,
        "endpoints": {
            "POST /load": "加载 ONNX 模型目录",
            "POST /tts": "合成语音，返回 WAV",
        },
        "language_options": [
            "auto   — 自动检测（推荐）",
            "zh     — 中文",
            "ja     — 日文",
            "en     — 英文",
            "ko     — 韩文",
            "hybrid — 中英混合",
        ],
    }


@app.post("/load")
def load_model(
    model_dir: str = Form(..., description="ONNX 模型目录路径"),
    language: str = Form("auto", description="模型默认语言，建议填 auto"),
):
    """加载 ONNX 模型。同一进程只保留一个模型，重复调用会替换旧模型。"""
    global _loaded_model
    try:
        if _loaded_model:
            genie.unload_character(CHAR_NAME)
        genie.load_character(CHAR_NAME, model_dir, language)
        _loaded_model = model_dir
        return {"status": "ok", "model_dir": model_dir, "language": language}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tts")
async def tts_endpoint(
    text: str = Form(..., description="要合成的目标文本"),
    text_language: str = Form("auto", description="目标文本语言，auto=自动检测"),
    ref_audio: UploadFile = File(..., description="参考音频文件（WAV/FLAC/OGG）"),
    ref_text: str = Form(..., description="参考音频对应的文字内容"),
    ref_language: str = Form("auto", description="参考音频的语言，auto=自动检测"),
):
    """
    合成语音接口。
    - ref_language 独立控制参考音频文本的 G2P，解决"中文参考→日语输出"的乱码问题。
    - text_language 控制目标文本的 G2P，支持 auto 自动检测。
    """
    if not _loaded_model:
        raise HTTPException(status_code=400, detail="请先调用 POST /load 加载模型")

    # 把上传的参考音频写到临时文件
    suffix = os.path.splitext(ref_audio.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await ref_audio.read())
        tmp_path = tmp.name

    try:
        # 设置参考音频，ref_language 独立于 text_language
        genie.set_reference_audio(
            character_name=CHAR_NAME,
            audio_path=tmp_path,
            audio_text=ref_text,
            language=text_language,
            ref_language=ref_language,
        )

        # 收集所有 PCM chunk
        pcm_chunks: list[bytes] = []
        async for chunk in genie.tts_async(
            character_name=CHAR_NAME,
            text=text,
            play=False,
            split_sentence=True,
            text_language=text_language,
        ):
            pcm_chunks.append(chunk)

        wav_bytes = pcm_chunks_to_wav_stream(pcm_chunks)
        return StreamingResponse(
            io.BytesIO(wav_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": 'attachment; filename="output.wav"'},
        )
    except Exception as e:
        logger.exception("TTS error")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)


# ─── 入口 ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Genie-TTS 测试 API")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9881)
    parser.add_argument(
        "--model", default=None,
        help="启动时自动加载的 ONNX 模型目录（可选）",
    )
    parser.add_argument(
        "--language", default="auto",
        help="启动时加载模型使用的默认语言（默认 auto）",
    )
    args = parser.parse_args()

    if args.model:
        genie.load_character(CHAR_NAME, args.model, args.language)
        _loaded_model = args.model
        logger.info(f"已预加载模型: {args.model}")

    uvicorn.run(app, host=args.host, port=args.port)
