#!/usr/bin/env python3
"""Wallpaper Engine Extractor - Extract assets from Wallpaper Engine scene files.

Usage:
  # Extract a PKG scene file
  python extractor.py pkg scene.pkg -o extracted/

  # Extract a TEX texture file
  python extractor.py tex texture.tex -o output.mp4

  # Show info about a file
  python extractor.py info scene.pkg
"""

import argparse
import os
import sys

from extractor.pkg import extract_pkg, parse_pkg
from extractor.tex import probe_tex, extract_tex
from extractor.utils import format_size


def cmd_pkg(args):
    """Extract a PKG scene file."""
    with open(args.input, "rb") as f:
        data = f.read()

    info = parse_pkg(data)
    print(f"PKG {info['magic']} v{info['version']}: {info['entry_count']} entries")

    extracted = extract_pkg(data, args.output)
    for path, size in extracted:
        rel = os.path.relpath(path, args.output)
        print(f"  ✓ {rel}  ({format_size(size)})")

    print(f"\nExtracted {len(extracted)} files to {args.output}/")


def cmd_tex(args):
    """Extract a TEX texture file."""
    with open(args.input, "rb") as f:
        data = f.read()

    meta = probe_tex(data)
    kind = "video" if meta["is_video"] else "texture"
    print(f"TEX: {meta['width']}x{meta['height']}, {kind}, {format_size(meta['data_size'])}")

    ext = ".mp4" if meta["is_video"] else ".dds"
    out = args.output or (os.path.splitext(args.input)[0] + ext)

    payload = extract_tex(data, out)
    print(f"Extracted {format_size(len(payload))} to {out}")

    if meta["is_video"] and args.extract_frame:
        from extractor.tex import extract_video_frame
        frame_out = os.path.splitext(out)[0] + "_frame.png"
        ok = extract_video_frame(data, frame_out, args.frame_time)
        if ok:
            print(f"Extracted video frame to {frame_out}")
        else:
            print(f"Video saved, but frame extraction requires ffmpeg")


def cmd_info(args):
    """Show info about a file."""
    with open(args.input, "rb") as f:
        data = f.read()

    ext = os.path.splitext(args.input)[1].lower()

    if ext == ".pkg" or data[4:8] == b"PKGV":
        info = parse_pkg(data)
        print(f"Type: Wallpaper Engine Scene Package")
        print(f"Version: {info['version']}")
        print(f"Entries: {info['entry_count']}")
        print(f"\nContents:")
        for e in info["entries"]:
            print(f"  {e['name']}  ({format_size(e['size'])})")

    elif ext == ".tex" or data[:4] == b"TEXV":
        meta = probe_tex(data)
        kind = "video (H.264)" if meta["is_video"] else "compressed texture"
        print(f"Type: Wallpaper Engine Texture (TEXv5)")
        print(f"Format code: {meta['format']}")
        print(f"Dimensions: {meta['width']}x{meta['height']}")
        print(f"Content: {kind}")
        print(f"Data size: {format_size(meta['data_size'])}")

    else:
        print(f"Unknown file type: {ext}")
        print(f"First bytes: {data[:16].hex()}")


def main():
    parser = argparse.ArgumentParser(
        description="Wallpaper Engine Asset Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", help="Command")

    # pkg
    p = sub.add_parser("pkg", help="Extract a .pkg scene file")
    p.add_argument("input", help="Path to scene.pkg")
    p.add_argument("-o", "--output", default="extracted", help="Output directory")
    p.set_defaults(func=cmd_pkg)

    # tex
    p = sub.add_parser("tex", help="Extract a .tex texture file")
    p.add_argument("input", help="Path to .tex file")
    p.add_argument("-o", "--output", help="Output file path")
    p.add_argument("--extract-frame", action="store_true", help="Try to extract first video frame")
    p.add_argument("--frame-time", type=float, default=0.0, help="Frame time in seconds")
    p.set_defaults(func=cmd_tex)

    # info
    p = sub.add_parser("info", help="Show file information")
    p.add_argument("input", help="Path to .pkg or .tex file")
    p.set_defaults(func=cmd_info)

    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
