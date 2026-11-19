#!/usr/bin/env python3
"""characterlens_post.py - finishing passes for CharacterLens styles.

The camera shader does the optics and pixel grids. This does what a camera
can't: colour depth + dithering, palettes, tape/sensor noise, overlays,
light leaks, and time-based effects (rolling shutter, slit-scan).

Usage
  python characterlens_post.py LOOK INPUT OUTPUT [options]
    INPUT   an image, or a folder of frames (sorted by name)
    OUTPUT  an image path, or a folder (created) for sequences

  python characterlens_post.py --list            # show all looks

Examples
  python characterlens_post.py ps1      renders/ out_ps1/
  python characterlens_post.py vhs      frame_0001.png vhs.png --timestamp
  python characterlens_post.py rolling  subframes/ out/ --subframes 8
  python characterlens_post.py slitscan frames/ slit.png

Needs numpy + Pillow. EXR input also needs `imageio` (or OpenImageIO).
"""
import argparse, datetime, glob, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ------------------------------------------------------------------ io
EXTS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".exr")


def load(path):
    if path.lower().endswith(".exr"):
        try:
            import imageio.v3 as iio
            a = np.asarray(iio.imread(path), dtype=np.float32)[..., :3]
        except Exception:
            try:
                import OpenImageIO as oiio
                a = oiio.ImageInput.open(path).read_image("float")[..., :3]
            except Exception:
                sys.exit("EXR needs imageio or OpenImageIO - or render PNG/TIFF instead.")
        return np.clip(a, 0, None) ** (1 / 2.2)          # linear -> display-ish
    im = Image.open(path).convert("RGB")
    return np.asarray(im, dtype=np.float32) / 255.0


def save(a, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path)


def frames_in(path):
    if os.path.isdir(path):
        return sorted(p for p in glob.glob(os.path.join(path, "*")) if p.lower().endswith(EXTS))
    return [path]


# ------------------------------------------------------------ helpers
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16.0 - 0.5


def grid_size(a, lines):
    return max(a.shape[0] / float(lines), 1.0)


def bayer(a, lines):
    """Bayer threshold map in the style's pixel grid (so dither cells match pixels)."""
    h, w = a.shape[:2]
    ps = grid_size(a, lines)
    y = (np.arange(h) / ps).astype(int) % 4
    x = (np.arange(w) / ps).astype(int) % 4
    return BAYER4[y[:, None], x[None, :]][..., None]


def quantize(a, bits, dither=None, amount=1.0):
    lv = 2 ** bits - 1
    if dither is not None:
        a = a + dither * amount / lv
    return np.round(np.clip(a, 0, 1) * lv) / lv


def luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def blur(a, r):
    if r <= 0:
        return a
    return np.stack([np.asarray(Image.fromarray((np.clip(a[..., c], 0, 1) * 255).astype(np.uint8))
                                .filter(ImageFilter.GaussianBlur(r)), np.float32) / 255 for c in range(a.shape[2])], -1)


def hblur(a, r):
    """Horizontal-only box blur (tape chroma)."""
    r = int(max(r, 1))
    k = np.ones(2 * r + 1) / (2 * r + 1)
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, a)


def to_ycc(a):
    y = luma(a)
    return y, a[..., 2] - y, a[..., 0] - y


def from_ycc(y, cb, cr):
    r = cr + y
    b = cb + y
    g = (y - 0.2126 * r - 0.0722 * b) / 0.7152
    return np.stack([r, g, b], -1)


def grain(a, rng, amount, size=1.0, mono=True):
    h, w = a.shape[:2]
    sh, sw = max(int(h / size), 1), max(int(w / size), 1)
    n = rng.standard_normal((sh, sw, 1 if mono else 3)).astype(np.float32)
    if size != 1.0:
        n = np.stack([np.asarray(Image.fromarray(n[..., c]).resize((w, h), Image.BILINEAR)) for c in range(n.shape[2])], -1)
    return a + n * amount


def bloom(a, thresh=0.7, radius=12, amount=0.5):
    hi = np.clip(a - thresh, 0, None) / (1 - thresh)
    return a + blur(hi, radius) * amount


def font(size):
    for f in ("consola.ttf", "DejaVuSansMono.ttf", "Courier New.ttf", "cour.ttf", "Menlo.ttc"):
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            pass
    return ImageFont.load_default()


