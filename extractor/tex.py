"""Wallpaper Engine TEX texture file parser.

The TEXv5 format stores textures which can be:
  1. Compressed GPU textures (DXT/BCn formats)
  2. Video textures (H.264/H.265 in MP4/ISOBMFF container)
  3. Other pixel formats

Structure:
  TEXV0005\x00      (9 bytes - magic + version + null)
  TEXI0001\x00      (9 bytes - info chunk header)
  [Info data]       (format, flags, width, height)
  TEXB0004\x00      (9 bytes - data chunk header)  [or TEXB0004 with diff null]
  [Sub-header]      (texture-specific metadata)
  [Raw data]        (compressed texture or MP4 data)
"""

import struct
import os


def probe_tex(data: bytes) -> dict:
    """Read TEX metadata without extracting the full payload."""
    if not data.startswith(b"TEXV0005\x00"):
        raise ValueError("Not a TEXv5 file")

    # Find TEXI (info) chunk
    tex_i = data.find(b"TEXI0001\x00")
    if tex_i < 0:
        raise ValueError("Missing TEXI0001 chunk")

    info_start = tex_i + 9
    # Info layout: padding(4) + format(4) + unknown(4) + width(4) + height(4) + ...
    if info_start + 16 > len(data):
        raise ValueError("Truncated TEXI data")

    tex_format = struct.unpack_from("<I", data, info_start + 4)[0]  # at offset +4
    width = struct.unpack_from("<I", data, info_start + 8)[0]
    height = struct.unpack_from("<I", data, info_start + 12)[0]

    # Find TEXB (data) chunk
    tex_b = data.find(b"TEXB0004")
    if tex_b < 0:
        raise ValueError("Missing TEXB0004 chunk")

    chunk_start = tex_b + 8
    # Check for null terminator after TEXB0004
    if chunk_start < len(data) and data[chunk_start] == 0:
        chunk_start += 1

    chunk_data = data[chunk_start:]
    data_size = len(chunk_data)

    # Detect if this is an MP4 video (most video texture)
    is_video = chunk_data.find(b"ftyp") >= 0 and chunk_data.find(b"moov") >= 0

    return {
        "format": tex_format,
        "width": width,
        "height": height,
        "data_size": data_size,
        "is_video": is_video,
    }


def extract_tex(data: bytes, output_path: str = None) -> bytes:
    """Extract the raw payload (MP4 or texture data) from a TEX file.

    Returns the extracted bytes. If output_path is given, also writes to file.
    """
    if not data.startswith(b"TEXV0005\x00"):
        raise ValueError("Not a TEXv5 file")

    tex_b = data.find(b"TEXB0004")
    if tex_b < 0:
        raise ValueError("Missing TEXB0004 chunk")

    chunk_start = tex_b + 8
    if chunk_start < len(data) and data[chunk_start] == 0:
        chunk_start += 1

    chunk_data = data[chunk_start:]

    # For video textures, skip the sub-header (44 bytes) to get to the MP4
    if chunk_data.find(b"ftyp") >= 0:
        ftyp_offset = chunk_data.find(b"ftyp")
        if ftyp_offset >= 4:
            # The ftyp box starts 4 bytes before 'ftyp' (big-endian size field)
            mp4_start = ftyp_offset - 4
            payload = chunk_data[mp4_start:]
        else:
            payload = chunk_data
    else:
        # For compressed textures, the TEXB data may start with a small sub-header
        # The actual DXT data follows. This varies by format.
        payload = chunk_data

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(payload)

    return payload


def extract_video_frame(tex_data: bytes, output_path: str, time_sec: float = 0.0) -> bool:
    """Try to extract a single video frame using available tools.

    Tries: ffmpeg, avconvert (macOS), then falls back to noting
    that the video was extracted successfully.
    
    Returns True if a frame was extracted, False otherwise.
    """
    import subprocess, shutil, tempfile

    tmp_mp4 = os.path.join(os.path.dirname(output_path), "_temp_video.mp4")
    payload = extract_tex(tex_data, tmp_mp4)

    # Try ffmpeg first
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        frame_out = output_path
        cmd = [
            ffmpeg, "-y",
            "-ss", str(time_sec),
            "-i", tmp_mp4,
            "-vframes", "1",
            "-q:v", "2",
            frame_out,
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=30)
            if os.path.exists(frame_out) and os.path.getsize(frame_out) > 0:
                os.remove(tmp_mp4)
                return True
        except Exception:
            pass

    # Try macOS avconvert as fallback
    avconvert = shutil.which("avconvert")
    if avconvert:
        temp_mov = tempfile.mktemp(suffix=".mov")
        try:
            subprocess.run(
                [avconvert, "-s", tmp_mp4, "-p", "PresetHighestQuality", "-o", temp_mov],
                capture_output=True, timeout=60,
            )
            # Then try sips to convert
            sips_cmd = ["sips", "-s", "format", "png", temp_mov, "--out", output_path]
            subprocess.run(sips_cmd, capture_output=True, timeout=30)
            if os.path.exists(output_path):
                os.remove(tmp_mp4)
                os.remove(temp_mov)
                return True
        except Exception:
            pass

    # If we can't extract a frame, just note that the video was saved
    print(f"  Video texture saved to {tmp_mp4}")
    print(f"  Use ffmpeg to extract a frame: ffmpeg -i {tmp_mp4} -ss 0 -vframes 1 frame.png")
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
