"""Wallpaper Engine PKG scene file extractor.

The PKG format (PKGV0022) is a simple archive format:
  [Header]     16 bytes
  [Directory]  N entries with filename + size metadata
  [File Data]  Raw file data concatenated after directory

Header (16 bytes):
  - count_or_flag: uint32 LE (typically 8)
  - magic: 4 bytes "PKGV"
  - version: 4 bytes "0022"
  - entry_count: uint32 LE

Directory Entry (variable):
  - name_len:  uint32 LE
  - name:      UTF-8 string (name_len bytes)
  - padding:   uint32 LE (typically 0)
  - file_size: uint32 LE
"""

import struct
import os
import json


def parse_pkg(data: bytes) -> dict:
    """Parse PKG file and return metadata about its contents."""
    if len(data) < 16:
        raise ValueError("File too small for PKG header")

    magic = data[4:8].decode("ascii", errors="replace")
    version = data[8:12].decode("ascii", errors="replace")
    entry_count = struct.unpack("<I", data[12:16])[0]

    if magic != "PKGV":
        raise ValueError(f"Invalid PKG magic: {magic}")

    info = {"magic": magic, "version": version, "entry_count": entry_count, "entries": []}

    pos = 16
    for _ in range(entry_count):
        if pos + 4 > len(data):
            break

        name_len = struct.unpack("<I", data[pos : pos + 4])[0]
        pos += 4

        if name_len == 0 or name_len > 500:
            break

        name = data[pos : pos + name_len].decode("utf-8", errors="replace").rstrip("\x00")
        pos += name_len

        if pos + 8 > len(data):
            break

        # 4 bytes unknown (padding, typically 0)
        pos += 4

        file_size = struct.unpack("<I", data[pos : pos + 4])[0]
        pos += 4

        info["entries"].append({"name": name, "size": file_size})

    return info


def extract_pkg(data: bytes, output_dir: str) -> list:
    """Extract all files from a PKG archive.

    Returns a list of (filepath, size) tuples for extracted files.
    """
    if len(data) < 16:
        raise ValueError("File too small for PKG header")

    entry_count = struct.unpack("<I", data[12:16])[0]
    os.makedirs(output_dir, exist_ok=True)

    # --- Parse directory ---
    entries = []
    pos = 16

    for _ in range(entry_count):
        if pos + 4 > len(data):
            break

        name_len = struct.unpack("<I", data[pos : pos + 4])[0]
        pos += 4

        if name_len == 0 or name_len > 500:
            break

        name = data[pos : pos + name_len].decode("utf-8", errors="replace").rstrip("\x00")
        pos += name_len

        if pos + 8 > len(data):
            break

        pos += 4  # padding
        file_size = struct.unpack("<I", data[pos : pos + 4])[0]
        pos += 4

        entries.append({"name": name, "size": file_size})

    # --- Extract file data ---
    data_pos = pos
    extracted = []

    for entry in entries:
        file_data = data[data_pos : data_pos + entry["size"]]
        filepath = os.path.join(output_dir, entry["name"])
        filedir = os.path.dirname(filepath)

        os.makedirs(filedir, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(file_data)

        extracted.append((filepath, entry["size"]))
        data_pos += entry["size"]

    # Save manifest
    manifest = [
        {"path": e["name"], "size": e["size"]} for e in entries
    ]
    with open(os.path.join(output_dir, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return extracted


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Wallpaper Engine PKG Extractor")
    parser.add_argument("input", help="Path to scene.pkg file")
    parser.add_argument("-o", "--output", default="extracted", help="Output directory")
    args = parser.parse_args()

    with open(args.input, "rb") as f:
        data = f.read()

    info = parse_pkg(data)
    print(f"PKG v{info['version']}: {info['entry_count']} entries")

    extracted = extract_pkg(data, args.output)
    for path, size in extracted:
        rel = os.path.relpath(path, args.output)
        print(f"  {rel} ({size:,} bytes)")


if __name__ == "__main__":
    main()
