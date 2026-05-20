"""Utility functions for Wallpaper Engine extraction."""

import os
import json


def ensure_dir(path: str) -> str:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    return path


def save_json(data, filepath: str, **kwargs):
    """Save data as JSON with proper encoding."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, **kwargs)


def load_json(filepath: str) -> dict:
    """Load a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def format_size(size: int) -> str:
    """Format size in bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def safe_filename(name: str) -> str:
    """Sanitize a filename by replacing problematic characters."""
    import re
    # Replace path separators
    name = name.replace("/", "_").replace("\\", "_")
    # Remove or replace other problematic chars
    name = re.sub(r'[<>:"|?*]', "_", name)
    return name.strip()
