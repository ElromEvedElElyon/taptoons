#!/usr/bin/env python3
"""
TapToons v3.0 Sprite Generator
Generates all game assets as base64 PNG data URIs.
Pixel art style inspired by Celeste / Shovel Knight.

In the name of the Lord Jesus Christ.
"""

import json
import base64
import io
import math
import random
from PIL import Image, ImageDraw

# ============================================================
# PALETTE - Celeste / Shovel Knight inspired
# ============================================================
PAL = {
    'black':       (26, 28, 44),
    'dark_purple': (93, 39, 93),
    'red':         (177, 62, 83),
    'orange':      (239, 125, 87),
    'yellow':      (255, 205, 117),
    'lime':        (167, 240, 112),
    'green':       (56, 183, 100),
    'cyan':        (115, 239, 161),
    'dark_blue':   (41, 54, 111),
    'blue':        (59, 93, 201),
    'sky_blue':    (65, 166, 246),
    'teal':        (37, 113, 121),
    'white':       (255, 255, 255),
    'light_gray':  (200, 210, 220),
    'mid_gray':    (140, 150, 165),
    'dark_gray':   (80, 90, 100),
    'pink':        (255, 150, 180),
    'hot_pink':    (255, 100, 150),
    'light_blue':  (150, 200, 255),
    'brown':       (130, 80, 50),
    'dark_brown':  (90, 55, 35),
    'tan':         (180, 130, 80),
    'gold':        (255, 200, 50),
    'deep_red':    (140, 40, 50),
    'light_purple':(180, 130, 220),
    'magenta':     (200, 60, 150),
    'peach':       (255, 180, 140),
    'dark_green':  (30, 120, 60),
    'forest':      (20, 80, 40),
    'transparent': (0, 0, 0, 0),
}

T = PAL['transparent']


def img_to_base64(img):
    """Convert PIL Image to base64 data URI string."""
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64}"


def make_image(w, h):
    """Create a transparent RGBA image."""
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def px(img, x, y, color):
    """Set a single pixel, skip if out of bounds or transparent."""
    if 0 <= x < img.width and 0 <= y < img.height:
        if isinstance(color, tuple) and len(color) == 4 and color[3] == 0:
            return
        if isinstance(color, tuple) and len(color) == 3:
            color = color + (255,)
        img.putpixel((x, y), color)


def fill_rect(img, x, y, w, h, color):
    """Fill a rectangle."""
    for dy in range(h):
        for dx in range(w):
            px(img, x + dx, y + dy, color)


def draw_circle_filled(img, cx, cy, r, color):
    """Draw a filled circle."""
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r:
                px(img, cx + x, cy + y, color)


def draw_outline(img, cx, cy, r, color):
    """Draw circle outline."""
    for angle in range(360):
        rad = math.radians(angle)
        x = int(cx + r * math.cos(rad))
        y = int(cy + r * math.sin(rad))
        px(img, x, y, color)


# ============================================================
# 1. PLAYER CHARACTERS - 32x32, 4 frames each
# ============================================================

def draw_sulley(frame):
    """Blue furry monster with horns. Inspired by big friendly beast."""
    img = make_image(32, 32)
    c_body = PAL['blue']
    c_body_light = PAL['sky_blue']
    c_belly = PAL['light_blue']
    c_horn = PAL['yellow']
    c_horn_dark = PAL['orange']
    c_eye_white = PAL['white']
    c_pupil = PAL['black']
    c_mouth = PAL['dark_purple']

    # Animation offsets
    leg_off = 0
    body_off = 0
    if frame == 'run1':
        leg_off = -1
        body_off = -1
    elif frame == 'run2':
        leg_off = 1
        body_off = 0
    elif frame == 'jump':
        body_off = -2

    by = 8 + body_off  # body y offset

    # Horns
    for i in range(3):
        px(img, 10, by - 1 + i, c_horn_dark)
        px(img, 11, by - 2 + i, c_horn)
    for i in range(3):
        px(img, 20, by - 1 + i, c_horn_dark)
        px(img, 21, by - 2 + i, c_horn)

    # Head (round, furry)
    for y in range(6):
        w = min(y + 3, 7)
        for x in range(-w, w + 1):
            c = c_body_light if (x + y) % 3 == 0 else c_body
            px(img, 16 + x, by + y, c)

    # Body (wider)
    for y in range(8):
        w = min(y + 5, 9)
        for x in range(-w, w + 1):
            if abs(x) < w - 2 and y > 1:
                c = c_belly
            elif (x + y) % 4 == 0:
                c = c_body_light
            else:
                c = c_body
            px(img, 16 + x, by + 6 + y, c)

    # Eyes
    for dx in [-3, 3]:
        fill_rect(img, 14 + dx, by + 2, 3, 3, c_eye_white)
        px(img, 15 + dx, by + 3, c_pupil)

    # Mouth
    fill_rect(img, 14, by + 6, 5, 1, c_mouth)

    # Arms
    arm_y = by + 8
    fill_rect(img, 6, arm_y, 2, 5, c_body)
    fill_rect(img, 24, arm_y, 2, 5, c_body)

    # Legs
    leg_y = by + 14
    if frame == 'jump':
        # legs tucked
        fill_rect(img, 11, leg_y + 1, 3, 3, c_body)
        fill_rect(img, 18, leg_y + 1, 3, 3, c_body)
    else:
        fill_rect(img, 11 - leg_off, leg_y, 3, 5, c_body)
        fill_rect(img, 18 + leg_off, leg_y, 3, 5, c_body)
        # feet
        fill_rect(img, 10 - leg_off, leg_y + 4, 5, 2, c_body_light)
        fill_rect(img, 17 + leg_off, leg_y + 4, 5, 2, c_body_light)

    # Fur tufts
    for i in range(5):
        fx = 9 + i * 3
        px(img, fx, by + 1, c_body_light)
        px(img, fx + 1, by, c_body_light)

    return img


