# -*- coding: utf-8 -*-
"""Generate Thailand-themed preview + icons for the trip site."""
import os
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display

FONTS = "C:/Windows/Fonts"
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Thai flag colours
RED   = (165, 25, 49)     # #A51931
WHITE = (244, 245, 248)   # #F4F5F8
BLUE  = (45, 42, 74)      # #2D2A4A
# site palette
PAPER = (246, 238, 220)   # cream
LEMON = (232, 180, 58)    # gold
INK_BLUE = (28, 26, 48)   # blue-deep

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

FRANK = "FrankRuhlHofshi-Bold.otf"       # Hebrew + latin serif, heavy
DAVID = "DavidLibre-Bold.ttf"
SERIF = "timesbd.ttf"
SANS  = "arialbd.ttf"

def he(s):
    """Reorder Hebrew for correct visual (RTL) rendering in PIL."""
    return get_display(s)

def flag_stripes(w, h):
    """Thai flag: 5 horizontal stripes 1:1:2:1:1 (red/white/blue/white/red)."""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    unit = h / 6.0
    bands = [(RED, 1), (WHITE, 1), (BLUE, 2), (WHITE, 1), (RED, 1)]
    y = 0.0
    for colour, n in bands:
        d.rectangle([0, int(round(y)), w, int(round(y + unit * n))], fill=colour)
        y += unit * n
    return img

def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], radius=r, fill=255)
    return m

# ---------------------------------------------------------------- PREVIEW
def make_preview(path):
    W, H = 1200, 630
    img = flag_stripes(W, H)
    # subtle darkening so the card/text reads on any stripe
    shade = Image.new("RGBA", (W, H), (10, 9, 20, 60))
    img = Image.alpha_composite(img.convert("RGBA"), shade)
    d = ImageDraw.Draw(img)

    # centred translucent card
    cw, ch = 780, 470
    cx, cy = (W - cw) // 2, (H - ch) // 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cw, ch], radius=28, fill=(28, 26, 48, 150),
                         outline=(246, 238, 220, 90), width=2)
    img.alpha_composite(card, (cx, cy))
    d = ImageDraw.Draw(img)

    midx = W // 2
    # top small-caps latin
    f_top = font(SERIF, 40)
    d.text((midx, cy + 78), "T H A I L A N D  ·  2 0 2 6", font=f_top,
           fill=LEMON, anchor="mm")
    # big Hebrew title
    f_title = font(FRANK, 165)
    d.text((midx, cy + 195), he("תאילנד"), font=f_title, fill=PAPER, anchor="mm")
    # subtitle Hebrew
    f_sub = font(DAVID, 40)
    d.text((midx, cy + 300), he("מקדשים, איים וכרך — שלושה שבועות במזרח"),
           font=f_sub, fill=(246, 238, 220), anchor="mm")

    # city chips
    chips = ["Bangkok", "Ko Samui", "Chiang Mai"]
    f_chip = font(SERIF, 34)
    gap = 26
    padx = 26
    sizes = [d.textbbox((0, 0), c, font=f_chip) for c in chips]
    widths = [(b[2] - b[0]) + padx * 2 for b in sizes]
    star_w = 44
    total = sum(widths) + star_w * (len(chips) - 1) + gap * 2 * (len(chips) - 1)
    x = midx - total / 2
    chy = cy + 400
    ch_h = 60
    for i, c in enumerate(chips):
        cwd = widths[i]
        d.rounded_rectangle([x, chy - ch_h / 2, x + cwd, chy + ch_h / 2],
                            radius=ch_h / 2, outline=(246, 238, 220, 160), width=2)
        d.text((x + cwd / 2, chy), c, font=f_chip, fill=PAPER, anchor="mm")
        x += cwd
        if i < len(chips) - 1:
            x += gap
            # small gold diamond separator
            sx, sy, s = x + star_w / 2, chy, 9
            d.polygon([(sx, sy - s), (sx + s, sy), (sx, sy + s), (sx - s, sy)], fill=LEMON)
            x += star_w + gap

    img.convert("RGB").save(path, "JPEG", quality=90)
    print("wrote", path)

# ---------------------------------------------------------------- ICONS
def make_icon(path, size, radius_frac=0.18, num_frac=0.42, pad=0):
    """Rounded Thai-flag tile with gold 2026."""
    ss = 4  # supersample
    w = size * ss
    inner = w - pad * ss * 2
    flag = flag_stripes(inner, inner)
    tile = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    r = int(inner * radius_frac)
    flag.putalpha(rounded_mask(inner, inner, r))
    tile.alpha_composite(flag.convert("RGBA"), (pad * ss, pad * ss))
    d = ImageDraw.Draw(tile)
    fnum = font(SERIF, int(inner * num_frac))
    d.text((w // 2, w // 2), "2026", font=fnum, fill=LEMON, anchor="mm",
           stroke_width=max(2, int(inner * 0.012)), stroke_fill=INK_BLUE)
    tile = tile.resize((size, size), Image.LANCZOS)
    tile.save(path, "PNG")
    print("wrote", path, size)

make_preview(os.path.join(OUT, "preview.jpg"))
make_icon(os.path.join(OUT, "icon-512.png"), 512)
make_icon(os.path.join(OUT, "icon-192.png"), 192)
# maskable: keep flag full-bleed but pull 2026 into the safe centre (smaller)
make_icon(os.path.join(OUT, "icon-maskable-512.png"), 512, radius_frac=0.0, num_frac=0.30)
make_icon(os.path.join(OUT, "apple-touch-icon.png"), 180)
