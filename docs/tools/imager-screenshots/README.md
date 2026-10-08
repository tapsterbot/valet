# Raspberry Pi Imager screenshots

Tools for making the Raspberry Pi Imager screenshots in the [Install OS guide](../../source/install-os.md)
from a screen recording, in the same style as the guide: the window on white with a macOS shadow,
and yellow arrows pointing at what to click.

Requires `ffmpeg` and Python with Pillow (`sudo apt install ffmpeg python3-pil`).

## What you need

1. **A screen recording** of setting up an SD card in Raspberry Pi Imager on a Mac. Pause for 2–3 seconds
   on each screen, and use example values for passwords and Wi-Fi.
2. **One ordinary screenshot of the Imager window** (Cmd-Shift-4, then Space, then click the window).
   While a window is being recorded, macOS hides its red/yellow/green buttons behind a recording
   indicator, so the buttons and title bar are taken from this screenshot instead.

Keep both files out of the repo, since the recording is large.

## Steps

1. Extract frames and find the screens:
   ```bash
   python find_frames.py ~/imager-recording.mov /tmp/imager-frames
   ```
   This saves one frame per second (`0001.png`, `0002.png`, ...), lists the stretches where the screen
   holds still, and writes contact sheets (`contact-sheet-*.png`) labelled with the second of each frame.
2. In `make_screenshots.py`, update the settings for the new recording:
   - `WINDOW_BOX`: where the Imager window is in the video frames.
   - `FRAMES`: which second to use for each screenshot. Pick frames with no mouse pointer over the window.
   - `PATCHES`: cover up anything unwanted (like a mouse pointer) by copying the same area from another
     screenshot.
   - `ARROWS`: for each arrow, the point it aims at and the direction of its tail, in degrees
     (57 = tail down-right like the original guide, 237 = up-left, 303 = up-right).
   - `TITLEBAR_DY`: if the title bar patch looks off by a pixel or two, adjust this.
3. Build the screenshots, check them, and adjust arrow positions until nothing important is covered:
   ```bash
   python make_screenshots.py /tmp/imager-frames ~/imager-window.png /tmp/imager-screenshots
   ```
4. Copy the finished images into `docs/source/images/` and update `install-os.md` to match.

The arrow style (color, length and proportions) is defined in `imaging.py` and was measured from
the original guide's arrows.

## How `find_frames.py` finds the screens

It's a simple pixel diff. Each second's frame is shrunk to a quarter size and made greyscale
(which is faster and smooths out video compression noise), then compared with the previous
second's frame. The average brightness difference across all pixels (0 = identical, 255 = black
vs. white) is one number per second. Above `STILL_THRESHOLD` (0.6), the screen has changed.

In the October 2026 recording:
- A new page or dialog scored roughly 5 to 50.
- Typing, moving the mouse pointer, or a button highlighting scored about 0.7 to 1.5. That's just
  over the threshold, so these also start a new segment, and some screens get split into a few
  short pieces.
- Nothing changing scored near 0.

So it errs on the side of splitting too often: an extra segment is just one more thumbnail to skip,
while a missed screen would be lost. Things to know:
- Only one frame per second is checked, so a screen shown for less than a second can be missed.
  That's why the recording should pause 2–3 seconds on each screen.
- The threshold was chosen for this recording. A different recording size or a busier background
  might need it adjusted.
- It can't tell an important change from a trivial one (a ticked checkbox looks about the same as a
  moving pointer), so it only narrows the frames down to candidates. Choosing the screenshots is
  done by looking at the contact sheets.
