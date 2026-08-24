#!/usr/bin/env python3
"""Compose Barbakaï OS branding assets with exact Unicode text."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
SRC_ICON = ROOT / "branding" / "source" / "barbakai-icon-source.jpg"
SRC_WALL = ROOT / "branding" / "source" / "barbakai-wallpaper-source.jpg"

FONTS = Path(r"C:\Windows\Fonts")
FONT_TITLE = FONTS / "segoeuib.ttf"  # Segoe UI Bold — supports ï
FONT_TITLE_FALLBACK = FONTS / "arialbd.ttf"
FONT_BODY = FONTS / "segoeui.ttf"
FONT_LIGHT = FONTS / "segoeuil.ttf"

CYAN = (0, 212, 255, 255)
MAGENTA = (196, 77, 255, 255)
GOLD = (232, 196, 92, 255)
WHITE = (245, 250, 255, 255)
NEAR_WHITE = (230, 240, 255, 255)


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    alt = FONT_TITLE_FALLBACK if path != FONT_TITLE_FALLBACK else FONT_BODY
    return ImageFont.truetype(str(alt), size)


def glow_text(
    canvas: Image.Image,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    glow: tuple[int, int, int, int],
    radius: int = 16,
    glow_passes: int = 3,
) -> None:
    """Draw glowing text onto an RGBA canvas. xy is top-left of the text bbox."""
    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    for _ in range(glow_passes):
        d.text(xy, text, font=fnt, fill=glow, anchor="lt")
    tmp = tmp.filter(ImageFilter.GaussianBlur(radius=radius))
    canvas.alpha_composite(tmp)
    draw = ImageDraw.Draw(canvas)
    draw.text(xy, text, font=fnt, fill=fill, anchor="lt")


def text_size(fnt: ImageFont.FreeTypeFont, text: str) -> tuple[int, int]:
    bbox = fnt.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def make_wordmark(width: int = 1800, height: int = 420) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    title = "Barbakaï"
    tag = "THE GAME CONTROL"
    f_title = font(FONT_TITLE, 168)
    f_tag = font(FONT_LIGHT if FONT_LIGHT.exists() else FONT_BODY, 36)

    tw, th = text_size(f_title, title)
    tag_w, tag_h = text_size(f_tag, tag)
    title_x = (width - tw) // 2
    title_y = 36
    glow_text(img, (title_x, title_y), title, f_title, WHITE, (0, 180, 255, 210), radius=16)
    glow_text(img, (title_x, title_y), title, f_title, WHITE, (180, 60, 255, 90), radius=24)

    line_y = title_y + th + 18
    line_left = (width - tw) // 2
    line_right = line_left + tw
    draw = ImageDraw.Draw(img)
    glow_line = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(glow_line).rectangle(
        (line_left, line_y, line_right, line_y + 8),
        fill=(0, 212, 255, 180),
    )
    img.alpha_composite(glow_line.filter(ImageFilter.GaussianBlur(radius=4)))
    draw.rectangle((line_left, line_y + 2, line_right, line_y + 6), fill=(0, 220, 255, 255))

    tag_x = (width - tag_w) // 2
    tag_y = line_y + 18
    glow_text(img, (tag_x, tag_y), tag, f_tag, GOLD, (232, 196, 92, 120), radius=6)
    return tight_crop_on_dark(img, threshold=8, pad=36)


def make_wordmark_compact(width: int = 1600, height: int = 280) -> Image.Image:
    """Single-line Barbakaï for plymouth / lockup."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    title = "Barbakaï"
    f_title = font(FONT_TITLE, 160)
    tw, th = text_size(f_title, title)
    x = (width - tw) // 2
    y = (height - th) // 2 - 10
    glow_text(img, (x, y), title, f_title, WHITE, (0, 180, 255, 200), radius=14)
    return tight_crop_on_dark(img, threshold=8, pad=28)


def tight_crop_on_dark(im: Image.Image, threshold: int = 18, pad: int = 24) -> Image.Image:
    if im.mode == "RGBA":
        bbox = im.split()[-1].getbbox()
    else:
        gray = im.convert("L")
        bbox = gray.point(lambda p: 255 if p > threshold else 0).getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad)
    b = min(im.height, b + pad)
    return im.crop((l, t, r, b))


def icon_to_png(src: Path, size: int | None = None) -> Image.Image:
    im = Image.open(src).convert("RGBA")
    if size:
        im = im.resize((size, size), Image.Resampling.LANCZOS)
    return im


def make_full_logo(icon: Image.Image, wordmark: Image.Image) -> Image.Image:
    icon_c = tight_crop_on_dark(icon, threshold=12, pad=20)
    icon_h = 420
    ratio = icon_h / icon_c.height
    icon_r = icon_c.resize((int(icon_c.width * ratio), icon_h), Image.Resampling.LANCZOS)
    wm = wordmark.copy()
    wm_h = 280
    wm_ratio = wm_h / wm.height
    wm = wm.resize((int(wm.width * wm_ratio), wm_h), Image.Resampling.LANCZOS)
    gap = 48
    pad = 36
    w = icon_r.width + gap + wm.width + pad * 2
    h = max(icon_r.height, wm.height) + pad * 2
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    iy = (h - icon_r.height) // 2
    wy = (h - wm.height) // 2
    canvas.alpha_composite(icon_r, (pad, iy))
    canvas.alpha_composite(wm, (pad + icon_r.width + gap, wy))
    return canvas


