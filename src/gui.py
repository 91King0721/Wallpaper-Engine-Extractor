#!/usr/bin/env python3
"""Wallpaper Engine Media Extractor — GUI

Cross-platform GUI with drag-and-drop support.
Requires: pip install tkinterdnd2  (for drag-and-drop)
          tkinter (built-in with Python)
"""

import os
import sys
import shutil
import json
import threading
import queue
import locale
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

# Drag-and-drop support (optional)
_HAS_DND = False
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    _HAS_DND = True
except ImportError:
    TkinterDnD = None
    DND_FILES = None

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))
from extractor.pkg import extract_pkg
from extractor.tex import probe_tex, extract_tex
from extractor.utils import format_size


# ============================================================
# Language
# ============================================================
def detect_lang():
    lang = "en"
    try:
        locale.setlocale(locale.LC_ALL, "")
        lc = locale.getlocale()
        if lc and lc[0] and lc[0].startswith("zh"):
            lang = "zh"
    except Exception:
        pass
    env = os.environ.get("LANG", "")
    if env.startswith("zh"):
        lang = "zh"
    return lang


LANG = {
    "zh": {
        "title": "Wallpaper Engine 资源提取器",
        "subtitle": "从 Wallpaper Engine 场景中提取视频、音频资源",
        "drop_hint": "拖放场景文件夹到此处",
        "drop_hint_drag": "松开以选择此文件夹",
        "drop_or": "或",
        "select_btn": "\U0001f4c2  选择文件夹",
        "paste_btn": "\U0001f4cb  粘贴路径",
        "run_btn": "\U0001f680  一键提取",
        "cancel_btn": "\u23f9  取消",
        "selected": "已选择: {}",
        "no_selection": "尚未选择文件夹",
        "processing": "正在提取，请稍候...",
        "done": "\u2705 提取完成！",
        "failed": "\u274c 提取失败",
        "no_pkg": "未找到 .pkg 或 .tex 文件",
        "log_header": "执行日志",
        "lang_tip": "切换语言",
        "theme_tip": "切换主题",
        "outputs_audio": "音频文件",
        "outputs_video": "视频文件",
        "outputs_data": "数据文件",
        "outputs_shaders": "着色器文件",
        "python_err": "需要 Python 3.8+",
        "settings": "设置",
        "dark": "深色",
        "light": "浅色",
        "clear_log": "清空日志",
"open_outputs": "\U0001f4c2  打开输出文件夹",
        "output_path": "输出到:",
        "output_browse": "\U0001f4c2  浏览",
        "output_default": "outputs/（项目目录）",
        "dnd_notice": "\u2139\ufe0f 可将文件夹拖到窗口上直接选择",
        "dnd_unsupported": "拖拽不可用（需 tkinterdnd2）",
    },
    "en": {
        "title": "Wallpaper Engine Media Extractor",
        "subtitle": "Extract video and audio from Wallpaper Engine scenes",
        "drop_hint": "Drop scene folder here",
        "drop_hint_drag": "Release to select this folder",
        "drop_or": "or",
        "select_btn": "\U0001f4c2  Select Folder",
        "paste_btn": "\U0001f4cb  Paste Path",
        "run_btn": "\U0001f680  Extract",
        "cancel_btn": "\u23f9  Cancel",
        "selected": "Selected: {}",
        "no_selection": "No folder selected",
        "processing": "Extracting, please wait...",
        "done": "\u2705 Extraction complete!",
        "failed": "\u274c Extraction failed",
        "no_pkg": "No .pkg or .tex files found",
        "log_header": "Execution Log",
        "lang_tip": "Switch language",
        "theme_tip": "Toggle theme",
        "outputs_audio": "Audio files",
        "outputs_video": "Video files",
        "outputs_data": "Data files",
        "outputs_shaders": "Shader files",
        "python_err": "Python 3.8+ required",
        "settings": "Settings",
        "dark": "Dark",
        "light": "Light",
        "clear_log": "Clear log",
"open_outputs": "\U0001f4c2  Open output folder",
        "output_path": "Output to:",
        "output_browse": "\U0001f4c2  Browse",
        "output_default": "outputs/ (project folder)",
        "dnd_notice": "\u2139\ufe0f Drag a folder onto the window to select",
        "dnd_unsupported": "Drag & drop unavailable (tkinterdnd2 required)",
    },
}


