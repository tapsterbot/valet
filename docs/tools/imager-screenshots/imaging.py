"""Image helpers for turning Raspberry Pi Imager screen recordings into setup guide screenshots."""
import math

from PIL import Image, ImageDraw, ImageFilter

# Canvas layout, matching the original macOS window screenshots in the guide:
# the window sits 112px from the sides and 75px from the top, with room for its shadow below.
LEFT, TOP, RIGHT, BOTTOM = 112, 75, 112, 148
CORNER_RADIUS = 30

# Arrow style, measured from the arrows in the original guide screenshots.
YELLOW = (255, 249, 83)


def rounded_mask(size, radius, scale=4):
    """Anti-aliased mask for a rectangle with rounded corners."""
    w, h = size
    big = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(big).rounded_rectangle((scale, scale, w * scale - scale - 1, h * scale - scale - 1),
                                          radius * scale, fill=255)
    return big.resize(size, Image.LANCZOS)


def frame_window(frame, window_box):
    """Cut the window out of a video frame and place it on white with a macOS-style shadow."""
    win = frame.convert("RGB").crop(window_box)
    w, h = win.size
    canvas = Image.new("RGB", (LEFT + w + RIGHT, TOP + h + BOTTOM), "white")
    mask = rounded_mask((w, h), CORNER_RADIUS)
    shadow = Image.new("L", canvas.size, 0)
    shadow.paste(mask.point(lambda v: v * 0.55), (LEFT, TOP + 22))
    shadow = shadow.filter(ImageFilter.GaussianBlur(32))
    canvas.paste(Image.new("RGB", canvas.size, "black"), (0, 0), shadow)
    canvas.paste(win, (LEFT, TOP), mask)
    return canvas


def titlebar_patch(still_path, box, dy=0, white=253):
    """Cut the title bar (window buttons and title) out of a still macOS window screenshot.

    While a window is being screen-recorded, macOS covers its red/yellow/green buttons with a
    recording indicator, so the buttons are taken from an ordinary screenshot instead.
    `dy` is how much lower the still screenshot sits than the framed video images, and `white`
    is the video's white level, so the patch blends in."""
    still = Image.open(still_path)
    flat = Image.new("RGB", still.size, "white")
    flat.paste(still, (0, 0), still.convert("RGBA"))
    patch = flat.crop((box[0], box[1] + dy, box[2], box[3] + dy))
    return patch.point(lambda v: round(v * white / 255))


def arrow(img, tip, angle, length=228, shaft=18, head_len=100, head_w=90):
    """Draw a guide-style arrow pointing at `tip`.

    `angle` is the direction from the tip to the tail, in degrees, with y pointing down:
    0 = tail to the right, 57 = tail down-right (the original guide's style),
    123 = down-left, 237 = up-left, 303 = up-right."""
    scale = 4  # draw large and downsample for smooth edges
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)  # from the tip toward the tail
    px, py = -uy, ux                   # perpendicular, for widths
    tx, ty = tip
    bx, by = tx + ux * head_len, ty + uy * head_len  # where the head meets the shaft
    ex, ey = tx + ux * length, ty + uy * length      # end of the tail
    head = [(tx, ty),
            (bx + px * head_w / 2, by + py * head_w / 2),
            (bx - px * head_w / 2, by - py * head_w / 2)]
    body = [(bx + px * shaft / 2, by + py * shaft / 2),
            (ex + px * shaft / 2, ey + py * shaft / 2),
            (ex - px * shaft / 2, ey - py * shaft / 2),
            (bx - px * shaft / 2, by - py * shaft / 2)]
    mask = Image.new("L", (img.width * scale, img.height * scale), 0)
    draw = ImageDraw.Draw(mask)
    for points in (head, body):
        draw.polygon([(x * scale, y * scale) for x, y in points], fill=255)
    mask = mask.resize(img.size, Image.LANCZOS)
    img.paste(Image.new("RGB", img.size, YELLOW), (0, 0), mask)
