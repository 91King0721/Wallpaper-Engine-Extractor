[English](README.md) | [简体中文](README-CN.md)

---

# Wallpaper Engine 视频音频资源提取器

从 Wallpaper Engine 场景壁纸中提取视频、音频、图片、着色器等资源。

---

## 快速开始

### 准备工作

1. 安装 Python 3.8+（见 DEPENDENCIES.txt）
2. 打开终端执行：

```bash
pip3 install tkinterdnd2
```

3. 从 Releases 下载对应系统的压缩包，解压

### macOS 用户

解压后双击 `Open.command`→ 选择场景文件夹 → 选择输出目录 → 点击「一键提取」。

### Windows 用户

解压后双击 `Open.bat` → 选择场景文件夹 → 选择输出目录 → 点击「一键提取」。

### 手动运行（通用）

```bash
# 克隆或下载本项目后
pip3 install tkinterdnd2           # 安装拖拽支持
python3 gui.py                     # 启动图形界面
```

---

## 使用方法详解

### 1. 选择输入文件夹

点击「选择文件夹」或直接把场景文件夹拖入窗口。程序会自动递归查找其中的 `.pkg` 和 `.tex` 文件。

### 2. 选择输出目录

默认输出到 `outputs/`（项目目录下）。可点击「浏览」修改。

### 3. 开始提取

点击「一键提取」，等待完成。提取结果会分类保存到输出目录中：

```
输出目录/
├── audio/      背景音乐 (MP3)
├── video/      视频纹理 (MP4)
├── data/       场景元数据 (JSON) 和纹理文件 (TEX)
└── shaders/    GLSL 着色器 (frag/vert)
```

### 4. 从视频提取壁纸帧

如果提取出的 `video/` 中有 MP4 文件（60 FPS 动态壁纸常用），需要额外截取一帧：

```bash
ffmpeg -i outputs/video/wallpaper_4k.mp4 -ss 0 -vframes 1 wallpaper.png
```

---

## 项目文件说明

| 文件 | 作用 |
|------|------|
| `gui.py` | 图形界面程序 |
| `run.py` | 命令行一键提取脚本 |
| `extractor.py` | 手动分步提取 CLI |
| `extractor/` | 提取核心模块 |
| `src/` | 发布包中的 Python 源码目录 |
| `Open.command` | macOS 双击启动脚本 |
| `Open.bat` | Windows 双击启动脚本 |
| `build/` | 图标和打包脚本 |
| `input/` | 放入待提取的场景文件 |
| `outputs/` | 提取结果输出目录 |

---

## 常见问题

**Q: 拖拽文件到窗口没反应？**  
A: 请确认已执行 `pip3 install tkinterdnd2`。装好后重启程序即可。

**Q: macOS 提示"无法验证开发者"？**  
A: 右键 → 打开，即可绕过 Gatekeeper 运行。

**Q: Windows 命令行窗口一闪而过？**  
A: 检查 Python 3 是否正确安装并添加到 PATH。

---

## 开源协议

MIT