def draw_mike(frame):
    """Green one-eyed monster."""
    img = make_image(32, 32)
    c_body = PAL['green']
    c_light = PAL['cyan']
    c_dark = PAL['dark_green']
    c_eye = PAL['white']
    c_pupil = PAL['black']
    c_iris = PAL['green']
    c_mouth = PAL['dark_purple']

    body_off = 0
    leg_off = 0
    if frame == 'run1':
        leg_off = -1; body_off = -1
    elif frame == 'run2':
        leg_off = 1
    elif frame == 'jump':
        body_off = -2

    by = 6 + body_off

    # Body - round ball shape
    for y in range(16):
        ry = y - 8
        w = int(math.sqrt(max(0, 64 - ry * ry)))
        for x in range(-w, w + 1):
            dist = abs(x) + abs(ry)
            if dist < 4:
                c = c_light
            elif (x + y) % 5 == 0:
                c = c_light
            else:
                c = c_body
            px(img, 16 + x, by + 4 + y, c)

    # Giant eye
    draw_circle_filled(img, 16, by + 8, 5, c_eye)
    draw_circle_filled(img, 16, by + 8, 3, c_iris)
    draw_circle_filled(img, 16, by + 8, 2, c_pupil)
    px(img, 15, by + 7, PAL['white'])  # highlight

    # Eyebrow
    fill_rect(img, 11, by + 3, 10, 1, c_dark)

    # Mouth
    fill_rect(img, 13, by + 14, 6, 2, c_mouth)
    # Teeth
    px(img, 14, by + 14, PAL['white'])
    px(img, 17, by + 14, PAL['white'])

    # Legs
    leg_y = by + 19
    if frame == 'jump':
        fill_rect(img, 12, leg_y + 1, 3, 3, c_dark)
        fill_rect(img, 17, leg_y + 1, 3, 3, c_dark)
    else:
        fill_rect(img, 12 - leg_off, leg_y, 3, 5, c_dark)
        fill_rect(img, 17 + leg_off, leg_y, 3, 5, c_dark)
        fill_rect(img, 11 - leg_off, leg_y + 4, 5, 2, c_body)
        fill_rect(img, 16 + leg_off, leg_y + 4, 5, 2, c_body)

    # Arms (small)
    fill_rect(img, 7, by + 10, 2, 4, c_dark)
    fill_rect(img, 23, by + 10, 2, 4, c_dark)

    # Horn/antenna
    px(img, 16, by + 1, c_body)
    px(img, 16, by, c_light)

    return img


def draw_rosie(frame):
    """Pink cute monster with bow."""
    img = make_image(32, 32)
    c_body = PAL['pink']
    c_light = PAL['peach']
    c_dark = PAL['hot_pink']
    c_bow = PAL['red']
    c_eye = PAL['white']
    c_pupil = PAL['black']

    body_off = 0
    leg_off = 0
    if frame == 'run1':
        leg_off = -1; body_off = -1
    elif frame == 'run2':
        leg_off = 1
    elif frame == 'jump':
        body_off = -3

    by = 6 + body_off

    # Bow
    fill_rect(img, 18, by, 4, 3, c_bow)
    fill_rect(img, 10, by, 4, 3, c_bow)
    fill_rect(img, 14, by + 1, 4, 2, c_dark)

    # Head (round)
    for y in range(8):
        w = min(y + 3, 7)
        for x in range(-w, w + 1):
            c = c_light if abs(x) < 2 and y > 4 else c_body
            px(img, 16 + x, by + 3 + y, c)

    # Eyes (big cute)
    for dx in [-3, 3]:
        fill_rect(img, 14 + dx, by + 5, 3, 4, c_eye)
        fill_rect(img, 15 + dx, by + 7, 2, 2, c_pupil)
        px(img, 15 + dx, by + 6, PAL['white'])  # sparkle

    # Blush
    fill_rect(img, 9, by + 8, 2, 1, PAL['hot_pink'])
    fill_rect(img, 21, by + 8, 2, 1, PAL['hot_pink'])

    # Smile
    fill_rect(img, 14, by + 10, 4, 1, c_dark)

    # Body
    for y in range(7):
        w = min(y + 4, 7)
        for x in range(-w, w + 1):
            c = c_light if abs(x) < 3 else c_body
            px(img, 16 + x, by + 11 + y, c)

    # Arms
    fill_rect(img, 7, by + 12, 2, 4, c_body)
    fill_rect(img, 23, by + 12, 2, 4, c_body)

    # Legs
    leg_y = by + 18
    if frame == 'jump':
        fill_rect(img, 12, leg_y + 1, 3, 3, c_dark)
        fill_rect(img, 17, leg_y + 1, 3, 3, c_dark)
    else:
        fill_rect(img, 12 - leg_off, leg_y, 3, 5, c_dark)
        fill_rect(img, 17 + leg_off, leg_y, 3, 5, c_dark)

    # Tail (cute curl)
    px(img, 24, by + 14, c_dark)
    px(img, 25, by + 13, c_dark)
    px(img, 26, by + 13, c_body)

    return img


