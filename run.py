#!/usr/bin/env python3
"""Wallpaper Engine Media Extractor — One-click extraction script.

Double-click run.bat (Windows) or run.command (macOS) to run this.
"""

import os
import sys
import shutil
import json
import locale

# ============================================================
# Language detection (auto-switch zh/en based on system locale)
# ============================================================
_LANG = "en"
try:
    locale.setlocale(locale.LC_ALL, "")
    lc = locale.getlocale()
    if lc and lc[0]:
        _LANG = "zh" if lc[0].startswith("zh") else "en"
except Exception:
    pass
# Use LANG env var as fallback
_lang_env = os.environ.get("LANG", "")
if _lang_env.startswith("zh"):
    _LANG = "zh"
elif _lang_env and not _lang_env.startswith("C"):
    _LANG = "en" 

def tr(zh, en):
    return zh if _LANG == "zh" else en

# ============================================================
# Paths
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TEMP_DIR = os.path.join(BASE_DIR, "_temp_extract")

sys.path.insert(0, BASE_DIR)
from extractor.pkg import extract_pkg
from extractor.tex import probe_tex, extract_tex
from extractor.utils import format_size


# ============================================================
# Error messages
# ============================================================
MSG = {
    "no_input": tr(
        "❌ input/ 中未找到 .pkg 或 .tex 文件\n"
        "   请将 Wallpaper Engine 的场景文件放入 input/ 文件夹\n\n"
        "   提示：input/ 支持放整个场景文件夹，例如：\n"
        "     input/\n"
        "       └── 场景名称/\n"
        "             ├── scene.pkg\n"
        "             ├── project.json\n"
        "             └── shaders/",
        "❌ No .pkg or .tex files found in input/\n"
        "   Please place Wallpaper Engine scene files into the input/ folder\n\n"
        "   Tip: input/ supports nested scene folders, e.g.:\n"
        "     input/\n"
        "       └── Scene Name/\n"
        "             ├── scene.pkg\n"
        "             ├── project.json\n"
        "             └── shaders/"
    ),
    "no_python": tr(
        "❌ 未检测到 Python 3！\n"
        "   请先安装 Python 3：https://www.python.org/downloads/",
        "❌ Python 3 is not installed!\n"
        "   Please install Python 3: https://www.python.org/downloads/"
    ),
    "python_version": tr(
        "❌ Python 版本过低，需要 Python 3.8 或更高版本",
        "❌ Python 3.8+ is required"
    ),
    "extract_ok": tr("✅ 提取完成！结果保存在 outputs/ 文件夹",
                     "✅ Extraction complete! Results saved to outputs/"),
    "extract_fail": tr("❌ 提取过程中出现问题，请检查 input/ 文件夹",
                       "❌ Extraction failed. Please check the input/ folder"),
    "cleanup": tr("  🧹 清理临时文件...", "  🧹 Cleaning temp files..."),
}

# ============================================================
# Extraction functions
# ============================================================

def log(msg):
    print(f"  {msg}")


def extract_pkg_file(pkg_path):
    """Extract PKG and organize results."""
    name = os.path.splitext(os.path.basename(pkg_path))[0]
    scene_dir = os.path.join(TEMP_DIR, name)

    log(tr("├─ 正在解包场景文件...", "├─ Extracting scene package..."))
    with open(pkg_path, "rb") as f:
        pkg_data = f.read()
    extracted = extract_pkg(pkg_data, scene_dir)

    for filepath, size in extracted:
        rel = os.path.relpath(filepath, scene_dir)

        if rel.endswith(".mp3"):
            dest_dir = os.path.join(OUTPUT_DIR, "audio")
            os.makedirs(dest_dir, exist_ok=True)
            base = os.path.basename(rel)
            # Clean up audio filenames
            if "LOST BLESS" in base:
                base = "track_01.mp3"
            elif "nayuta" in base:
                base = "track_02.mp3"
            dest = os.path.join(dest_dir, base)
            log(tr(f"├─ 音频: {base}", f"├─ Audio: {base}"))

        elif rel.endswith(".tex"):
            log(tr("├─ 纹理: material.tex", "├─ Texture: material.tex"))
            dest_dir = os.path.join(OUTPUT_DIR, "data")
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, os.path.basename(rel))
            shutil.move(filepath, dest)
            # Also extract the video/ texture payload
            extract_tex_file(dest)
            continue

        elif rel.endswith(".json"):
            dest_dir = os.path.join(OUTPUT_DIR, "data")
            os.makedirs(dest_dir, exist_ok=True)
            fname = os.path.basename(rel)
            # Clean up effect json name
            if fname.startswith("_" * 30):
                fname = "effect.json"
            dest = os.path.join(dest_dir, fname)

        elif rel.endswith((".frag", ".vert")):
            dest_dir = os.path.join(OUTPUT_DIR, "shaders")
            os.makedirs(dest_dir, exist_ok=True)
            fname = os.path.basename(rel)
            if fname.startswith("_" * 30):
                fname = "effect" + os.path.splitext(fname)[1]
            dest = os.path.join(dest_dir, fname)

        else:
            dest_dir = os.path.join(OUTPUT_DIR, "data")
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, os.path.basename(rel))

        shutil.move(filepath, dest)

    return extracted


