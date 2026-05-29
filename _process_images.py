"""One-off: composite white-bg product renders onto the og-image Nord style.

Flood-fills the border-connected white background (so interior whites like the
"MotorLab" wordmark survive), then lays the product over a gradient + grid +
soft center glow that matches og-image.svg. Blueprint mode inverts line art
(dark lines on white -> cyan lines on dark) for the dimension drawing.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

# --- Nord palette (HANDOFF D1 / og-image.svg) ---
BG_TL = (0x1a, 0x1d, 0x23)   # gradient top-left
BG_BR = (0x2e, 0x34, 0x40)   # gradient bottom-right
GRID = (0x88, 0xc0, 0xd0)    # cyan grid lines
GRID_OPACITY = 0.15
GRID_STEP = 40
GLOW = (0x3b, 0x44, 0x52)    # center spotlight target (one step lighter)


def make_background(w, h, glow=True):
    """Diagonal gradient + soft radial glow + faint cyan grid (matches og-image)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (xx / max(w - 1, 1) + yy / max(h - 1, 1)) / 2.0          # 0..1 diagonal
    bg = np.empty((h, w, 3), np.float32)
    for c in range(3):
        bg[..., c] = BG_TL[c] + (BG_BR[c] - BG_TL[c]) * t

    if glow:
        cx, cy = w * 0.5, h * 0.46
        r = np.sqrt(((xx - cx) / (w * 0.55)) ** 2 + ((yy - cy) / (h * 0.55)) ** 2)
        g = np.clip(1.0 - r, 0.0, 1.0) ** 1.6                    # bright center, soft falloff
        for c in range(3):
            bg[..., c] += (GLOW[c] - bg[..., c]) * g * 0.55

    # grid lines blended at low opacity
    line = np.zeros((h, w), np.float32)
    line[::GRID_STEP, :] = 1.0
    line[:, ::GRID_STEP] = 1.0
    for c in range(3):
        bg[..., c] = bg[..., c] * (1 - line * GRID_OPACITY) + GRID[c] * (line * GRID_OPACITY)

    return np.clip(bg, 0, 255)


def bg_mask(img, thresh=170):
    """Boolean mask of border-connected near-white pixels (the backdrop)."""
    work = img.copy()
    seed = (255, 0, 255)
    w, h = work.size
    for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(work, pt, seed, thresh=thresh)
    arr = np.asarray(work)
    return (arr[..., 0] == 255) & (arr[..., 1] == 0) & (arr[..., 2] == 255)


def compose_product(path, out):
    img = Image.open(path).convert("RGB")
    border = bg_mask(img)

    arr = np.asarray(img).astype(int)
    minc = arr.min(2)
    maxc = arr.max(2)
    sat = maxc - minc
    bri = arr.mean(2)

    # Solid bright-metallic blobs (the clamp) — erode first so thin AA edges
    # around the logo letters don't count, leaving only chunky metal regions.
    metal = (~border) & (bri >= 138) & (bri <= 238) & (sat < 40) & (minc < 238)
    metal_zone = ndimage.binary_dilation(
        ndimage.binary_erosion(metal, iterations=3), iterations=5)

    # Interior near-white = either logo paint (sits on the dark housing) or a
    # see-through pocket in the mount. A pocket is flagged when it (a) hugs the
    # red clamp, (b) hugs bare metal, or (c) is a chunky blob (a window) — the
    # last survives a 6px erosion, whereas thin logo strokes erode to nothing.
    interior = (minc >= 240) & ~border
    lbl, n = ndimage.label(interior)
    logo = np.zeros_like(interior)
    pocket = np.zeros_like(interior)
    for cid in range(1, n + 1):
        comp = lbl == cid
        ring = ndimage.binary_dilation(comp, iterations=4) & ~comp
        touches_red = sat[ring].max() > 80
        touches_metal = (ring & metal_zone).sum() / max(ring.sum(), 1) > 0.08
        chunky = ndimage.binary_erosion(comp, iterations=6).sum() / comp.sum() > 0.15
        if touches_red or touches_metal or chunky:   # backdrop pocket, not logo
            pocket |= comp
        else:                              # surrounded by housing -> logo paint
            logo |= comp

    protect = ndimage.binary_dilation(logo, iterations=3)
    pocket = ndimage.binary_dilation(pocket, iterations=2)
    # neutral light-gray AA halo left around interior pockets -> fold into background
    halo = (~border) & (minc >= 178) & (minc <= 244) & (sat <= 16) & ~protect
    mask = border | pocket | halo

    # feather: 255 = keep product, 0 = show background
    keep = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8), "L")
    keep = keep.filter(ImageFilter.GaussianBlur(1.2))
    a = np.asarray(keep, np.float32)[..., None] / 255.0

    w, h = img.size
    bg = make_background(w, h)
    prod = np.asarray(img, np.float32)
    result = prod * a + bg * (1 - a)
    Image.fromarray(np.clip(result, 0, 255).astype(np.uint8)).save(out)
    cov = 100 * (1 - mask.mean())
    print(f"  {out}  product coverage {cov:4.1f}%")


def compose_blueprint(path, out):
    """Line art on white -> cyan/light lines on Nord dark (blueprint look)."""
    img = Image.open(path).convert("L")
    w, h = img.size
    lum = np.asarray(img, np.float32) / 255.0
    ink = np.clip((1.0 - lum) * 1.15, 0, 1)[..., None]            # darker source = stronger line
    bg = make_background(w, h, glow=False)
    LINE = np.array([0xd8, 0xde, 0xe9], np.float32)              # nord snow for lines
    result = bg * (1 - ink) + LINE * ink
    Image.fromarray(np.clip(result, 0, 255).astype(np.uint8)).save(out)
    print(f"  {out}  blueprint")


if __name__ == "__main__":
    import os
    os.makedirs("images/og", exist_ok=True)
    for n in range(1, 7):
        compose_product(f"images/MotorLab_V1-{n}.jpg", f"images/og/MotorLab_V1-{n}.png")
    compose_blueprint("images/MotorLab_3D_20260515.PNG", "images/og/MotorLab_dimensions.png")
    print("done")
