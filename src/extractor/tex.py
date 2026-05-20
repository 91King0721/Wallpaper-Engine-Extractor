"""Wallpaper Engine TEX texture file parser.

The TEXv5 format stores textures which can be:
  1. Compressed GPU textures (DXT/BCn formats)
  2. Video textures (H.264/H.265 in MP4/ISOBMFF container)
  3. Other pixel formats

Structure:
  TEXV0005\x00      (9 bytes - magic + version + null)
  TEXI0001\x00      (9 bytes - info chunk header)
  [Info data]       (format, flags, width, height)
  TEXB0003\x00      (10 bytes - TEXB v3 data chunk header)
  [Sub-header]      (8 bytes metadata for v3)
  [Raw data]        (compressed texture or MP4 data)

  TEXB0004\x00      (10 bytes - TEXB v4 data chunk header)
  [Sub-header]      (44 bytes metadata for v4)
  [Raw data]
"""

import struct
import os


def _find_texb(data: bytes) -> int:
    """Find TEXB chunk starting position (TEXB0003 or TEXB0004)."""
    pos = data.find(b"TEXB0003")
    if pos >= 0:
        return pos
    pos = data.find(b"TEXB0004")
    if pos >= 0:
        return pos
    return -1


def _texb_data_start(tex_b: int, data: bytes) -> int:
    """Compute the start offset of raw data after the TEXB chunk header."""
    start = tex_b + 8  # past "TEXB0003" or "TEXB0004"
    if start < len(data) and data[start] == 0:
        start += 1
    # TEXB0003 has additional 8-byte sub-header after null terminator
    ver = data[tex_b : tex_b + 9]
    if ver.startswith(b"TEXB0003"):
        start += 8  # skip 8-byte sub-header
    return start


def probe_tex(data: bytes) -> dict:
    """Read TEX metadata without extracting the full payload."""
    if not data.startswith(b"TEXV0005\x00"):
        raise ValueError("Not a TEXv5 file")

    # Find TEXI (info) chunk
    tex_i = data.find(b"TEXI0001\x00")
    if tex_i < 0:
        raise ValueError("Missing TEXI0001 chunk")

    info_start = tex_i + 9
    if info_start + 16 > len(data):
        raise ValueError("Truncated TEXI data")

    tex_format = struct.unpack_from("<I", data, info_start + 4)[0]
    width = struct.unpack_from("<I", data, info_start + 8)[0]
    height = struct.unpack_from("<I", data, info_start + 12)[0]

    tex_b = _find_texb(data)
    if tex_b < 0:
        raise ValueError("Missing TEXB chunk")

    data_start = _texb_data_start(tex_b, data)
    chunk_data = data[data_start:]
    data_size = len(chunk_data)

    is_video = b"ftyp" in chunk_data and b"moov" in chunk_data

    return {
        "format": tex_format,
        "width": width,
        "height": height,
        "data_size": data_size,
        "is_video": is_video,
    }


def extract_tex(data: bytes, output_path: str = None) -> bytes:
    """Extract the raw payload (MP4 or texture data) from a TEX file."""
    if not data.startswith(b"TEXV0005\x00"):
        raise ValueError("Not a TEXv5 file")

    tex_b = _find_texb(data)
    if tex_b < 0:
        raise ValueError("Missing TEXB chunk")

    data_start = _texb_data_start(tex_b, data)
    chunk_data = data[data_start:]

    # For video textures, find the ftyp box
    if chunk_data.find(b"ftyp") >= 0:
        ftyp_offset = chunk_data.find(b"ftyp")
        if ftyp_offset >= 4:
            mp4_start = ftyp_offset - 4
            payload = chunk_data[mp4_start:]
        else:
            payload = chunk_data
    else:
        payload = chunk_data

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(payload)

    return payload


def extract_video_frame(tex_data: bytes, output_path: str, time_sec: float = 0.0) -> bool:
    import subprocess, shutil, tempfile
    tmp_mp4 = os.path.join(os.path.dirname(output_path), "_temp_video.mp4")
    payload = extract_tex(tex_data, tmp_mp4)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        cmd = [ffmpeg, "-y", "-ss", str(time_sec), "-i", tmp_mp4, "-vframes", "1", "-q:v", "2", output_path]
        try:
            subprocess.run(cmd, capture_output=True, timeout=30)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                os.remove(tmp_mp4)
                return True
        except Exception:
            pass
    print(f"  Video saved to {tmp_mp4}")
    return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Wallpaper Engine TEX Extractor")
    parser.add_argument("input", help="Path to .tex file")
    parser.add_argument("-o", "--output", default=None, help="Output file path")
    parser.add_argument("--info", action="store_true", help="Show file info only")
    args = parser.parse_args()
    with open(args.input, "rb") as f:
        data = f.read()
    info = probe_tex(data)
    print(f"TEX format: {info['format']} ({info['width']}x{info['height']})")
    print(f"Data size: {info['data_size']:,} bytes")
    print(f"Is video: {info['is_video']}")
    if not args.info:
        out = args.output or (args.input + ".mp4" if info["is_video"] else args.input + ".dds")
        payload = extract_tex(data, out)
        print(f"Extracted {len(payload):,} bytes to {out}")

if __name__ == "__main__":
    main()
