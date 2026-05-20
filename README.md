[简体中文](README-CN.md) | [English](README.md)

---

# Wallpaper Engine Media Extractor

Extract videos, audio, images, and shaders from Wallpaper Engine scene wallpapers.

---

## Quick Start

### Prerequisites

1. Install Python 3.8+ (see DEPENDENCIES.txt)
2. Open terminal and run:

```bash
pip3 install tkinterdnd2
```

3. Download the release zip for your platform from Releases page, unzip

### macOS

Double-click `WallpaperEngineExtractor.app`. Select scene folder → choose output folder → click "Extract".

### Windows

Double-click `WallpaperEngineExtractor.bat`. Select scene folder → choose output folder → click "Extract".

### Run Manually

```bash
# After cloning or downloading
pip3 install tkinterdnd2           # Install drag-and-drop support
python3 gui.py                     # Launch GUI
```

---

## Usage Guide

### 1. Select Input Folder

Click "Select Folder" or drag a scene folder onto the window. The program will recursively scan for `.pkg` and `.tex` files.

### 2. Choose Output Directory

Default output is `outputs/` (project directory). Click "Browse" to change.

### 3. Extract

Click "Extract" and wait. Results are organized into:

```
output_dir/
├── audio/      Background music (MP3)
├── video/      Video textures (MP4)
├── data/       Scene metadata (JSON) and textures (TEX)
└── shaders/    GLSL shaders (frag/vert)
```

### 4. Extract Wallpaper Frame from Video

If `video/` contains an MP4 file (common for 60 FPS animated wallpapers):

```bash
ffmpeg -i outputs/video/wallpaper_4k.mp4 -ss 0 -vframes 1 wallpaper.png
```

---

## Project Files

| File | Purpose |
|------|---------|
| `gui.py` | GUI application (main entry) |
| `run.py` | CLI one-click extraction |
| `extractor.py` | Manual extraction CLI |
| `extractor/` | Core extraction modules |
| `dist/` | Release packages (.app / .bat) |
| `build/` | Icons and packaging scripts |
| `input/` | Place scene files here |
| `outputs/` | Extraction results |

---

## FAQ

**Q: Drag and drop doesn't work?**  
A: Run `pip3 install tkinterdnd2` and restart the app.

**Q: macOS "Cannot verify developer" warning?**  
A: Right-click → Open to bypass Gatekeeper.

**Q: Windows CMD window closes immediately?**  
A: Make sure Python 3 is installed and added to PATH.

---

## License

MIT
