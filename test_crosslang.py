"""
Genie-TTS 跨语言测试脚本
========================
直接使用 genie_tts 库，无需启动 api.py 服务器。
首次运行时自动下载 feibi 角色模型（~230 MB）。

运行：
  python test_crosslang.py

输出 WAV 文件保存在 test_output/ 目录。
"""

import sys
import os
import json
from pathlib import Path

# ── 环境配置：确保从任意工作目录运行都正常 ─────────────────────────────
_THIS_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(_THIS_DIR / "src"))
os.environ.setdefault("GENIE_DATA_DIR", str(_THIS_DIR / "GenieData"))
os.chdir(_THIS_DIR)          # CharacterModels/ 相对路径从脚本目录解析

import genie_tts as genie

OUT_DIR = _THIS_DIR / "test_output"
OUT_DIR.mkdir(exist_ok=True)

# ── 1. 加载预训练角色（首次自动下载）────────────────────────────────────
print("=" * 60)
print("Step 1: 加载 feibi 预训练角色（首次运行自动下载 ~230 MB）")
genie.load_predefined_character('feibi')

# 读取 feibi 的默认参考音频（用于跨语言测试）
_feibi_dir = _THIS_DIR / "CharacterModels" / "v2ProPlus" / "feibi"
with open(_feibi_dir / "prompt_wav.json", encoding="utf-8") as f:
    _presets = json.load(f)
REF_WAV  = str(_feibi_dir / "prompt_wav" / _presets["Normal"]["wav"])
REF_TEXT = _presets["Normal"]["text"]

print(f"  参考音频: {REF_WAV}")
print(f"  参考文本: {REF_TEXT}")
print()

# ── 2. 测试用例 ──────────────────────────────────────────────────────────
# (描述, text_language, text)
CASES = [
    # 跨语言克隆
    ("中文参考→日语",     "ja",   "こんにちは、今日はいい天気ですね。私はあなたの声で話します。"),
    ("中文参考→英语",     "en",   "Hello, this is a cross-language voice cloning test. How does it sound?"),
    ("中文参考→韩语",     "ko",   "안녕하세요. 오늘 날씨가 정말 좋네요."),
    # auto 混合检测
    ("中文参考→中英混合", "auto", "今天的weather非常nice，我很happy，感觉整个人都好了。"),
    # baseline：纯中文（音质最佳）
    ("中文参考→中文",     "zh",   "在此之前，请您务必继续享受旅居拉古那的时光。"),
    # auto 单语言检测
    ("auto检测日文",      "auto", "桜の花びらが風に舞い、春の訪れを告げています。"),
    ("auto检测英文",      "auto", "The quick brown fox jumps over the lazy dog."),
    ("auto检测中文",      "auto", "人工智能技术正在改变我们的生活方式。"),
    ("auto检测中英",      "auto", "这个model的performance真的很impressive。"),
]

print("Step 2: 开始跨语言合成测试")
print("=" * 60)

results = []
for desc, text_lang, text in CASES:
    out_file = str(OUT_DIR / f"{desc.replace('→', '_').replace(' ', '_')}.wav")

    # 每条用例都设置参考音频，ref_language 明确为 zh
    genie.set_reference_audio(
        character_name='feibi',
        audio_path=REF_WAV,
        audio_text=REF_TEXT,
        ref_language='zh',   # 参考音频是中文
    )

    print(f"  测试: {desc}")
    print(f"        text_language={text_lang}")
    print(f"        text={text[:50]}{'...' if len(text) > 50 else ''}")

    try:
        genie.tts(
            character_name='feibi',
            text=text,
            play=False,
            save_path=out_file,
            text_language=text_lang,
        )
        size_kb = os.path.getsize(out_file) / 1024
        status = f"[OK]   → {out_file}  ({size_kb:.1f} KB)"
        ok = True
    except Exception as e:
        status = f"[FAIL] {e}"
        ok = False

    print(f"        {status}")
    print()
    results.append((desc, ok, status))

# ── 3. 汇总 ─────────────────────────────────────────────────────────────
print("=" * 60)
print("测试结果汇总")
print("=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
for desc, ok, status in results:
    mark = "✓" if ok else "✗"
    print(f"  {mark} {desc:18s}  {status}")
print()
print(f"通过: {passed}/{len(results)}")
print(f"输出目录: {OUT_DIR}")