def draw_drake(frame):
    """Purple dragon monster."""
    img = make_image(32, 32)
    c_body = PAL['dark_purple']
    c_light = PAL['light_purple']
    c_belly = PAL['peach']
    c_wing = PAL['magenta']
    c_eye = PAL['yellow']
    c_pupil = PAL['black']
    c_horn = PAL['orange']

    body_off = 0
    leg_off = 0
    if frame == 'run1':
        leg_off = -1; body_off = -1
    elif frame == 'run2':
        leg_off = 1
    elif frame == 'jump':
        body_off = -2

    by = 5 + body_off

    # Horns
    for i in range(3):
        px(img, 12, by + i, c_horn)
        px(img, 20, by + i, c_horn)

    # Head
    for y in range(6):
        w = min(y + 2, 6)
        for x in range(-w, w + 1):
            px(img, 16 + x, by + 3 + y, c_body)

    # Snout
    fill_rect(img, 13, by + 7, 6, 3, c_light)

    # Eyes (fierce)
    fill_rect(img, 12, by + 5, 3, 2, c_eye)
    px(img, 13, by + 6, c_pupil)
    fill_rect(img, 18, by + 5, 3, 2, c_eye)
    px(img, 19, by + 6, c_pupil)

    # Body
    for y in range(8):
        w = min(y + 4, 8)
        for x in range(-w, w + 1):
            if abs(x) < w - 2:
                c = c_belly
            else:
                c = c_body
            px(img, 16 + x, by + 10 + y, c)

    # Wings
    wing_flap = 1 if frame in ('run1', 'jump') else 0
    for i in range(5):
        px(img, 6 - i, by + 10 + i - wing_flap, c_wing)
        px(img, 7 - i, by + 10 + i - wing_flap, c_wing)
        px(img, 25 + i, by + 10 + i - wing_flap, c_wing)
        px(img, 26 + i, by + 10 + i - wing_flap, c_wing)
    # Wing membrane
    for i in range(4):
        for j in range(i + 1):
            px(img, 6 - i + j, by + 11 + i - wing_flap, c_light)
            px(img, 25 + i - j, by + 11 + i - wing_flap, c_light)

    # Legs
    leg_y = by + 18
    if frame == 'jump':
        fill_rect(img, 12, leg_y + 1, 3, 3, c_body)
        fill_rect(img, 17, leg_y + 1, 3, 3, c_body)
    else:
        fill_rect(img, 12 - leg_off, leg_y, 3, 5, c_body)
        fill_rect(img, 17 + leg_off, leg_y, 3, 5, c_body)
        # Claws
        for d in range(3):
            px(img, 11 - leg_off + d, leg_y + 5, c_horn)
            px(img, 16 + leg_off + d, leg_y + 5, c_horn)

    # Tail
    for i in range(5):
        px(img, 24 + i, by + 16 - i // 2, c_body)
    px(img, 29, by + 14, c_horn)  # tail tip fire

    # Spine ridge
    for i in range(4):
        px(img, 16, by + 3 - 1, c_horn)
        px(img, 16, by + 10 + i * 2, c_horn)

    return img


def draw_gears(frame):
    """Orange robot monster."""
    img = make_image(32, 32)
    c_body = PAL['orange']
    c_light = PAL['yellow']
    c_dark = PAL['brown']
    c_metal = PAL['mid_gray']
    c_dark_metal = PAL['dark_gray']
    c_eye = PAL['sky_blue']
    c_eye_glow = PAL['cyan']
    c_bolt = PAL['gold']

    body_off = 0
    leg_off = 0
    if frame == 'run1':
        leg_off = -1; body_off = -1
    elif frame == 'run2':
        leg_off = 1
    elif frame == 'jump':
        body_off = -2

    by = 5 + body_off

    # Antenna
    px(img, 16, by, c_eye_glow)
    px(img, 16, by + 1, c_metal)
    px(img, 16, by + 2, c_metal)

    # Head (boxy robot)
    fill_rect(img, 10, by + 3, 12, 8, c_body)
    fill_rect(img, 11, by + 4, 10, 6, c_dark)
    # Face plate
    fill_rect(img, 12, by + 5, 8, 4, c_metal)

    # Eyes (LED style)
    fill_rect(img, 13, by + 6, 2, 2, c_eye)
    fill_rect(img, 17, by + 6, 2, 2, c_eye)
    # Eye glow
    px(img, 13, by + 6, c_eye_glow)
    px(img, 17, by + 6, c_eye_glow)

    # Mouth (LED bar)
    fill_rect(img, 14, by + 9, 4, 1, c_eye)

    # Body (chunky)
    fill_rect(img, 9, by + 11, 14, 9, c_body)
    fill_rect(img, 10, by + 12, 12, 7, c_dark)
    # Chest plate
    fill_rect(img, 12, by + 13, 8, 5, c_metal)
    # Chest light
    fill_rect(img, 15, by + 14, 2, 2, c_eye_glow)
    # Bolts
    px(img, 12, by + 13, c_bolt)
    px(img, 19, by + 13, c_bolt)
    px(img, 12, by + 17, c_bolt)
    px(img, 19, by + 17, c_bolt)

    # Gear shoulders
    for dx in [-1, 13]:
        fill_rect(img, 9 + dx, by + 11, 3, 3, c_dark_metal)
        px(img, 10 + dx, by + 12, c_bolt)

    # Arms (piston style)
    fill_rect(img, 5, by + 12, 3, 6, c_metal)
    fill_rect(img, 24, by + 12, 3, 6, c_metal)
    fill_rect(img, 5, by + 17, 3, 2, c_dark_metal)
    fill_rect(img, 24, by + 17, 3, 2, c_dark_metal)

    # Legs
    leg_y = by + 20
    if frame == 'jump':
        fill_rect(img, 11, leg_y, 4, 3, c_metal)
        fill_rect(img, 17, leg_y, 4, 3, c_metal)
    else:
        fill_rect(img, 11 - leg_off, leg_y, 4, 5, c_metal)
        fill_rect(img, 17 + leg_off, leg_y, 4, 5, c_metal)
        # Feet (heavy)
        fill_rect(img, 10 - leg_off, leg_y + 4, 6, 2, c_dark_metal)
        fill_rect(img, 16 + leg_off, leg_y + 4, 6, 2, c_dark_metal)

    # Exhaust particles on run
    if frame in ('run1', 'run2'):
        px(img, 15, leg_y + 6, c_light)
        px(img, 17, leg_y + 7, c_body)

    return img


def draw_rex(frame):
    """Red dinosaur monster."""
    img = make_image(32, 32)
    c_body = PAL['red']
    c_light = PAL['orange']
    c_belly = PAL['yellow']
    c_dark = PAL['deep_red']
    c_eye = PAL['white']
    c_pupil = PAL['black']
    c_claw = PAL['white']
    c_teeth = PAL['white']

    body_off = 0
    leg_off = 0
    if frame == 'run1':
        leg_off = -1; body_off = -1
    elif frame == 'run2':
        leg_off = 1
    elif frame == 'jump':
        body_off = -2

    by = 4 + body_off

    # Head (dino shaped, slightly forward)
    for y in range(7):
        w = min(y + 2, 6)
        for x in range(-w, w + 1):
            c = c_light if y < 2 and abs(x) < 2 else c_body
            px(img, 17 + x, by + 2 + y, c)

    # Jaw/snout
    fill_rect(img, 19, by + 6, 5, 3, c_body)
    fill_rect(img, 20, by + 7, 4, 2, c_dark)
    # Teeth
    for i in range(3):
        px(img, 20 + i, by + 7, c_teeth)

    # Eye
    fill_rect(img, 15, by + 4, 3, 3, c_eye)
    fill_rect(img, 16, by + 5, 2, 2, c_pupil)
    px(img, 16, by + 4, PAL['white'])

    # Body
    for y in range(9):
        w = min(y + 4, 8)
        for x in range(-w, w + 1):
            if abs(x) < w - 2 and y > 2:
                c = c_belly
            else:
                c = c_body
            px(img, 16 + x, by + 9 + y, c)

    # Spine plates
    for i in range(5):
        px(img, 16, by + 1 + i, c_light)
        px(img, 16, by + 9 + i * 2, c_light)

    # Small arms (T-rex style)
    fill_rect(img, 8, by + 11, 2, 3, c_dark)
    fill_rect(img, 22, by + 11, 2, 3, c_dark)
    px(img, 8, by + 13, c_claw)
    px(img, 23, by + 13, c_claw)

    # Tail
    for i in range(6):
        py_off = i // 2
        px(img, 7 - i, by + 14 + py_off, c_body)
        px(img, 7 - i, by + 15 + py_off, c_body)
    px(img, 2, by + 17, c_dark)

    # Legs (thick)
    leg_y = by + 18
    if frame == 'jump':
        fill_rect(img, 11, leg_y + 1, 4, 3, c_dark)
        fill_rect(img, 17, leg_y + 1, 4, 3, c_dark)
    else:
        fill_rect(img, 11 - leg_off, leg_y, 4, 6, c_dark)
        fill_rect(img, 17 + leg_off, leg_y, 4, 6, c_dark)
        # Clawed feet
        for d in range(3):
            px(img, 10 - leg_off + d * 2, leg_y + 6, c_claw)
            px(img, 16 + leg_off + d * 2, leg_y + 6, c_claw)

    return img


# ============================================================
# 2. ENEMIES - 32x32, 2 frames each
# ============================================================

def draw_badnik(frame):
    """Badnik Robot - red shell with spikes."""
    img = make_image(32, 32)
    c_shell = PAL['red']
    c_shell_light = PAL['orange']
    c_metal = PAL['mid_gray']
    c_dark = PAL['dark_gray']
    c_eye = PAL['yellow']
    c_spike = PAL['white']
    c_black = PAL['black']

    bob = 0 if frame == 'frame1' else 1

    by = 6 + bob

    # Shell (dome)
    for y in range(10):
        ry = y - 5
        w = int(math.sqrt(max(0, 49 - ry * ry)))
        for x in range(-w, w + 1):
            # Highlight on top
            if y < 3 and abs(x) < 3:
                c = c_shell_light
            else:
                c = c_shell
            px(img, 16 + x, by + y, c)

    # Metal band
    fill_rect(img, 9, by + 8, 14, 2, c_metal)

    # Body/base
    fill_rect(img, 10, by + 10, 12, 6, c_dark)
    fill_rect(img, 11, by + 11, 10, 4, c_metal)

    # Eyes (menacing)
    fill_rect(img, 12, by + 12, 3, 2, c_eye)
    fill_rect(img, 17, by + 12, 3, 2, c_eye)
    px(img, 13, by + 13, c_black)
    px(img, 18, by + 13, c_black)

    # Spikes on shell
    spike_positions = [(10, by - 1), (16, by - 2), (22, by - 1),
                       (8, by + 3), (24, by + 3)]
    for sx, sy in spike_positions:
        px(img, sx, sy, c_spike)
        px(img, sx, sy + 1, c_spike)
        px(img, sx - 1 if sx < 16 else sx + 1, sy + 1, c_metal)

    # Wheels/treads
    fill_rect(img, 10, by + 16, 4, 3, c_dark)
    fill_rect(img, 18, by + 16, 4, 3, c_dark)
    # Wheel detail
    px(img, 12, by + 17, c_metal)
    px(img, 20, by + 17, c_metal)

    # Exhaust on frame2
    if frame == 'frame2':
        px(img, 8, by + 14, c_shell_light)
        px(img, 7, by + 15, c_dark)

    return img


def draw_bat(frame):
    """Flying Bat - purple winged enemy."""
    img = make_image(32, 32)
    c_body = PAL['dark_purple']
    c_wing = PAL['light_purple']
    c_wing_dark = PAL['magenta']
    c_eye = PAL['red']
    c_fang = PAL['white']

    wing_up = frame == 'frame1'
    by = 10 if wing_up else 12

    # Body (small, round)
    for y in range(6):
        w = min(y + 1, 3)
        for x in range(-w, w + 1):
            px(img, 16 + x, by + y, c_body)

    # Ears
    px(img, 13, by - 1, c_body)
    px(img, 13, by - 2, c_body)
    px(img, 19, by - 1, c_body)
    px(img, 19, by - 2, c_body)

    # Eyes (glowing red)
    px(img, 14, by + 2, c_eye)
    px(img, 18, by + 2, c_eye)

    # Fangs
    px(img, 15, by + 5, c_fang)
    px(img, 17, by + 5, c_fang)

    # Wings
    if wing_up:
        # Wings up
        for i in range(8):
            wy = by - i // 2
            px(img, 12 - i, wy + 1, c_wing_dark)
            px(img, 12 - i, wy, c_wing)
            px(img, 20 + i, wy + 1, c_wing_dark)
            px(img, 20 + i, wy, c_wing)
        # Wing membrane
        for i in range(6):
            for j in range(i // 2 + 1):
                px(img, 12 - i, by + 1 + j, c_wing)
                px(img, 20 + i, by + 1 + j, c_wing)
    else:
        # Wings down
        for i in range(8):
            wy = by + i // 2
            px(img, 12 - i, wy + 1, c_wing_dark)
            px(img, 12 - i, wy + 2, c_wing)
            px(img, 20 + i, wy + 1, c_wing_dark)
            px(img, 20 + i, wy + 2, c_wing)
        for i in range(6):
            for j in range(i // 2 + 1):
                px(img, 12 - i, by + 2 - j, c_wing)
                px(img, 20 + i, by + 2 - j, c_wing)

    # Small feet
    px(img, 15, by + 6, c_body)
    px(img, 17, by + 6, c_body)

    return img


def draw_slime(frame):
    """Slime - green bouncing blob."""
    img = make_image(32, 32)
    c_body = PAL['green']
    c_light = PAL['cyan']
    c_dark = PAL['dark_green']
    c_eye = PAL['white']
    c_pupil = PAL['black']
    c_shine = PAL['lime']

    # Frame 1: tall, frame 2: squished
    if frame == 'frame1':
        # Taller blob
        by = 8
        for y in range(16):
            # Teardrop shape
            if y < 4:
                w = y + 1
            elif y < 10:
                w = min(y, 8)
            else:
                w = max(8 - (y - 10), 3)
            for x in range(-w, w + 1):
                if abs(x) < w - 1 and y < 6:
                    c = c_light
                elif abs(x) == 0 and y < 3:
                    c = c_shine
                else:
                    c = c_body
                px(img, 16 + x, by + y, c)
        # Eyes
        fill_rect(img, 13, by + 7, 2, 3, c_eye)
        fill_rect(img, 17, by + 7, 2, 3, c_eye)
        px(img, 13, by + 9, c_pupil)
        px(img, 17, by + 9, c_pupil)
        # Shine
        px(img, 11, by + 4, c_shine)
        px(img, 12, by + 5, c_shine)
    else:
        # Squished wider blob
        by = 14
        for y in range(10):
            if y < 3:
                w = y + 4
            elif y < 7:
                w = min(y + 3, 10)
            else:
                w = max(10 - (y - 7), 5)
            for x in range(-w, w + 1):
                if abs(x) < w - 2 and y < 4:
                    c = c_light
                else:
                    c = c_body
                px(img, 16 + x, by + y, c)
        # Eyes (squished)
        fill_rect(img, 12, by + 3, 3, 2, c_eye)
        fill_rect(img, 18, by + 3, 3, 2, c_eye)
        px(img, 13, by + 4, c_pupil)
        px(img, 19, by + 4, c_pupil)
        # Splatter drops
        px(img, 6, by + 7, c_body)
        px(img, 26, by + 7, c_body)
        px(img, 8, by + 8, c_dark)
        px(img, 24, by + 8, c_dark)

    return img


# ============================================================
# 3. COLLECTIBLES - 32x32
# ============================================================

def draw_ring(frame_idx):
    """Gold Ring - 4-frame rotation animation."""
    img = make_image(32, 32)
    c_outer = PAL['gold']
    c_inner = PAL['yellow']
    c_shine = PAL['white']
    c_dark = PAL['orange']

    cx, cy = 16, 16

    # 4 frames showing ring rotating: full face, 3/4, side, 3/4 back
    widths = [7, 5, 2, 5]
    w = widths[frame_idx]

    # Outer ring
    for angle in range(360):
        rad = math.radians(angle)
        x = int(cx + w * math.cos(rad))
        y = int(cy + 7 * math.sin(rad))
        c = c_shine if angle < 60 else (c_outer if angle < 180 else c_dark)
        px(img, x, y, c)

    # Inner ring (slightly smaller)
    iw = max(w - 2, 0)
    if iw > 0:
        for angle in range(360):
            rad = math.radians(angle)
            x = int(cx + iw * math.cos(rad))
            y = int(cy + 5 * math.sin(rad))
            c = c_inner if angle < 180 else c_dark
            px(img, x, y, c)

    # Fill between outer and inner
    if w > 2:
        for angle in range(360):
            rad = math.radians(angle)
            for r_step in range(max(iw, 1), w):
                x = int(cx + r_step * math.cos(rad))
                yr = int(5 + (7 - 5) * (r_step - max(iw, 1)) / max(w - max(iw, 1), 1))
                y = int(cy + yr * math.sin(rad))
                if angle < 45:
                    c = c_shine
                elif angle < 180:
                    c = c_inner
                else:
                    c = c_dark
                px(img, x, y, c)

    # Sparkle
    if frame_idx == 0:
        px(img, cx - 4, cy - 6, c_shine)
        px(img, cx + 5, cy + 4, c_shine)

    return img


def draw_star(frame_idx):
    """Power Star - 2-frame twinkle."""
    img = make_image(32, 32)
    c_body = PAL['yellow']
    c_light = PAL['white']
    c_dark = PAL['orange']
    c_center = PAL['gold']

    cx, cy = 16, 16
    expand = 1 if frame_idx == 1 else 0

    # Star shape - 5 points
    points = []
    for i in range(5):
        angle = math.radians(-90 + i * 72)
        ox = int(cx + (9 + expand) * math.cos(angle))
        oy = int(cy + (9 + expand) * math.sin(angle))
        points.append((ox, oy))
        inner_angle = math.radians(-90 + i * 72 + 36)
        ix = int(cx + 4 * math.cos(inner_angle))
        iy = int(cy + 4 * math.sin(inner_angle))
        points.append((ix, iy))

    # Draw filled star using scanline
    for y in range(32):
        for x in range(32):
            # Check if point is inside star (approximate with distance)
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            angle = math.atan2(dy, dx)
            # Star radius at this angle
            star_r = 4
            for i in range(5):
                pt_angle = math.radians(-90 + i * 72)
                diff = abs(angle - pt_angle)
                if diff > math.pi:
                    diff = 2 * math.pi - diff
                if diff < math.radians(36):
                    star_r = max(star_r, (9 + expand) * (1 - diff / math.radians(36)) + 4 * (diff / math.radians(36)))
            if dist <= star_r:
                if dist < 3:
                    c = c_light
                elif dist < 5:
                    c = c_center
                else:
                    c = c_body
                px(img, x, y, c)

    # Eyes (cute)
    px(img, 14, 14, PAL['black'])
    px(img, 18, 14, PAL['black'])

    # Twinkle sparkles
    if frame_idx == 1:
        for sx, sy in [(5, 5), (27, 5), (5, 27), (27, 27)]:
            px(img, sx, sy, c_light)
            px(img, sx + 1, sy, c_light)
            px(img, sx, sy + 1, c_light)

    return img


def draw_shield(frame_idx):
    """Shield orb - 2-frame pulse."""
    img = make_image(32, 32)
    c_outer = PAL['sky_blue']
    c_inner = PAL['cyan']
    c_core = PAL['white']
    c_edge = PAL['blue']

    cx, cy = 16, 16
    r = 9 + frame_idx  # pulse

    # Outer glow
    for y in range(-r - 2, r + 3):
        for x in range(-r - 2, r + 3):
            dist = math.sqrt(x * x + y * y)
            if dist <= r + 2 and dist > r:
                px(img, cx + x, cy + y, c_edge + (80,))

    # Main orb
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            dist = math.sqrt(x * x + y * y)
            if dist <= r:
                if dist < 3:
                    c = c_core
                elif dist < 5:
                    c = c_inner
                elif dist < 7:
                    c = c_outer
                else:
                    c = c_edge
                # Add transparency gradient
                alpha = max(100, 255 - int(dist * 15))
                px(img, cx + x, cy + y, c + (alpha,) if len(c) == 3 else c)

    # Shield symbol (cross)
    for i in range(-2, 3):
        px(img, cx + i, cy, c_core)
        px(img, cx, cy + i, c_core)

    # Sparkle
    if frame_idx == 0:
        px(img, cx - 3, cy - 5, c_core)
    else:
        px(img, cx + 4, cy - 4, c_core)
        px(img, cx - 5, cy + 3, c_core)

    return img


# ============================================================
# 4. ENVIRONMENT TILES - 16x16
# ============================================================

def draw_ground_tile():
    """Ground block - grass top, dirt body."""
    img = make_image(16, 16)
    c_grass = PAL['green']
    c_grass_light = PAL['lime']
    c_grass_dark = PAL['dark_green']
    c_dirt = PAL['brown']
    c_dirt_light = PAL['tan']
    c_dirt_dark = PAL['dark_brown']

    # Grass top (3px high, undulating)
    for x in range(16):
        grass_h = 3 if x % 4 < 2 else 2
        for y in range(grass_h):
            if y == 0:
                c = c_grass_light
            elif y == 1:
                c = c_grass
            else:
                c = c_grass_dark
            px(img, x, y, c)

    # Dirt body
    random.seed(42)
    for y in range(3, 16):
        for x in range(16):
            r = random.random()
            if r < 0.15:
                c = c_dirt_light
            elif r < 0.3:
                c = c_dirt_dark
            else:
                c = c_dirt
            px(img, x, y, c)

    # Add small stones
    px(img, 4, 8, c_dirt_light)
    px(img, 5, 8, c_dirt_light)
    px(img, 11, 12, c_dirt_light)
    px(img, 12, 12, c_dirt_light)

    # Grass blades on top
    px(img, 3, 0, c_grass_light)
    px(img, 7, 0, c_grass_light)
    px(img, 12, 0, c_grass_light)

    return img


def draw_stone_platform():
    """Stone platform tile."""
    img = make_image(16, 16)
    c_stone = PAL['mid_gray']
    c_light = PAL['light_gray']
    c_dark = PAL['dark_gray']
    c_edge = PAL['black']

    # Fill base
    fill_rect(img, 0, 0, 16, 16, c_stone)

    # Top edge (highlight)
    fill_rect(img, 0, 0, 16, 1, c_light)
    # Left edge (highlight)
    for y in range(16):
        px(img, 0, y, c_light)

    # Bottom edge (shadow)
    fill_rect(img, 0, 15, 16, 1, c_dark)
    # Right edge (shadow)
    for y in range(16):
        px(img, 15, y, c_dark)

    # Stone cracks/mortar lines
    fill_rect(img, 0, 5, 16, 1, c_dark)
    fill_rect(img, 0, 10, 16, 1, c_dark)
    fill_rect(img, 7, 0, 1, 5, c_dark)
    fill_rect(img, 4, 6, 1, 4, c_dark)
    fill_rect(img, 11, 6, 1, 4, c_dark)
    fill_rect(img, 7, 11, 1, 5, c_dark)

    # Highlights on bricks
    px(img, 3, 2, c_light)
    px(img, 10, 2, c_light)
    px(img, 2, 7, c_light)
    px(img, 8, 7, c_light)
    px(img, 5, 12, c_light)
    px(img, 12, 12, c_light)

    return img


def draw_brick_block():
    """Brick block tile."""
    img = make_image(16, 16)
    c_brick = PAL['orange']
    c_light = PAL['yellow']
    c_dark = PAL['brown']
    c_mortar = PAL['dark_brown']

    # Fill background with mortar
    fill_rect(img, 0, 0, 16, 16, c_mortar)

    # Draw bricks in staggered pattern
    for row in range(4):
        y = row * 4
        offset = 4 if row % 2 == 1 else 0
        for col in range(-1, 3):
            bx = col * 8 + offset
            # Brick face
            fill_rect(img, bx + 1, y + 1, 6, 2, c_brick)
            # Highlight
            fill_rect(img, bx + 1, y + 1, 6, 1, c_light)
            # Shadow
            px(img, bx + 6, y + 2, c_dark)

    return img


# ============================================================
# 5. PARALLAX BACKGROUNDS - 480x270 (tileable)
# ============================================================

def draw_sky_layer():
    """Layer 1: Sky gradient."""
    img = make_image(480, 270)
    draw = ImageDraw.Draw(img)
    c_top = (26, 28, 44)      # deep blue
    c_mid = (41, 54, 111)     # dark blue
    c_bottom = (65, 166, 246) # sky blue

    for y in range(270):
        t = y / 270
        if t < 0.5:
            t2 = t * 2
            r = int(c_top[0] + (c_mid[0] - c_top[0]) * t2)
            g = int(c_top[1] + (c_mid[1] - c_top[1]) * t2)
            b = int(c_top[2] + (c_mid[2] - c_top[2]) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(c_mid[0] + (c_bottom[0] - c_mid[0]) * t2)
            g = int(c_mid[1] + (c_bottom[1] - c_mid[1]) * t2)
            b = int(c_mid[2] + (c_bottom[2] - c_mid[2]) * t2)
        draw.line([(0, y), (479, y)], fill=(r, g, b, 255))

    # Stars (upper portion)
    random.seed(777)
    for _ in range(60):
        sx = random.randint(0, 479)
        sy = random.randint(0, 120)
        brightness = random.randint(180, 255)
        size = random.choice([1, 1, 1, 2])
        c = (brightness, brightness, brightness, brightness)
        px(img, sx, sy, c)
        if size == 2:
            px(img, sx + 1, sy, c)
            px(img, sx, sy + 1, c)

    # Moon
    cx_m, cy_m = 400, 40
    for y in range(-12, 13):
        for x in range(-12, 13):
            dist = math.sqrt(x * x + y * y)
            if dist <= 12:
                # Crescent: cut out a circle offset to the right
                cut_dist = math.sqrt((x - 5) ** 2 + y * y)
                if cut_dist > 10:
                    bright = max(200, 255 - int(dist * 4))
                    px(img, cx_m + x, cy_m + y, (bright, bright, 220, 255))

    return img


def draw_mountains_layer():
    """Layer 2: Far mountains (dark purple silhouette)."""
    img = make_image(480, 270)
    c_mountain = (60, 30, 80)
    c_peak = (80, 45, 100)
    c_snow = (200, 210, 230)

    # Generate mountain profile using sine waves
    random.seed(123)
    heights = []
    for x in range(480):
        h = 0
        h += 60 * math.sin(x * 0.008 + 1.0)
        h += 30 * math.sin(x * 0.02 + 2.5)
        h += 15 * math.sin(x * 0.05 + 0.5)
        h += 8 * math.sin(x * 0.1)
        h = int(120 + h)
        heights.append(h)

    for x in range(480):
        mountain_top = heights[x]
        for y in range(mountain_top, 270):
            depth = y - mountain_top
            if depth < 3:
                c = c_peak
            elif depth < 8:
                c = c_mountain
            else:
                # Fade slightly
                fade = min(depth - 8, 30)
                c = (c_mountain[0] - fade, max(0, c_mountain[1] - fade), c_mountain[2] - fade // 2)
            px(img, x, y, c)

        # Snow on peaks
        if mountain_top < 100:
            for sy in range(max(0, mountain_top - 2), mountain_top + 3):
                px(img, x, sy, c_snow)

    return img


def draw_hills_layer():
    """Layer 3: Near hills (green with trees)."""
    img = make_image(480, 270)
    c_hill = PAL['green']
    c_hill_dark = PAL['dark_green']
    c_hill_light = PAL['lime']
    c_trunk = PAL['dark_brown']
    c_leaves = PAL['forest']
    c_leaves_light = PAL['green']

    # Generate hills
    heights = []
    for x in range(480):
        h = 0
        h += 40 * math.sin(x * 0.012 + 0.5)
        h += 20 * math.sin(x * 0.03 + 1.2)
        h += 10 * math.sin(x * 0.06 + 3.0)
        h = int(170 + h)
        heights.append(h)

    for x in range(480):
        hill_top = heights[x]
        for y in range(hill_top, 270):
            depth = y - hill_top
            if depth < 2:
                c = c_hill_light
            elif depth < 15:
                c = c_hill
            else:
                c = c_hill_dark
            px(img, x, y, c)

    # Trees (simple pixel art trees)
    random.seed(456)
    tree_positions = sorted(random.sample(range(20, 460, 3), 30))
    for tx in tree_positions:
        ty = heights[min(tx, 479)] - 1
        tree_h = random.randint(10, 20)

        # Trunk
        for i in range(tree_h // 2):
            px(img, tx, ty - i, c_trunk)
            px(img, tx + 1, ty - i, c_trunk)

        # Canopy (triangle)
        canopy_base = ty - tree_h // 2
        canopy_h = tree_h - tree_h // 2
        for cy in range(canopy_h):
            w = max(1, (canopy_h - cy))
            for cx_off in range(-w, w + 1):
                c = c_leaves_light if cy < 2 else c_leaves
                px(img, tx + cx_off, canopy_base - cy, c)

    return img


def draw_ground_layer():
    """Layer 4: Ground/flowers."""
    img = make_image(480, 270)
    c_ground = PAL['brown']
    c_ground_light = PAL['tan']
    c_grass = PAL['green']
    c_grass_light = PAL['lime']
    c_flower_r = PAL['red']
    c_flower_y = PAL['yellow']
    c_flower_p = PAL['pink']
    c_flower_b = PAL['sky_blue']

    # Ground starts at y=230
    ground_y = 230

    # Grass/ground fill
    for y in range(ground_y, 270):
        for x in range(480):
            depth = y - ground_y
            if depth < 3:
                c = c_grass_light if (x + depth) % 3 == 0 else c_grass
            elif depth < 6:
                c = c_grass if x % 5 == 0 else PAL['dark_green']
            else:
                random.seed(x * 270 + y)
                r = random.random()
                c = c_ground_light if r < 0.2 else c_ground
            px(img, x, y, c)

    # Grass blades above ground line
    random.seed(789)
    for x in range(0, 480, 2):
        if random.random() < 0.6:
            blade_h = random.randint(2, 5)
            for i in range(blade_h):
                c = c_grass_light if i == 0 else c_grass
                px(img, x, ground_y - 1 - i, c)

    # Flowers
    flower_colors = [c_flower_r, c_flower_y, c_flower_p, c_flower_b]
    for x in range(10, 470, 15):
        if random.random() < 0.5:
            fc = random.choice(flower_colors)
            fy = ground_y - random.randint(3, 7)
            # Stem
            for i in range(fy, ground_y):
                px(img, x, i, c_grass)
            # Petals
            px(img, x, fy, fc)
            px(img, x - 1, fy, fc)
            px(img, x + 1, fy, fc)
            px(img, x, fy - 1, fc)
            px(img, x, fy + 1, fc)
            px(img, x, fy, PAL['yellow'])  # center

    return img


# ============================================================
# 6. UI ELEMENTS - 16x16
# ============================================================

def draw_heart():
    """Heart icon 16x16."""
    img = make_image(16, 16)
    c_body = PAL['red']
    c_light = PAL['orange']
    c_dark = PAL['deep_red']
    c_shine = PAL['white']

    # Heart shape bitmap
    heart = [
        "..xxxx..xxxx..",
        ".xxxxxxXxxxxx.",
        "xxxxXXxxxxxxxx",
        "xxxxxxXxxxxxxx",
        "xxxxxxxxxxxxxx",
        ".xxxxxxxxxxxx.",
        "..xxxxxxxxxx..",
        "...xxxxxxxx...",
        "....xxxxxx....",
        ".....xxxx.....",
        "......xx......",
    ]

    for y, row in enumerate(heart):
        for x, ch in enumerate(row):
            bx = x + 1
            by = y + 2
            if ch == 'x':
                px(img, bx, by, c_body)
            elif ch == 'X':
                px(img, bx, by, c_light)

    # Shine
    px(img, 4, 4, c_shine)
    px(img, 5, 3, c_shine)

    # Dark edge at bottom
    px(img, 8, 12, c_dark)
    px(img, 7, 11, c_dark)
    px(img, 9, 11, c_dark)

    return img


def draw_coin_icon():
    """Coin icon 16x16."""
    img = make_image(16, 16)
    c_gold = PAL['gold']
    c_light = PAL['yellow']
    c_dark = PAL['orange']
    c_shine = PAL['white']
    c_center = PAL['brown']

    cx, cy = 8, 8

    # Circle
    for y in range(-6, 7):
        for x in range(-6, 7):
            dist = math.sqrt(x * x + y * y)
            if dist <= 6:
                if dist <= 4:
                    c = c_light
                elif dist <= 5:
                    c = c_gold
                else:
                    c = c_dark
                px(img, cx + x, cy + y, c)

    # Dollar sign / star in center
    px(img, 8, 5, c_center)
    px(img, 8, 6, c_center)
    px(img, 7, 6, c_center)
    px(img, 8, 7, c_center)
    px(img, 9, 7, c_center)
    px(img, 8, 8, c_center)
    px(img, 7, 8, c_center)
    px(img, 8, 9, c_center)
    px(img, 8, 10, c_center)

    # Shine
    px(img, 5, 4, c_shine)
    px(img, 6, 3, c_shine)

    return img


def draw_speed_icon():
    """Speed boost icon 16x16."""
    img = make_image(16, 16)
    c_bolt = PAL['yellow']
    c_light = PAL['white']
    c_dark = PAL['orange']
    c_glow = PAL['gold']

    # Lightning bolt shape
    bolt = [
        "......xx......",
        ".....xxx......",
        "....xxxx......",
        "...xxxxx......",
        "..xxxxxx......",
        ".xxxxxxxXX....",
        "......xxxx....",
        ".....xxxxx....",
        "....xxxxx.....",
        "...xxxxx......",
        "..xxxx........",
        ".xxx..........",
        "xx............",
    ]

    for y, row in enumerate(bolt):
        for x, ch in enumerate(row):
            bx = x + 1
            by = y + 1
            if ch == 'x':
                px(img, bx, by, c_bolt)
            elif ch == 'X':
                px(img, bx, by, c_light)

    # Glow around bolt
    # Speed lines
    px(img, 0, 5, c_glow)
    px(img, 0, 6, c_glow)
    px(img, 14, 8, c_glow)
    px(img, 15, 9, c_glow)

    return img


# ============================================================
# MAIN - Generate all sprites and save as JSON
# ============================================================

def main():
    print("TapToons v3.0 Sprite Generator")
    print("=" * 50)

    sprites = {}

    # 1. Player Characters
    print("\n[1/6] Generating player characters...")
    characters = {
        'sulley': draw_sulley,
        'mike': draw_mike,
        'rosie': draw_rosie,
        'drake': draw_drake,
        'gears': draw_gears,
        'rex': draw_rex,
    }

    frames = ['idle', 'run1', 'run2', 'jump']
    for name, func in characters.items():
        sprites[f"player_{name}"] = {}
        for frame in frames:
            img = func(frame)
            sprites[f"player_{name}"][frame] = img_to_base64(img)
            print(f"  - {name}/{frame} (32x32)")

    # 2. Enemies
    print("\n[2/6] Generating enemies...")
    enemies = {
        'badnik': draw_badnik,
        'bat': draw_bat,
        'slime': draw_slime,
    }

    for name, func in enemies.items():
        sprites[f"enemy_{name}"] = {}
        for i, frame in enumerate(['frame1', 'frame2']):
            img = func(frame)
            sprites[f"enemy_{name}"][frame] = img_to_base64(img)
            print(f"  - {name}/{frame} (32x32)")

    # 3. Collectibles
    print("\n[3/6] Generating collectibles...")

    # Ring (4 frames)
    sprites["collectible_ring"] = {}
    for i in range(4):
        img = draw_ring(i)
        sprites["collectible_ring"][f"frame{i+1}"] = img_to_base64(img)
        print(f"  - ring/frame{i+1} (32x32)")

    # Star (2 frames)
    sprites["collectible_star"] = {}
    for i in range(2):
        img = draw_star(i)
        sprites["collectible_star"][f"frame{i+1}"] = img_to_base64(img)
        print(f"  - star/frame{i+1} (32x32)")

    # Shield (2 frames)
    sprites["collectible_shield"] = {}
    for i in range(2):
        img = draw_shield(i)
        sprites["collectible_shield"][f"frame{i+1}"] = img_to_base64(img)
        print(f"  - shield/frame{i+1} (32x32)")

    # 4. Environment Tiles
    print("\n[4/6] Generating environment tiles...")
    sprites["tile_ground"] = img_to_base64(draw_ground_tile())
    print("  - ground (16x16)")
    sprites["tile_stone"] = img_to_base64(draw_stone_platform())
    print("  - stone (16x16)")
    sprites["tile_brick"] = img_to_base64(draw_brick_block())
    print("  - brick (16x16)")

    # 5. Parallax Backgrounds
    print("\n[5/6] Generating parallax backgrounds...")
    sprites["bg_sky"] = img_to_base64(draw_sky_layer())
    print("  - sky layer (480x270)")
    sprites["bg_mountains"] = img_to_base64(draw_mountains_layer())
    print("  - mountains layer (480x270)")
    sprites["bg_hills"] = img_to_base64(draw_hills_layer())
    print("  - hills layer (480x270)")
    sprites["bg_ground"] = img_to_base64(draw_ground_layer())
    print("  - ground layer (480x270)")

    # 6. UI Elements
    print("\n[6/6] Generating UI elements...")
    sprites["ui_heart"] = img_to_base64(draw_heart())
    print("  - heart (16x16)")
    sprites["ui_coin"] = img_to_base64(draw_coin_icon())
    print("  - coin (16x16)")
    sprites["ui_speed"] = img_to_base64(draw_speed_icon())
    print("  - speed (16x16)")

    # Save to JSON
    output_path = "/home/administrador/taptoons/sprites.json"
    with open(output_path, 'w') as f:
        json.dump(sprites, f, indent=2)

    # Stats
    total_sprites = 0
    for key, val in sprites.items():
        if isinstance(val, dict):
            total_sprites += len(val)
        else:
            total_sprites += 1

    file_size = len(json.dumps(sprites))
    print(f"\n{'=' * 50}")
    print(f"COMPLETE! Generated {total_sprites} sprites")
    print(f"Saved to: {output_path}")
    print(f"File size: {file_size / 1024:.1f} KB")
    print(f"{'=' * 50}")

    # Also generate a preview HTML
    preview_path = "/home/administrador/taptoons/sprite_preview.html"
    generate_preview_html(sprites, preview_path)
    print(f"Preview: {preview_path}")


def generate_preview_html(sprites, path):
    """Generate an HTML preview page for all sprites."""
    html = """<!DOCTYPE html>
<html>
<head>
<title>TapToons v3.0 - Sprite Preview</title>
<style>
body {
    background: #1a1c2c;
    color: #fff;
    font-family: 'Courier New', monospace;
    padding: 20px;
}
h1 { color: #ffcd75; text-align: center; }
h2 { color: #41a6f6; border-bottom: 1px solid #29366f; padding-bottom: 5px; }
h3 { color: #73efa1; }
.sprite-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 10px 0 30px 0;
}
.sprite-card {
    background: #29366f;
    border: 1px solid #3b5dc9;
    border-radius: 4px;
    padding: 10px;
    text-align: center;
}
.sprite-card img {
    image-rendering: pixelated;
    image-rendering: crisp-edges;
}
.sprite-card .label {
    font-size: 10px;
    color: #a7f070;
    margin-top: 5px;
}
.bg-preview img {
    width: 480px;
    height: 270px;
    image-rendering: pixelated;
    border: 1px solid #3b5dc9;
}
.small-sprite img { width: 64px; height: 64px; }
.large-sprite img { width: 128px; height: 128px; }
.tile-sprite img { width: 64px; height: 64px; }
</style>
</head>
<body>
<h1>TapToons v3.0 Sprite Assets</h1>
"""

    # Characters
    char_names = ['sulley', 'mike', 'rosie', 'drake', 'gears', 'rex']
    descriptions = {
        'sulley': 'Blue Furry Monster',
        'mike': 'Green One-Eye',
        'rosie': 'Pink Cutie w/ Bow',
        'drake': 'Purple Dragon',
        'gears': 'Orange Robot',
        'rex': 'Red Dinosaur',
    }

    html += "<h2>Player Characters (32x32, 4 frames each)</h2>\n"
    for name in char_names:
        key = f"player_{name}"
        html += f"<h3>{name.title()} - {descriptions[name]}</h3>\n"
        html += '<div class="sprite-grid">\n'
        for frame in ['idle', 'run1', 'run2', 'jump']:
            html += f'<div class="sprite-card large-sprite"><img src="{sprites[key][frame]}"><div class="label">{frame}</div></div>\n'
        html += '</div>\n'

    # Enemies
    html += "<h2>Enemies (32x32, 2 frames each)</h2>\n"
    enemy_desc = {'badnik': 'Red Shell Robot', 'bat': 'Purple Winged', 'slime': 'Green Blob'}
    for name in ['badnik', 'bat', 'slime']:
        key = f"enemy_{name}"
        html += f"<h3>{name.title()} - {enemy_desc[name]}</h3>\n"
        html += '<div class="sprite-grid">\n'
        for frame in ['frame1', 'frame2']:
            html += f'<div class="sprite-card large-sprite"><img src="{sprites[key][frame]}"><div class="label">{frame}</div></div>\n'
        html += '</div>\n'

    # Collectibles
    html += "<h2>Collectibles (32x32)</h2>\n"
    for coll_name, frame_count in [('ring', 4), ('star', 2), ('shield', 2)]:
        key = f"collectible_{coll_name}"
        html += f"<h3>{coll_name.title()}</h3>\n"
        html += '<div class="sprite-grid">\n'
        for i in range(frame_count):
            html += f'<div class="sprite-card large-sprite"><img src="{sprites[key][f"frame{i+1}"]}"><div class="label">frame{i+1}</div></div>\n'
        html += '</div>\n'

    # Tiles
    html += "<h2>Environment Tiles (16x16)</h2>\n"
    html += '<div class="sprite-grid">\n'
    for tname in ['ground', 'stone', 'brick']:
        key = f"tile_{tname}"
        html += f'<div class="sprite-card tile-sprite"><img src="{sprites[key]}"><div class="label">{tname}</div></div>\n'
    html += '</div>\n'

    # Backgrounds
    html += "<h2>Parallax Background Layers (480x270)</h2>\n"
    for layer in ['sky', 'mountains', 'hills', 'ground']:
        key = f"bg_{layer}"
        html += f"<h3>Layer: {layer.title()}</h3>\n"
        html += f'<div class="bg-preview"><img src="{sprites[key]}"></div>\n'

    # UI
    html += "<h2>UI Elements (16x16)</h2>\n"
    html += '<div class="sprite-grid">\n'
    for uname in ['heart', 'coin', 'speed']:
        key = f"ui_{uname}"
        html += f'<div class="sprite-card tile-sprite"><img src="{sprites[key]}"><div class="label">{uname}</div></div>\n'
    html += '</div>\n'

    html += """
<p style="text-align:center; color:#5d275d; margin-top:40px;">
Generated by TapToons v3.0 Sprite Generator<br>
In the name of the Lord Jesus Christ
</p>
</body>
</html>"""

    with open(path, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    main()
