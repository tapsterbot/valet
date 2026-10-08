"""Extract one frame per second from a screen recording, list the moments where the screen holds
still (good screenshot candidates), and make labelled contact sheets of them.

Usage: python find_frames.py RECORDING.mov FRAMES_DIR
"""
import argparse
import glob
import os
import subprocess

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

# Mean greyscale pixel change between seconds (0-255); above this, the screen changed.
# New pages score about 5-50, typing or pointer moves about 0.7-1.5 (see README).
STILL_THRESHOLD = 0.6


def extract(recording, frames_dir):
    os.makedirs(frames_dir, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-i", recording, "-vf", "fps=1",
                    os.path.join(frames_dir, "%04d.png")], check=True)


def still_segments(files):
    """Group consecutive frames into runs where the screen doesn't change."""
    def small(f):
        return Image.open(f).convert("L").resize((374, 275))
    segments, start, prev = [], 0, small(files[0])
    for i in range(1, len(files)):
        cur = small(files[i])
        if ImageStat.Stat(ImageChops.difference(prev, cur)).mean[0] > STILL_THRESHOLD:
            segments.append((start + 1, i))  # 1-based seconds, matching the frame file names
            start = i
        prev = cur
    segments.append((start + 1, len(files)))
    return segments


def contact_sheet(frames_dir, seconds, out, cols=4, tw=480, th=353):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    rows = (len(seconds) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 34)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, sec in enumerate(seconds):
        im = Image.open(os.path.join(frames_dir, f"{sec:04d}.png")).convert("RGB").resize((tw - 8, th - 8))
        x, y = (i % cols) * tw, (i // cols) * (th + 34)
        sheet.paste(im, (x + 4, y + 34))
        draw.text((x + 8, y + 2), f"{sec}s", fill="red", font=font)
    sheet.save(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("recording")
    parser.add_argument("frames_dir")
    args = parser.parse_args()

    extract(args.recording, args.frames_dir)
    files = sorted(glob.glob(os.path.join(args.frames_dir, "[0-9]*.png")))
    segments = still_segments(files)
    for first, last in segments:
        print(f"{first:4d}-{last:4d}s  ({last - first + 1}s)")

    # One contact sheet per 16 segments, showing the last frame of each
    ends = [last for _, last in segments]
    for n, i in enumerate(range(0, len(ends), 16), start=1):
        out = os.path.join(args.frames_dir, f"contact-sheet-{n}.png")
        contact_sheet(args.frames_dir, ends[i:i + 16], out)
        print("wrote", out)


if __name__ == "__main__":
    main()
