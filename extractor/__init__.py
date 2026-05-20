# Wallpaper Engine Extractor - A tool to extract Wallpaper Engine scene files
from .pkg import extract_pkg
from .tex import extract_tex

__version__ = "1.0.0"
__all__ = ["extract_pkg", "extract_tex"]
