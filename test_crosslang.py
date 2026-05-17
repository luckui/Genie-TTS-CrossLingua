"""
Genie-TTS 跨语言测试脚本
========================
前置条件：api.py 已在 9881 端口运行
  python api.py --port 9881 --model "D:/Other/Live2dWeb/Genie-TTS GUI/CharacterModels/v2ProPlus/feibi/tts_models"

运行：
  python test_crosslang.py
"""

import os
import sys
import requests

API = "http://localhost:9881"
MODEL_DIR  = r"D:\Other\Live2dWeb\Genie-TTS GUI\CharacterModels\v2ProPlus\feibi\tts_models"
REF_WAV    = r"D:\Other\Live2dWeb\Genie-TTS GUI\CharacterModels\v2ProPlus\feibi\prompt_wav\zh_vo_Main_Linaxita_2_1_10_26.wav"
REF_TEXT   = "在此之前，请您务必继续享受旅居拉古那的时光。"
OUT_DIR    = "test_output"

os.makedirs(OUT_DIR, exist_ok=True)

# ────────────────────────────────────────
# 测试用例定义
# ────────────────────────────────────────
CASES = [
    # (描述,          ref_language, text_language, text)
    # ── 问题1：跨语言克隆 ──
    ("中文参考→日语",  "zh", "ja",     "こんにちは、今日はいい天気ですね。私はあなたの声で話します。"),
    ("中文参考→英语",  "zh", "en",     "Hello, this is a cross-language voice cloning test. How does it sound?"),
    ("中文参考→韩语",  "zh", "ko",     "안녕하세요. 오늘 날씨가 정말 좋네요."),
    # ── 问题2：中英混合 ──
    ("中文参考→中英混合", "zh", "auto", "今天的weather非常nice，我很happy，感觉整个人都好了。"),
    # ── 纯中文（baseline，应该最好） ──
    ("中文参考→中文",  "zh", "zh",     "在此之前，请您务必继续享受旅居拉古那的时光。"),
    # ── auto 模式检测 ──
    ("auto检测日文",   "zh", "auto",   "桜の花びらが風に舞い、春の訪れを告げています。"),
    ("auto检测英文",   "zh", "auto",   "The quick brown fox jumps over the lazy dog."),
    ("auto检测中文",   "zh", "auto",   "人工智能技术正在改变我们的生活方式。"),
    ("auto检测中英",   "zh", "auto",   "这个model的performance真的很impressive。"),
]

# ────────────────────────────────────────
# 1. 加载模型
# ────────────────────────────────────────
print("=" * 60)
print("Step 1: 加载模型")
resp = requests.post(f"{API}/load", data={"model_dir": MODEL_DIR, "language": "auto"})
if resp.status_code != 200:
    print(f"  [FAIL] 加载失败: {resp.text}")
    sys.exit(1)
print(f"  [OK]   {resp.json()}")

# ────────────────────────────────────────
# 2. 逐个测试
# ────────────────────────────────────────
print()
print("Step 2: 开始跨语言合成测试")
print("=" * 60)

results = []
for desc, ref_lang, text_lang, text in CASES:
    out_file = os.path.join(OUT_DIR, f"{desc.replace('→', '_').replace(' ', '_')}.wav")
    print(f"  测试: {desc}")
    print(f"        ref_language={ref_lang}  text_language={text_lang}")
    print(f"        text={text[:40]}{'...' if len(text)>40 else ''}")

    with open(REF_WAV, "rb") as f:
        resp = requests.post(
            f"{API}/tts",
            data={
                "text": text,
                "text_language": text_lang,
                "ref_text": REF_TEXT,
                "ref_language": ref_lang,
            },
            files={"ref_audio": ("ref.wav", f, "audio/wav")},
            timeout=120,
        )

    if resp.status_code == 200:
        with open(out_file, "wb") as wf:
            wf.write(resp.content)
        size_kb = len(resp.content) / 1024
        status = f"[OK]   → {out_file}  ({size_kb:.1f} KB)"
        ok = True
    else:
        status = f"[FAIL] HTTP {resp.status_code}: {resp.text[:200]}"
        ok = False

    print(f"        {status}")
    print()
    results.append((desc, ok, status))

# ────────────────────────────────────────
# 3. 汇总
# ────────────────────────────────────────
print("=" * 60)
print("测试结果汇总")
print("=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
for desc, ok, status in results:
    mark = "✓" if ok else "✗"
    print(f"  {mark} {desc:20s}  {status}")
print()
print(f"通过: {passed}/{len(results)}")
print(f"输出目录: {os.path.abspath(OUT_DIR)}")