def overlay_text(a, lines, pos="tl", color=(255, 255, 255), scale=0.045, shadow=True):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    h, w = a.shape[:2]
    fs = max(int(h * scale), 10)
    f = font(fs)
    pad = int(fs * 0.8)
    for i, text in enumerate(lines):
        tw = d.textlength(text, font=f)
        x = pad if pos[1] == "l" else w - pad - tw
        y = pad + i * int(fs * 1.25) if pos[0] == "t" else h - pad - (len(lines) - i) * int(fs * 1.25)
        if shadow:
            d.text((x + 2, y + 2), text, font=f, fill=(0, 0, 0))
        d.text((x, y), text, font=f, fill=color)
    return np.asarray(im, np.float32) / 255


def stamp(frame, fps, start):
    t = start + datetime.timedelta(seconds=frame / float(fps))
    return t


def light_leak(a, rng, strength=0.6):
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = a.copy()
    for _ in range(rng.integers(1, 3)):
        side = rng.integers(0, 4)
        cx = [0, w, rng.uniform(0, w), rng.uniform(0, w)][side]
        cy = [rng.uniform(0, h), rng.uniform(0, h), 0, h][side]
        rad = rng.uniform(0.3, 0.7) * max(h, w)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / rad
        m = np.clip(1 - d, 0, 1) ** 2 * strength
        col = np.array(rng.choice([[1.0, 0.45, 0.1], [1.0, 0.25, 0.15], [1.0, 0.7, 0.3], [0.9, 0.2, 0.5]]), np.float32)
        out = 1 - (1 - out) * (1 - m[..., None] * col)          # screen
    return out


def curve_s(a, amount=0.15):
    """S-curve contrast."""
    a = np.clip(a, 0, 1)
    return a + (a * a * (3 - 2 * a) - a) * amount * 2


def saturate(a, s):
    y = luma(a)[..., None]
    return y + (a - y) * s


# --------------------------------------------------------------- looks
def look_ps1(a, i, rng, o):
    return quantize(a, 5, bayer(a, o.lines or 240), 1.0)        # 15-bit colour + 4x4 ordered dither


def look_n64(a, i, rng, o):
    a = blur(a, grid_size(a, o.lines or 240) * 0.35)
    return quantize(a, 5, bayer(a, o.lines or 240), 0.6)


def look_doom(a, i, rng, o):
    lines = o.lines or 200
    h, w = a.shape[:2]
    sw, sh = max(int(w / grid_size(a, lines)), 1), lines
    small = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((sw, sh), Image.NEAREST)
    small = small.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    return np.asarray(small.resize((w, h), Image.NEAREST), np.float32) / 255


def look_gameboy(a, i, rng, o):
    pal = np.array([[0.06, 0.22, 0.06], [0.19, 0.38, 0.19], [0.55, 0.67, 0.06], [0.61, 0.74, 0.06]], np.float32)
    if o.gray:
        pal = np.array([[0.0, 0.0, 0.0], [0.33, 0.33, 0.33], [0.66, 0.66, 0.66], [1.0, 1.0, 1.0]], np.float32)
    y = np.clip(luma(a) * 1.15, 0, 1)
    y = np.clip(y + bayer(a, o.lines or 112)[..., 0] / 3.0, 0, 1)
    idx = np.clip(np.round(y * 3), 0, 3).astype(int)
    return pal[idx]


def look_crt(a, i, rng, o):
    a = bloom(a, 0.6, a.shape[0] / 90, 0.45)
    return grain(a, rng, 0.012)


def look_vhs(a, i, rng, o):
    h, w = a.shape[:2]
    y, cb, cr = to_ycc(a)
    cb = hblur(np.roll(cb, int(w * 0.004), 1), w / 90)            # chroma: low bandwidth, delayed
    cr = hblur(np.roll(cr, int(w * 0.004), 1), w / 90)
    y = y + 0.5 * (y - hblur(y, w / 300)) * 0.8                     # edge ringing / sharpening halo
    y = y + 0.18 * np.roll(hblur(y, 3), int(w * 0.012), 1) - 0.18 * hblur(y, 3) * 0.5  # ghost
    y = y + rng.standard_normal((h, w)).astype(np.float32) * 0.035
    cb = cb + hblur(rng.standard_normal((h, w)).astype(np.float32), w / 120) * 0.08
    cr = cr + hblur(rng.standard_normal((h, w)).astype(np.float32), w / 120) * 0.08
    out = from_ycc(y, cb * 0.85, cr * 0.85)
    # tracking band drifting down the frame
    band_y = int(((i * 0.013 + rng.uniform(0, 0.02)) % 1.0) * h)
    bh = max(int(h * 0.025), 2)
    seg = out[band_y:band_y + bh]
    if seg.size:
        seg[:] = np.roll(seg, int(w * 0.03), 1) * 0.7 + rng.random(seg.shape).astype(np.float32) * 0.35
    # head-switching noise at the bottom
    hs = max(int(h * 0.018), 2)
    out[-hs:] = np.roll(out[-hs:], int(w * 0.05), 1) * 0.6 + rng.random((hs, w, 3)).astype(np.float32) * 0.3
    if o.timestamp:
        t = stamp(i, o.fps, o.start)
        out = overlay_text(out, ["PLAY >", "", t.strftime("%b %d %Y").upper(), t.strftime("%H:%M:%S")],
                           "tl", (235, 235, 235), 0.05)
    return out