def extract_tex_file(tex_path):
    """Extract TEX file (video or texture)."""
    with open(tex_path, "rb") as f:
        data = f.read()

    meta = probe_tex(data)
    base = os.path.splitext(os.path.basename(tex_path))[0]

    if meta["is_video"]:
        log(tr(f"├─ 检测到视频纹理: {meta['width']}x{meta['height']}",
               f"├─ Video texture detected: {meta['width']}x{meta['height']}"))
        out_dir = os.path.join(OUTPUT_DIR, "video")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "wallpaper_4k.mp4")
        extract_tex(data, out_path)
        log(tr(f"├─ 视频 → outputs/video/wallpaper_4k.mp4",
               f"├─ Video → outputs/video/wallpaper_4k.mp4"))
        log(tr(f"└─ 如需提取帧，请用 ffmpeg：",
               f"└─ To extract a frame, use ffmpeg:"))
        log(f"   ffmpeg -i \"{out_path}\" -ss 0 -vframes 1 frame.png")
    else:
        log(tr(f"├─ 静态纹理: {meta['width']}x{meta['height']}",
               f"├─ Static texture: {meta['width']}x{meta['height']}"))
        out_dir = os.path.join(OUTPUT_DIR, "data")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{base}.dds")
        extract_tex(data, out_path)
        log(tr(f"├─ 纹理 → outputs/data/{base}.dds",
               f"├─ Texture → outputs/data/{base}.dds"))


# ============================================================
# Main
# ============================================================

def run():
    title = tr("Wallpaper Engine 视频音频资源提取器",
               "Wallpaper Engine Media Extractor")
    print("=" * 54)
    print(f"  {title}")
    print("=" * 54)
    print()

    # Check input directory
    if not os.path.isdir(INPUT_DIR):
        log(MSG["no_input"])
        return

    # Recursively scan for .pkg and .tex files
    pkg_files = []
    tex_files = []
    for root, dirs, files in os.walk(INPUT_DIR):
        for f in files:
            path = os.path.join(root, f)
            if f.endswith(".pkg"):
                pkg_files.append(path)
            elif f.endswith(".tex"):
                tex_files.append(path)

    if not pkg_files and not tex_files:
        print(MSG["no_input"])
        return

    log(tr(f"📦 发现 {len(pkg_files)} 个场景包, {len(tex_files)} 个纹理文件",
           f"📦 Found {len(pkg_files)} scene pack(s), {len(tex_files)} texture file(s)"))
    print()

    # Extract PKG files
    for pkg in pkg_files:
        label = tr("📁 处理", "📁 Processing")
        log(f"{label}: {os.path.basename(pkg)}")
        try:
            extract_pkg_file(pkg)
        except Exception as e:
            log(tr(f"  ❌ 提取失败: {e}", f"  ❌ Extraction failed: {e}"))
        print()

    # Extract standalone TEX files
    for tex in tex_files:
        label = tr("📁 处理", "📁 Processing")
        log(f"{label}: {os.path.basename(tex)}")
        try:
            extract_tex_file(tex)
        except Exception as e:
            log(tr(f"  ❌ 提取失败: {e}", f"  ❌ Extraction failed: {e}"))
        print()

    # Cleanup
    if os.path.exists(TEMP_DIR):
        print(MSG["cleanup"])
        shutil.rmtree(TEMP_DIR)

    # Summary
    print("=" * 54)
    print(f"  {tr('✅ 提取完成！', '✅ Extraction complete!')}")
    print()

    if os.path.isdir(OUTPUT_DIR):
        for root, dirs, files in os.walk(OUTPUT_DIR):
            level = root.replace(OUTPUT_DIR, "").count(os.sep)
            indent = "  " * (level + 1)
            for f in sorted(files):
                fp = os.path.join(root, f)
                sz = format_size(os.path.getsize(fp))
                print(f"{indent}{f}  ({sz})")

    print()
    items = [
        ("📂", tr("提取结果保存在 outputs/ 文件夹", "Results saved to outputs/")),
        ("🎵", tr("音频 → outputs/audio/", "Audio → outputs/audio/")),
        ("🎬", tr("视频 → outputs/video/", "Video → outputs/video/")),
        ("📊", tr("数据 → outputs/data/", "Data → outputs/data/")),
        ("🎨", tr("着色器 → outputs/shaders/", "Shaders → outputs/shaders/")),
    ]
    for icon, msg in items:
        log(f"{icon} {msg}")


if __name__ == "__main__":
    run()