# ============================================================
# Modern Flat Theme
# ============================================================
class Theme:
    def __init__(self, dark=True):
        self.dark = dark
        self.update()

    def toggle(self):
        self.dark = not self.dark
        self.update()
        return self.dark

    def update(self):
        if self.dark:
            self.bg = "#1a1a2e"
            self.bg2 = "#16213e"
            self.bg3 = "#0f3460"
            self.card = "#1e2a4a"
            self.card_border = "#2a3f6a"
            self.accent = "#e94560"
            self.accent2 = "#0f7b6e"
            self.text = "#e8e8e8"
            self.text2 = "#a0a0b0"
            self.text3 = "#606080"
            self.success = "#2ecc71"
            self.error = "#e74c3c"
            self.warning = "#f39c12"
            self.input_bg = "#0d1b2a"
            self.hover_card = "#243b6a"
            self.scroll_bg = "#1a1a2e"
            self.scroll_fg = "#2a3f6a"
        else:
            self.bg = "#f0f2f5"
            self.bg2 = "#ffffff"
            self.bg3 = "#e8ecf0"
            self.bg3 = "#e8ecf0"
            self.card = "#ffffff"
            self.card_border = "#d0d5dd"
            self.accent = "#e94560"
            self.accent2 = "#0f7b6e"
            self.text = "#1a1a2e"
            self.text2 = "#555570"
            self.text3 = "#9090a0"
            self.success = "#27ae60"
            self.error = "#e74c3c"
            self.warning = "#f39c12"
            self.input_bg = "#f5f7fa"
            self.hover_card = "#e8ecf0"
            self.scroll_bg = "#f0f2f5"
            self.scroll_fg = "#d0d5dd"


# ============================================================
# Scrollable Frame
# ============================================================
class ScrollFrame(tk.Frame):
    def __init__(self, parent, theme, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.theme = theme

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                bg=theme.input_bg)
        self.vsb = tk.Scrollbar(self, orient="vertical",
                                command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=theme.input_bg)

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.inner, anchor="nw",
                                  width=self.canvas.winfo_reqwidth)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(1, width=event.width)