def overlay_wallpaper(wall: Image.Image, wordmark: Image.Image) -> Image.Image:
    canvas = wall.convert("RGBA")
    # Upscale to 2560x1440
    canvas = canvas.resize((2560, 1440), Image.Resampling.LANCZOS)
    # Slight contrast
    canvas = ImageEnhance.Contrast(canvas).enhance(1.06)
    canvas = ImageEnhance.Color(canvas).enhance(1.08)

    wm = wordmark.copy()
    target_w = 1100
    ratio = target_w / wm.width
    wm = wm.resize((target_w, int(wm.height * ratio)), Image.Resampling.LANCZOS)

    x = (canvas.width - wm.width) // 2
    y = canvas.height - wm.height - 70

    # Dark vignette behind the wordmark for readability
    shade = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle(
        (x - 40, y - 10, x + wm.width + 40, y + wm.height + 10),
        radius=28,
        fill=(0, 0, 0, 110),
    )
    shade = shade.filter(ImageFilter.GaussianBlur(radius=18))
    canvas.alpha_composite(shade)
    canvas.alpha_composite(wm, (x, y))
    return canvas.convert("RGB")


def save_jpeg(im: Image.Image, path: Path, quality: int = 92) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(path, "JPEG", quality=quality, optimize=True)


def save_png(im: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG", optimize=True)


def copy(src: Path, *dests: Path) -> None:
    for d in dests:
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, d)


def main() -> None:
    icon = icon_to_png(SRC_ICON)
    wall_src = Image.open(SRC_WALL).convert("RGB")
    wordmark = make_wordmark()
    wordmark_compact = make_wordmark_compact()
    wallpaper = overlay_wallpaper(wall_src, wordmark)
    full = make_full_logo(icon, wordmark)

    plymouth_logo = icon.resize((480, 480), Image.Resampling.LANCZOS)
    plymouth_word = wordmark_compact.resize((720, 126), Image.Resampling.LANCZOS)

    branding = ROOT / "branding" / "out"
    branding.mkdir(parents=True, exist_ok=True)

    save_png(icon, branding / "barbakai-icon.png")
    save_png(wordmark, branding / "barbakai-wordmark.png")
    save_png(full, branding / "barbakai-logo-full.png")
    save_jpeg(wallpaper, branding / "barbakai-wallpaper.jpeg")
    save_png(plymouth_logo, branding / "plymouth-logo.png")
    save_png(plymouth_word, branding / "plymouth-wordmark.png")

    share = ROOT / "system_files" / "usr" / "share"

    icon_dests = [
        share / "icons" / "barbakai" / "barbakai-icon.png",
        share / "barbakai" / "branding" / "images" / "barbakai-icon.png",
        share / "pixmaps" / "barbakai.png",
        share / "icons" / "hicolor" / "512x512" / "apps" / "barbakai.png",
        share / "plymouth" / "themes" / "barbakai" / "images" / "logo.png",
        # Keep legacy NextOS paths so older configs still resolve
        share / "icons" / "nexusos" / "nextos-icon.png",
        share / "nextos" / "branding" / "images" / "nextos-icon.png",
    ]
    for dest in icon_dests:
        save_png(icon, dest)

    icon256 = icon.resize((256, 256), Image.Resampling.LANCZOS)
    save_png(icon256, share / "icons" / "hicolor" / "256x256" / "apps" / "barbakai.png")

    save_png(full, share / "icons" / "barbakai" / "barbakai-logo-full.png")
    save_png(full, share / "barbakai" / "branding" / "images" / "barbakai-logo-full.png")
    save_png(full, share / "icons" / "nexusos" / "nextos-logo-full.png")
    save_png(full, share / "nextos" / "branding" / "images" / "nextos-logo-full.png")

    save_png(wordmark, share / "icons" / "barbakai" / "barbakai-logo.png")
    save_png(wordmark, share / "barbakai" / "branding" / "images" / "barbakai-logo.png")
    save_png(wordmark, share / "icons" / "nexusos" / "nextos-logo.png")
    save_png(wordmark, share / "nextos" / "branding" / "images" / "nextos-logo.png")

    save_png(plymouth_logo, share / "plymouth" / "themes" / "barbakai" / "images" / "logo.png")
    save_png(plymouth_word, share / "plymouth" / "themes" / "barbakai" / "images" / "wordmark.png")

    wall_dests = [
        share / "barbakai" / "wallpapers" / "barbakai-wallpaper.jpeg",
        share / "wallpapers" / "Barbakai" / "contents" / "images" / "2560x1440.jpg",
        share / "wallpapers" / "nexusos" / "nextos-wallpaper.jpeg",
        share / "nextos" / "wallpapers" / "nextos-wallpaper.jpeg",
        share / "backgrounds" / "barbakai" / "barbakai-wallpaper.jpeg",
        share / "sddm" / "themes" / "breeze" / "barbakai-wallpaper.jpeg",
    ]
    for dest in wall_dests:
        save_jpeg(wallpaper, dest)

    # Also keep a 1920x1080 variant for smaller screens / SDDM
    wall_1080 = wallpaper.resize((1920, 1080), Image.Resampling.LANCZOS)
    save_jpeg(
        wall_1080,
        share / "wallpapers" / "Barbakai" / "contents" / "images" / "1920x1080.jpg",
    )

    print("Branding assets written.")
    print(f"  icon     {icon.size}")
    print(f"  wordmark {wordmark.size}")
    print(f"  full     {full.size}")
    print(f"  wall     {wallpaper.size}")


if __name__ == "__main__":
    main()
