#!/usr/bin/env python3
"""Composite a rotating lighthouse beam over a looping clip.

Usage:
    py tools/beam_overlay.py --in clip.mp4 --lamp 1228,111 --out beamed.mp4 [--audio drone.wav]

The beam is a level cone turning one full revolution, always the same way
(clockwise seen from above), per loop of the clip, so it loops exactly. It is
modelled in 3D and projected from a camera on the ground below the lamp: it
reaches far into the distance on the sides, flares when it turns toward the
viewer, and dims when it passes behind the tower. Screen-blended in warm gold.
Needs numpy, Pillow and ffmpeg on PATH.
"""

import argparse
import json
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

GOLD = np.array([1.0, 0.86, 0.60])


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                          "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return s["width"], s["height"], float(num) / float(den), int(s["nb_read_frames"])


def beam_layer(theta, W, H, lamp, horizon, f, scale):
    """Beam brightness 0..1 for direction theta, rendered at W*scale x H*scale."""
    w, h = int(W * scale), int(H * scale)
    cx = W / 2
    z0 = 100.0
    x0 = (lamp[0] - cx) / f * z0
    y0 = (horizon - lamp[1]) / f * z0
    dx, dz = math.sin(theta), math.cos(theta)

    def project(s):
        X, Z = x0 + s * dx, z0 + s * dz
        return (cx + f * X / Z) * scale, (horizon - f * y0 / Z) * scale, Z

    away = max(0.0, dz)
    dim = 1 - 0.8 * away ** 1.5           # seen from behind, a beam is faint
    samples = np.concatenate([[0], np.geomspace(1, 4000, 160)])
    pts = []
    for s in samples:
        x, y, Z = project(s)
        if Z < 6:
            break
        pts.append((x, y, s, Z))

    layers = []
    for widen, gain, blur in ((0.10, 0.45, 18), (0.035, 0.6, 7)):  # soft cone, then bright core
        img = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(img)
        for i in range(len(pts) - 1, 0, -1):  # far to near, so the nearer, brighter part wins
            (xa, ya, sa, Za), (xb, yb, sb, Zb) = pts[i - 1], pts[i]
            ra = min(4000, f * scale * (1.2 + widen * sa) / Za)
            rb = min(4000, f * scale * (1.2 + widen * sb) / Zb)
            vx, vy = xb - xa, yb - ya
            n = math.hypot(vx, vy) or 1
            px, py = -vy / n, vx / n
            a = math.exp(-sb / 1400) * gain * dim
            d.polygon([(xa + px * ra, ya + py * ra), (xb + px * rb, yb + py * rb),
                       (xb - px * rb, yb - py * rb), (xa - px * ra, ya - py * ra)],
                      fill=int(255 * min(1, a)))
        layers.append(np.asarray(img.filter(ImageFilter.GaussianBlur(blur * scale * 2)), dtype=np.float32) / 255)
    beam = np.clip(layers[0] + layers[1], 0, 1)

    # the lamp flare, which swells as the beam swings toward the viewer
    facing = max(0.0, -dz)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r2 = (xx - lamp[0] * scale) ** 2 + (yy - lamp[1] * scale) ** 2
    rad = (30 + 520 * facing ** 4) * scale
    flare = (0.45 + 0.55 * facing ** 3) * np.exp(-r2 / (2 * rad ** 2))
    wash = 0.10 * facing ** 6             # the whole scene lit for a moment
    return np.clip(beam + flare + wash, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--lamp", required=True, help="x,y of the lamp in pixels")
    ap.add_argument("--horizon", type=float, help="screen y of eye level (default lamp y + 22%% of height)")
    ap.add_argument("--focal", type=float, default=1400)
    ap.add_argument("--start", type=float, default=-90, help="start bearing in degrees: -90 = left, 0 = away")
    ap.add_argument("--strength", type=float, default=0.85)
    ap.add_argument("--audio")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    W, H, fps, n = probe(a.src)
    lamp = tuple(float(v) for v in a.lamp.split(","))
    horizon = a.horizon if a.horizon is not None else lamp[1] + 0.22 * H
    scale = 0.5

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc_cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(fps), "-i", "-"]
    if a.audio:
        enc_cmd += ["-i", a.audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    enc_cmd += ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", a.out]
    enc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE)

    start = math.radians(a.start)
    for i in range(n):
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3:
            break
        frame = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        theta = start - 2 * math.pi * i / n   # one turn per loop, clockwise from above
        b = beam_layer(theta, W, H, lamp, horizon, a.focal, scale)
        b = np.asarray(Image.fromarray((b * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR),
                       dtype=np.float32) / 255
        light = (b * a.strength)[..., None] * GOLD
        out = 1 - (1 - frame) * (1 - light)  # screen blend
        enc.stdin.write((np.clip(out, 0, 1) * 255).astype(np.uint8).tobytes())
        if i % 24 == 0:
            print(f"frame {i}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