def look_nightvision(a, i, rng, o):
    y = np.clip(luma(a) * 1.25, 0, 1) ** 1.1
    y = bloom(np.repeat(y[..., None], 3, -1), 0.65, a.shape[0] / 60, 0.6)[..., 0]
    y = y + rng.standard_normal(y.shape).astype(np.float32) * 0.09 * (1.1 - y * 0.5)
    y = y * (0.92 + 0.08 * rng.random())                           # tube flicker
    return np.stack([y * 0.25, y * 0.95, y * 0.3], -1)


def look_cctv(a, i, rng, o):
    a = saturate(a, 0.35)
    a = grain(a, rng, 0.03, 1.5)
    a = quantize(a, 6)
    t = stamp(i, o.fps, o.start)
    return overlay_text(a, ["CAM %02d" % o.cam, t.strftime("%Y-%m-%d  %H:%M:%S")], "tl", (240, 240, 240), 0.04)


def look_dashcam(a, i, rng, o):
    a = curve_s(saturate(a, 1.1), 0.1)
    a = grain(a, rng, 0.015)
    t = stamp(i, o.fps, o.start)
    return overlay_text(a, [t.strftime("%Y/%m/%d %H:%M:%S") + "   %d KM/H" % o.speed], "bl", (255, 255, 255), 0.035)


def look_webcam(a, i, rng, o):
    h, w = a.shape[:2]
    a = saturate(curve_s(a, 0.08), 1.25) * 1.12 + 0.03
    a = grain(a, rng, 0.03, 2.0, mono=False)
    sm = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((320, max(int(320 * h / w), 1)), Image.BILINEAR)
    import io
    buf = io.BytesIO(); sm.save(buf, "JPEG", quality=18); buf.seek(0)
    return np.asarray(Image.open(buf).convert("RGB").resize((w, h), Image.BILINEAR), np.float32) / 255


def look_disposable(a, i, rng, o):
    a = curve_s(saturate(a, 1.15), 0.12) * np.array([1.04, 1.0, 0.92], np.float32)
    a = grain(a, rng, 0.045, 1.6)
    if rng.random() < o.leak:
        a = light_leak(a, rng, 0.5)
    return a


def look_toy(a, i, rng, o):
    a = saturate(a, 1.35)
    a = np.stack([curve_s(a[..., 0], 0.35), curve_s(a[..., 1], 0.2), a[..., 2] * 0.85 + 0.08], -1)   # cross-process
    a = grain(a, rng, 0.05, 2.0)
    return light_leak(a, rng, 0.7) if rng.random() < max(o.leak, 0.6) else a


def look_super8(a, i, rng, o):
    a = curve_s(saturate(a, 1.1), 0.15) * np.array([1.05, 1.0, 0.88], np.float32)
    a = a * (0.93 + 0.1 * rng.random())                            # exposure flicker
    a = grain(a, rng, 0.07, 2.2)
    h, w = a.shape[:2]
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for _ in range(rng.integers(0, 6)):                           # dust
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(1, h / 250)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(20, 15, 10) if rng.random() < 0.7 else (240, 235, 220))
    if rng.random() < 0.3:                                        # scratch
        x = rng.uniform(0, w)
        d.line([(x, 0), (x + rng.uniform(-5, 5), h)], fill=(230, 225, 210), width=1)
    a = np.asarray(im, np.float32) / 255
    return light_leak(a, rng, 0.35) if rng.random() < o.leak * 0.5 else a


def look_tiltshift(a, i, rng, o):
    return curve_s(saturate(a, 1.45), 0.18)


def look_grain(a, i, rng, o):
    return grain(a, rng, 0.05 * o.amount, 1.5)


