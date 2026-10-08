"""Build the setup guide's Raspberry Pi Imager screenshots from extracted video frames.

Usage: python make_screenshots.py FRAMES_DIR STILL_SCREENSHOT.png OUTPUT_DIR

FRAMES_DIR comes from find_frames.py. The settings below are for the October 2026 recording
of Raspberry Pi Imager v2.0.12; update them for a new recording.
"""
import argparse
import os

from PIL import Image

from imaging import arrow, frame_window, titlebar_patch

# Where the Imager window is in each video frame (left, top, right, bottom).
WINDOW_BOX = (68, 52, 1428, 1016)

# Title bar area (window buttons and title) to replace from the still screenshot, in output
# image coordinates, and how much lower the still screenshot sits than the output images.
TITLEBAR_BOX = (118, 82, 680, 134)
TITLEBAR_DY = 1

# Output image name -> second of the recording to use (frame file number from find_frames.py).
FRAMES = {
    "imager-select-device": 17,
    "imager-select-os": 30,
    "imager-select-storage": 37,
    "imager-hostname": 55,
    "imager-localisation": 66,
    "imager-user": 119,
    "imager-wifi": 161,
    "imager-ssh": 166,
    "imager-pi-connect": 170,
    "imager-write-summary": 174,
    "imager-erase-warning": 180,
    "imager-writing": 300,
    "imager-write-complete": 500,
}

# Fix-ups: copy a box (output image coordinates) from another screenshot that has the same
# content there. The mouse pointer sat on NEXT the whole time the Pi Connect screen was shown,
# so that button row comes from the SSH screen.
PATCHES = {
    "imager-pi-connect": [("imager-ssh", (1170, 940, 1440, 1034))],
}

# Arrows: (tip x, tip y) and the direction of the tail in degrees (see imaging.arrow).
ARROWS = {
    "imager-select-device":  [((1380, 530), 70)],    # Raspberry Pi 4 row
    "imager-select-os":      [((1300, 540), 70)],    # Raspberry Pi OS (64-bit) row
    "imager-select-storage": [((1000, 440), 57)],    # SD card row
    "imager-hostname":       [((835, 552), 303)],    # hostname field
    "imager-user":           [((1150, 455), 303)],   # username field
    "imager-wifi":           [((1150, 437), 303)],   # SSID field
    "imager-ssh":            [((1330, 504), 80),     # Enable SSH toggle
                              ((1000, 622), 123)],   # Use password authentication
    "imager-write-summary":  [((1182, 948), 237)],   # WRITE button
    "imager-erase-warning":  [((1200, 694), 57)],    # I UNDERSTAND, ERASE AND WRITE
    "imager-write-complete": [((1360, 950), 290)],   # FINISH button
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("frames_dir")
    parser.add_argument("still_screenshot")
    parser.add_argument("output_dir")
    args = parser.parse_args()

    titlebar = titlebar_patch(args.still_screenshot, TITLEBAR_BOX, dy=TITLEBAR_DY)

    # Frame every screenshot first, since patches copy from other (un-annotated) screenshots
    images = {}
    for name, second in FRAMES.items():
        frame = Image.open(os.path.join(args.frames_dir, f"{second:04d}.png"))
        img = frame_window(frame, WINDOW_BOX)
        img.paste(titlebar, TITLEBAR_BOX[:2])
        images[name] = img
    for name, patches in PATCHES.items():
        for source, box in patches:
            images[name].paste(images[source].crop(box), box[:2])

    os.makedirs(args.output_dir, exist_ok=True)
    for name, img in images.items():
        img = img.copy()
        for tip, angle in ARROWS.get(name, []):
            arrow(img, tip, angle)
        out = os.path.join(args.output_dir, f"{name}.png")
        img.save(out, optimize=True)
        print("wrote", out)


if __name__ == "__main__":
    main()