# ============================================================
# Main GUI Application
# ============================================================
class App:
    def __init__(self):
        self.lang_code = detect_lang()
        self.T = LANG[self.lang_code]
        self.theme = Theme(dark=True)

        # Use TkinterDnD.Tk if available, otherwise fall back to tk.Tk
        if _HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("Wallpaper Engine Media Extractor")
        self.root.geometry("720x800")
        self.root.minsize(600, 650)

        # Center on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 720) // 2
        y = (sh - 800) // 2
        self.root.geometry(f"720x800+{x}+{y}")

        self.input_path = None
        self.output_dir = os.path.join(BASE_DIR, "outputs")
        self.running = False
        self.log_queue = queue.Queue()

        self._build_ui()
        self._apply_theme()
        self._poll_log()

        # Register drag-and-drop on the root window
        if _HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind("<<Drop>>", self._on_drop)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ============================================================
    # UI Build
    # ============================================================
    def _build_ui(self):
        self.root.configure(bg=self.theme.bg)

        # Main container
        self.main = tk.Frame(self.root, bg=self.theme.bg)
        self.main.pack(fill="both", expand=True, padx=20, pady=16)

        # -- Header --
        self.header = tk.Frame(self.main, bg=self.theme.bg)
        self.header.pack(fill="x", pady=(0, 10))

        self.title_lbl = tk.Label(
            self.header,
            text=self.T["title"],
            font=("Helvetica", 18, "bold"),
            bg=self.theme.bg, fg=self.theme.text, anchor="w"
        )
        self.title_lbl.pack(side="left")

        # Controls in header
        self.ctrl_frame = tk.Frame(self.header, bg=self.theme.bg)
        self.ctrl_frame.pack(side="right")

        self.lang_btn = tk.Label(
            self.ctrl_frame, text="\U0001f310", font=("Helvetica", 12),
            bg=self.theme.bg, fg=self.theme.text2, cursor="hand2"
        )
        self.lang_btn.pack(side="left", padx=(0, 4))
        self.lang_btn.bind("<Button-1>", lambda e: self._toggle_lang())

        self.theme_btn = tk.Label(
            self.ctrl_frame, text="\u2600\ufe0f", font=("Helvetica", 12),
            bg=self.theme.bg, fg=self.theme.text2, cursor="hand2"
        )
        self.theme_btn.pack(side="left")
        self.theme_btn.bind("<Button-1>", lambda e: self._toggle_theme())

        # Subtitle
        self.sub_lbl = tk.Label(
            self.main, text=self.T["subtitle"],
            font=("Helvetica", 10),
            bg=self.theme.bg, fg=self.theme.text2, anchor="w"
        )
        self.sub_lbl.pack(fill="x", pady=(0, 12))

        # -- Drop Zone (the main drag target) --
        self.drop_frame = tk.Frame(
            self.main, bg=self.theme.card,
            highlightbackground=self.theme.card_border,
            highlightthickness=2, padx=20, pady=16
        )
        self.drop_frame.pack(fill="x", pady=(0, 10))

        # Make the drop zone register for DnD too
        if _HAS_DND:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind("<<Drop>>", self._on_drop)
            self.drop_frame.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            self.drop_frame.dnd_bind("<<DragLeave>>", self._on_drag_leave)
            self.drop_frame.dnd_bind("<<DragPos>>", self._on_drag_pos)

        self.drop_inner = tk.Frame(self.drop_frame, bg=self.theme.card)
        self.drop_inner.pack(pady=16)

        self.drop_icon = tk.Label(
            self.drop_inner, text="\U0001f4c1", font=("Helvetica", 32),
            bg=self.theme.card, fg=self.theme.text3
        )
        self.drop_icon.pack()

        self.drop_lbl = tk.Label(
            self.drop_inner, text=self.T["drop_hint"],
            font=("Helvetica", 11),
            bg=self.theme.card, fg=self.theme.text2
        )
        self.drop_lbl.pack(pady=(4, 2))

        # DnD availability notice
        dnd_text = self.T["dnd_notice"] if _HAS_DND else self.T["dnd_unsupported"]
        self.dnd_notice = tk.Label(
            self.drop_inner, text=dnd_text,
            font=("Helvetica", 8),
            bg=self.theme.card, fg=self.theme.text3
        )
        self.dnd_notice.pack(pady=(0, 6))

        # Drop zone divider
        divider = tk.Frame(self.drop_inner, bg=self.theme.card_border,
                           height=1)
        divider.pack(fill="x", padx=40, pady=(0, 6))

        # Selection buttons row
        self.btn_row = tk.Frame(self.drop_inner, bg=self.theme.card)
        self.btn_row.pack()

        self.select_btn = tk.Label(
            self.btn_row, text=self.T["select_btn"],
            font=("Helvetica", 10, "bold"),
            bg=self.theme.accent, fg="white", padx=14, pady=6,
            cursor="hand2"
        )
        self.select_btn.pack(side="left", padx=(0, 6))
        self.select_btn.bind("<Button-1>", lambda e: self._select_folder())

        self.paste_btn = tk.Label(
            self.btn_row, text=self.T["paste_btn"],
            font=("Helvetica", 10),
            bg=self.theme.bg3, fg=self.theme.text, padx=10, pady=6,
            cursor="hand2"
        )
        self.paste_btn.pack(side="left")
        self.paste_btn.bind("<Button-1>", lambda e: self._paste_path())

        # -- Selected path display --
        self.path_frame = tk.Frame(self.main, bg=self.theme.bg)
        self.path_frame.pack(fill="x", pady=(0, 4))

        self.path_lbl = tk.Label(
            self.path_frame, text=self.T["no_selection"],
            font=("Helvetica", 9), anchor="w",
            bg=self.theme.bg, fg=self.theme.text3, wraplength=680
        )
        self.path_lbl.pack(fill="x")

        # -- Output path row --
        self.output_frame = tk.Frame(self.main, bg=self.theme.bg)
        self.output_frame.pack(fill="x", pady=(0, 10))

        self.output_label = tk.Label(
            self.output_frame, text=self.T["output_path"],
            font=("Helvetica", 9),
            bg=self.theme.bg, fg=self.theme.text2
        )
        self.output_label.pack(side="left")

        self.output_lbl = tk.Label(
            self.output_frame,
            text=self.T["output_default"],
            font=("Helvetica", 9), anchor="w",
            bg=self.theme.bg, fg=self.theme.text3, wraplength=500
        )
        self.output_lbl.pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.output_browse_btn = tk.Label(
            self.output_frame, text=self.T["output_browse"],
            font=("Helvetica", 9),
            bg=self.theme.bg3, fg=self.theme.text, padx=8, pady=2,
            cursor="hand2"
        )
        self.output_browse_btn.pack(side="right")
        self.output_browse_btn.bind("<Button-1>", lambda e: self._select_output())

        # -- Action buttons row --
        self.action_frame = tk.Frame(self.main, bg=self.theme.bg)
        self.action_frame.pack(fill="x", pady=(0, 10))

        self.run_btn = tk.Label(
            self.action_frame, text=self.T["run_btn"],
            font=("Helvetica", 12, "bold"),
            bg=self.theme.accent2, fg="white",
            padx=24, pady=8, cursor="hand2"
        )
        self.run_btn.pack(side="left")

        # Open outputs button (disabled until extraction done)
        self.open_btn = tk.Label(
            self.action_frame, text=self.T["open_outputs"],
            font=("Helvetica", 10),
            bg=self.theme.bg3, fg=self.theme.text2,
            padx=12, pady=8, cursor="hand2"
        )
        self.open_btn.pack(side="right")

        self.open_btn.bind("<Button-1>", lambda e: self._open_outputs())
        self.run_btn.bind("<Button-1>", lambda e: self._run_extraction())

        # -- Log output --
        log_header_frame = tk.Frame(self.main, bg=self.theme.bg)
        log_header_frame.pack(fill="x", pady=(0, 4))

        self.log_header = tk.Label(
            log_header_frame,
            text=f"  {self.T['log_header']}",
            font=("Helvetica", 10),
            bg=self.theme.bg, fg=self.theme.text2, anchor="w"
        )
        self.log_header.pack(side="left", fill="x", expand=True)

        self.clear_log_btn = tk.Label(
            log_header_frame, text=self.T["clear_log"],
            font=("Helvetica", 8),
            bg=self.theme.bg, fg=self.theme.text3, cursor="hand2"
        )
        self.clear_log_btn.pack(side="right")
        self.clear_log_btn.bind("<Button-1>", lambda e: self._clear_log())

        # Log text widget
        self.log_frame = tk.Frame(
            self.main, bg=self.theme.input_bg,
            highlightbackground=self.theme.card_border,
            highlightthickness=1
        )
        self.log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            self.log_frame,
            font=("Menlo", 9),
            bg=self.theme.input_bg, fg=self.theme.text,
            insertbackground=self.theme.text,
            relief="flat", padx=10, pady=10,
            state="disabled", wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, side="left")

        self.scrollbar = tk.Scrollbar(self.log_frame,
                                       command=self.log_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=self.scrollbar.set)

        # Bind hover effects
        for widget in [self.run_btn, self.select_btn]:
            widget.bind("<Enter>", lambda e, w=widget: self._on_hover(w, True))
            widget.bind("<Leave>", lambda e, w=widget: self._on_hover(w, False))

    # ============================================================
    # Drag & Drop Handlers
    # ============================================================
    def _on_drop(self, event):
        """Handle file/folder drop."""
        # tkinterdnd2 returns paths with {} wrapping and spaces escaped
        raw = event.data
        # Clean the path: remove curly braces, unescape
        path = raw.strip().lstrip("{").rstrip("}")
        # tkinterdnd2 may return multiple files separated by space
        # Take the first one (most likely a folder)
        if " " in path and not path.startswith("/"):
            # Could be multiple files with space-separated paths
            paths = path.split("} {")
            path = paths[0].lstrip("{").rstrip("}")
        if path:
            self._set_path(path)
        # Reset drop zone styling
        self._on_drag_leave(None)

    def _on_drag_enter(self, event):
        """Highlight the drop zone on drag enter."""
        self.drop_frame.configure(bg=self.theme.hover_card,
                                   highlightbackground=self.theme.accent)
        self.drop_inner.configure(bg=self.theme.hover_card)
        for child in self.drop_inner.winfo_children():
            try:
                child.configure(bg=self.theme.hover_card)
            except:
                pass
        self.drop_lbl.configure(text=self.T["drop_hint_drag"])

    def _on_drag_leave(self, event):
        """Reset drop zone styling."""
        self.drop_frame.configure(bg=self.theme.card,
                                   highlightbackground=self.theme.card_border)
        self.drop_inner.configure(bg=self.theme.card)
        for child in self.drop_inner.winfo_children():
            try:
                child.configure(bg=self.theme.card)
            except:
                pass
        self.drop_lbl.configure(text=self.T["drop_hint"])

    def _on_drag_pos(self, event):
        """Required for tkinterdnd2 DragPos events."""
        pass

    def _set_path(self, path):
        """Set the input path and update UI."""
        path = path.strip()
        if os.path.isdir(path):
            self.input_path = path
            self.path_lbl.configure(
                text=self.T["selected"].format(path),
                fg=self.theme.text2
            )
            self._log(f"\U0001f4c2 {path}", "info")
        elif os.path.isfile(path):
            # Use the parent directory
            folder = os.path.dirname(path)
            self.input_path = folder
            self.path_lbl.configure(
                text=self.T["selected"].format(folder),
                fg=self.theme.text2
            )
            self._log(f"\U0001f4c2 {folder}", "info")

    # ============================================================
    # Theme & Language
    # ============================================================
    def _apply_theme(self):
        bg = self.theme.bg
        self.root.configure(bg=bg)
        self.main.configure(bg=bg)
        self.header.configure(bg=bg)
        self.title_lbl.configure(bg=bg, fg=self.theme.text)
        self.ctrl_frame.configure(bg=bg)
        self.lang_btn.configure(bg=bg, fg=self.theme.text2)
        self.theme_btn.configure(bg=bg, fg=self.theme.text2)
        self.sub_lbl.configure(bg=bg, fg=self.theme.text2)
        self.path_frame.configure(bg=bg)
        self.path_lbl.configure(bg=bg, fg=self.theme.text3)
        self.output_frame.configure(bg=bg)
        self.output_label.configure(bg=bg, fg=self.theme.text2)
        self.output_lbl.configure(bg=bg, fg=self.theme.text3)
        self.output_browse_btn.configure(bg=self.theme.bg3, fg=self.theme.text)
        self.action_frame.configure(bg=bg)
        self.run_btn.configure(bg=self.theme.accent2)
        self.open_btn.configure(bg=self.theme.bg3, fg=self.theme.text2)
        self.log_header.configure(bg=bg, fg=self.theme.text2)
        self.clear_log_btn.configure(bg=bg, fg=self.theme.text3)
        log_header_frame = self.log_header.master
        log_header_frame.configure(bg=bg)

        self.drop_frame.configure(bg=self.theme.card,
            highlightbackground=self.theme.card_border)
        self.drop_inner.configure(bg=self.theme.card)
        self.drop_icon.configure(bg=self.theme.card, fg=self.theme.text3)
        self.drop_lbl.configure(bg=self.theme.card, fg=self.theme.text2)
        self.dnd_notice.configure(bg=self.theme.card, fg=self.theme.text3)
        self.btn_row.configure(bg=self.theme.card)
        self.select_btn.configure(bg=self.theme.accent)
        self.paste_btn.configure(bg=self.theme.bg3, fg=self.theme.text)

        self.log_frame.configure(bg=self.theme.input_bg,
            highlightbackground=self.theme.card_border)
        self.log_text.configure(bg=self.theme.input_bg, fg=self.theme.text,
            insertbackground=self.theme.text)
        self.scrollbar.configure(bg=self.theme.scroll_bg,
                                 troughcolor=self.theme.scroll_bg)

        self.theme_btn.configure(text="\U0001f319" if self.theme.dark else "\u2600\ufe0f")

    def _toggle_theme(self):
        self.theme.toggle()
        self._apply_theme()

    def _toggle_lang(self):
        self.lang_code = "en" if self.lang_code == "zh" else "zh"
        self.T = LANG[self.lang_code]
        self._refresh_texts()

    def _refresh_texts(self):
        self.title_lbl.configure(text=self.T["title"])
        self.sub_lbl.configure(text=self.T["subtitle"])
        self.drop_lbl.configure(text=self.T["drop_hint"])
        dnd_text = self.T["dnd_notice"] if _HAS_DND else self.T["dnd_unsupported"]
        self.dnd_notice.configure(text=dnd_text)
        self.select_btn.configure(text=self.T["select_btn"])
        self.paste_btn.configure(text=self.T["paste_btn"])
        self.run_btn.configure(text=self.T["run_btn"] if not self.running
                               else self.T["cancel_btn"])
        self.open_btn.configure(text=self.T["open_outputs"])
        self.output_label.configure(text=self.T["output_path"])
        self.output_browse_btn.configure(text=self.T["output_browse"])
        if self.output_dir == os.path.join(BASE_DIR, "outputs"):
            self.output_lbl.configure(text=self.T["output_default"])
        elif self.output_dir:
            self.output_lbl.configure(text=self.output_dir)
        self.log_header.configure(text=f"  {self.T['log_header']}")
        self.clear_log_btn.configure(text=self.T["clear_log"])
        if self.input_path:
            self.path_lbl.configure(text=self.T["selected"].format(self.input_path))
        else:
            self.path_lbl.configure(text=self.T["no_selection"])

    # ============================================================
    # File Selection
    # ============================================================
    def _select_folder(self):
        folder = filedialog.askdirectory(
            title=self.T["select_btn"].replace("\U0001f4c2  ", "")
        )
        if folder:
            self._set_path(folder)

    def _paste_path(self):
        """Paste a path from the clipboard."""
        try:
            path = self.root.clipboard_get().strip()
            if path and os.path.exists(path):
                self._set_path(path)
            elif path:
                self._log(f"\u26a0 {self.T['no_selection']}: {path}", "warn")
        except tk.TclError:
            self._log(f"\u26a0 {self.T['no_selection']}", "warn")

    # ============================================================
    # Extraction Logic
    # ============================================================
    def _log(self, msg, level="info"):
        colors = {"info": self.theme.text, "ok": self.theme.success,
                  "err": self.theme.error, "warn": self.theme.warning,
                  "title": self.theme.accent2}
        c = colors.get(level, self.theme.text)
        self.log_queue.put((msg, c))

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _poll_log(self):
        try:
            while True:
                msg, color = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", msg + "\n")
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(50, self._poll_log)

    def _select_output(self):
        """Select output folder."""
        folder = filedialog.askdirectory(
            title="Select output folder"
        )
        if folder:
            self.output_dir = folder
            self.output_lbl.configure(
                text=folder,
                fg=self.theme.text2
            )

    def _run_extraction(self):
        if self.running:
            return
        if not self.input_path:
            self._log(self.T["no_selection"], "warn")
            return

        self.running = True
        self.run_btn.configure(text=self.T["cancel_btn"], bg=self.theme.error)
        self._clear_log()

        self._log(f"{'='*40}", "title")
        self._log(f"  {self.T['title']}", "title")
        self._log(f"{'='*40}", "title")

        thread = threading.Thread(target=self._do_extract, daemon=True)
        thread.start()

    def _do_extract(self):
        input_dir = self.input_path
        temp_dir = os.path.join(input_dir, "_temp_extract")
        # Clear the output dir if it exists from a previous run
        if os.path.exists(self.output_dir):
            # Don't delete - just use it. Previous contents stay.
            pass

        self._log(f"\U0001f4c2 {input_dir}", "info")

        # Scan recursively for .pkg and .tex files
        pkg_files = []
        tex_files = []
        for root, dirs, files in os.walk(input_dir):
            # Skip hidden dirs and our own output
            dirs[:] = [d for d in dirs if not d.startswith("_") and not d.startswith(".")]
            for f in files:
                path = os.path.join(root, f)
                if f.endswith(".pkg"):
                    pkg_files.append(path)
                elif f.endswith(".tex"):
                    tex_files.append(path)

        if not pkg_files and not tex_files:
            self._log(f"\u274c {self.T['no_pkg']}", "err")
            # Try to help user - list files found
            all_files = []
            for root, dirs, files in os.walk(input_dir):
                for f in files:
                    all_files.append(f)
            if all_files:
                self._log(f"  {'发现以下文件:' if self.lang_code == 'zh' else 'Files found:'}", "info")
                for f in all_files[:10]:
                    self._log(f"    {f}", "info")
            self._finish(False)
            return

        self._log(
            f"\U0001f4e6 {len(pkg_files)} PKG, {len(tex_files)} TEX",
            "ok"
        )

        # Extract PKG files
        for pkg in pkg_files:
            name = os.path.basename(pkg)
            self._log(f"  [{name}]", "info")
            try:
                with open(pkg, "rb") as f:
                    data = f.read()
                extracted = extract_pkg(data, temp_dir)
                self._organize(extracted, temp_dir, self.output_dir)
            except Exception as e:
                self._log(f"  \u274c {e}", "err")

        # Extract standalone TEX files
        for tex in tex_files:
            name = os.path.basename(tex)
            self._log(f"  [{name}]", "info")
            try:
                with open(tex, "rb") as f:
                    data = f.read()
                meta = probe_tex(data)
                if meta["is_video"]:
                    out_dir = os.path.join(self.output_dir, "video")
                    os.makedirs(out_dir, exist_ok=True)
                    out_path = os.path.join(out_dir, "wallpaper_4k.mp4")
                    extract_tex(data, out_path)
                    sz = format_size(os.path.getsize(out_path))
                    lbl = self.lang_code
                    self._log(
                        f"  \U0001f3ac {'视频' if lbl == 'zh' else 'Video'}: wallpaper_4k.mp4 ({sz})",
                        "ok"
                    )
                else:
                    out_dir = os.path.join(self.output_dir, "data")
                    os.makedirs(out_dir, exist_ok=True)
                    base = os.path.splitext(name)[0]
                    out_path = os.path.join(out_dir, f"{base}.dds")
                    extract_tex(data, out_path)
                    self._log(f"  \U0001f5bc {'纹理' if self.lang_code == 'zh' else 'Texture'}: {base}.dds", "ok")
            except Exception as e:
                self._log(f"  \u274c {e}", "err")

        # Cleanup temp
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        # Summary
        self._log("", "info")
        self._log("\u2501" * 40, "title")
        if os.path.isdir(self.output_dir):
            total = sum(len(files) for _, _, files in os.walk(self.output_dir))
            self._log(f"\u2705 {self.T['done']} ({total} {'files' if self.lang_code == 'en' else '个文件'})", "ok")
            self._log(f"\U0001f4c2 {self.output_dir}", "info")
            for root, dirs, files in os.walk(self.output_dir):
                for f in sorted(files):
                    fp = os.path.join(root, f)
                    sz = format_size(os.path.getsize(fp))
                    icon = "\U0001f3b5" if f.endswith(".mp3") else \
                           "\U0001f3ac" if f.endswith(".mp4") else \
                           "\U0001f4c4"
                    self._log(f"  {icon} {f}  ({sz})", "info")
        else:
            self._log(f"\u274c {self.T['failed']}", "err")

        self._finish(True)

    def _organize(self, extracted, temp_dir, output_dir):
        for filepath, size in extracted:
            rel = os.path.relpath(filepath, temp_dir)
            try:
                if rel.endswith(".mp3"):
                    d = os.path.join(output_dir, "audio")
                    os.makedirs(d, exist_ok=True)
                    base = os.path.basename(rel)
                    if "LOST BLESS" in base:
                        base = "track_01.mp3"
                    elif "nayuta" in base:
                        base = "track_02.mp3"
                    shutil.move(filepath, os.path.join(d, base))
                    lbl = self.lang_code
                    self._log(f"  \U0001f3b5 {base}  ({format_size(size)})", "ok")

                elif rel.endswith(".tex"):
                    d = os.path.join(output_dir, "data")
                    os.makedirs(d, exist_ok=True)
                    dest = os.path.join(d, os.path.basename(rel))
                    shutil.move(filepath, dest)
                    self._extract_tex_inline(dest, output_dir)

                elif rel.endswith(".json"):
                    d = os.path.join(output_dir, "data")
                    os.makedirs(d, exist_ok=True)
                    fname = os.path.basename(rel)
                    if fname.startswith("_" * 30):
                        fname = "effect.json"
                    shutil.move(filepath, os.path.join(d, fname))

                elif rel.endswith((".frag", ".vert")):
                    d = os.path.join(output_dir, "shaders")
                    os.makedirs(d, exist_ok=True)
                    fname = os.path.basename(rel)
                    if fname.startswith("_" * 30):
                        fname = "effect" + os.path.splitext(fname)[1]
                    shutil.move(filepath, os.path.join(d, fname))

                else:
                    d = os.path.join(output_dir, "data")
                    os.makedirs(d, exist_ok=True)
                    shutil.move(filepath, os.path.join(d, os.path.basename(rel)))
            except Exception as e:
                self._log(f"    \u26a0 {e}", "warn")

    def _extract_tex_inline(self, tex_path, output_dir):
        try:
            with open(tex_path, "rb") as f:
                data = f.read()
            meta = probe_tex(data)
            if meta["is_video"]:
                out_dir = os.path.join(output_dir, "video")
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, "wallpaper_4k.mp4")
                extract_tex(data, out_path)
                sz = format_size(os.path.getsize(out_path))
                self._log(f"  \U0001f3ac wallpaper_4k.mp4  ({sz})", "ok")
        except Exception:
            pass

    def _open_outputs(self):
        if self.output_dir and os.path.isdir(self.output_dir):
            import subprocess
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", self.output_dir])
                elif sys.platform == "win32":
                    os.startfile(self.output_dir)
                else:
                    subprocess.run(["xdg-open", self.output_dir])
            except Exception as e:
                self._log(f"\u26a0 {e}", "warn")
        else:
            # Open the project's outputs folder as fallback
            outputs_path = os.path.join(BASE_DIR, "outputs")
            if os.path.isdir(outputs_path):
                import subprocess
                try:
                    if sys.platform == "darwin":
                        subprocess.run(["open", outputs_path])
                    elif sys.platform == "win32":
                        os.startfile(outputs_path)
                    else:
                        subprocess.run(["xdg-open", outputs_path])
                except Exception:
                    pass

    def _finish(self, success):
        self.running = False
        self.run_btn.configure(
            text=self.T["run_btn"],
            bg=self.theme.accent2
        )

    def _on_close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