def look_rolling(frames, o):
    """Rolling shutter: every --subframes consecutive renders make one frame;
    row r comes from sub-frame floor(r / H * N). Render the shot at N x the
    frame rate (or with N sub-steps) so time differs down the frame."""
    n = o.subframes
    for k in range(0, len(frames) - n + 1, n):
        stack = [load(p) for p in frames[k:k + n]]
        h = stack[0].shape[0]
        out = np.empty_like(stack[0])
        for r in range(h):
            out[r] = stack[min(int(r / h * n), n - 1)][r]
        yield k // n, out


def look_slitscan(frames, o):
    """Slit-scan: column c of the output comes from frame c * len/width."""
    first = load(frames[0])
    h, w = first.shape[:2]
    out = np.empty_like(first)
    for c in range(w):
        f = frames[min(int(c / w * len(frames)), len(frames) - 1)]
        col = load(f)[:, c] if f != frames[0] else first[:, c]
        out[:, c] = col
    yield 0, out


LOOKS = {
    "ps1": (look_ps1, "15-bit colour + ordered dither (use with [Style] PS1)"),
    "n64": (look_n64, "soft filtered 16-bit colour (use with [Style] N64)"),
    "doom": (look_doom, "256-colour palette at 320x200 (use with [Style] Doom)"),
    "gameboy": (look_gameboy, "4-tone green palette, dithered (--gray for Game Boy Camera prints)"),
    "crt": (look_crt, "phosphor bloom + faint noise (use with [Style] CRT TV)"),
    "vhs": (look_vhs, "chroma bleed, ringing, noise, tracking band, head-switch (--timestamp)"),
    "nightvision": (look_nightvision, "monochrome green, gain, bloom, grain"),
    "cctv": (look_cctv, "desaturated, noisy, camera ID + timestamp"),
    "dashcam": (look_dashcam, "punchy, timestamp + speed overlay"),
    "webcam": (look_webcam, "2000s webcam: low-res JPEG blocks, noise, oversaturated"),
    "disposable": (look_disposable, "warm film, grain, occasional light leak"),
    "toy": (look_toy, "cross-processed colour, grain, light leaks (Holga)"),
    "super8": (look_super8, "warm, heavy grain, flicker, dust and scratches"),
    "tiltshift": (look_tiltshift, "saturation + contrast for the miniature look"),
    "grain": (look_grain, "plain film grain (--amount)"),
    "rolling": (None, "rolling shutter from sub-frame renders (--subframes N)"),
    "slitscan": (None, "slit-scan: each column from a later frame"),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("look", nargs="?")
    ap.add_argument("input", nargs="?")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--lines", type=int, default=0, help="pixel grid lines (match the shader's Pixel lines)")
    ap.add_argument("--fps", type=float, default=25)
    ap.add_argument("--start", default=None, help="timestamp start, e.g. '2026-11-19 13:05:00'")
    ap.add_argument("--timestamp", action="store_true")
    ap.add_argument("--cam", type=int, default=1)
    ap.add_argument("--speed", type=int, default=48)
    ap.add_argument("--leak", type=float, default=0.3, help="light-leak probability per frame")
    ap.add_argument("--gray", action="store_true")
    ap.add_argument("--amount", type=float, default=1.0)
    ap.add_argument("--subframes", type=int, default=8)
    ap.add_argument("--seed", type=int, default=7)
    o = ap.parse_args()
    if o.list or not o.look:
        for k, (_, d) in LOOKS.items():
            print("  %-12s %s" % (k, d))
        return
    if o.look not in LOOKS or not o.input or not o.output:
        ap.error("need LOOK INPUT OUTPUT (see --list)")
    o.start = datetime.datetime.strptime(o.start, "%Y-%m-%d %H:%M:%S") if o.start else datetime.datetime.now().replace(microsecond=0)
    frames = frames_in(o.input)
    if not frames:
        sys.exit("no frames found in %s" % o.input)
    single = not os.path.isdir(o.input)

    def out_path(k, src):
        if single or o.look == "slitscan":
            return o.output
        return os.path.join(o.output, os.path.splitext(os.path.basename(src))[0] + ".png")

    if o.look in ("rolling", "slitscan"):
        gen = look_rolling(frames, o) if o.look == "rolling" else look_slitscan(frames, o)
        for k, img in gen:
            p = o.output if single or o.look == "slitscan" else os.path.join(o.output, "frame_%04d.png" % k)
            save(img, p); print(p)
        return
    fn = LOOKS[o.look][0]
    for k, p in enumerate(frames):
        rng = np.random.default_rng(o.seed * 100003 + k)
        save(fn(load(p), k, rng, o), out_path(k, p))
        print(out_path(k, p))


if __name__ == "__main__":
    main()
