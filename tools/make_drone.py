#!/usr/bin/env python3
"""Synthesize a seamless ambient drone loop, for laying under a looping clip.

Usage:
    py tools/make_drone.py --seconds 8 --out drone.wav
    py tools/make_drone.py --seconds 40 --arc 0:.45,8:.6,16:.95,24:1,32:.8 --wind 0:0,16:.2,24:1,32:.3 --out arc.wav
    ffmpeg -i clip.mp4 -i drone.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out.mp4

Every frequency is a whole number of cycles per loop (a multiple of 1/seconds Hz),
and the reverb is rendered to steady state over several loops before one loop is
cut out, so the end joins the start with no click. --arc shapes the choir and
shimmer over the loop (time:level pairs, wrapping round to the start), and --wind
adds a filtered wind-and-dust layer on its own curve. Needs numpy.
"""

import argparse
import wave

import numpy as np

SR = 48000


def snap(f, seconds):
    """Round a frequency to a whole number of cycles per loop."""
    return round(f * seconds) / seconds


def curve(spec, T, t):
    """Smooth periodic envelope from "time:level,..." pairs, wrapping at T."""
    pts = sorted((float(a), float(b)) for a, b in (p.split(":") for p in spec.split(",")))
    pts = pts + [(pts[0][0] + T, pts[0][1])]
    u = t % T
    env = np.zeros_like(t)
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        m = (u >= t0) & (u < t1) if t0 >= 0 else u < t1
        k = (u[m] - t0) / (t1 - t0)
        env[m] = v0 + (v1 - v0) * (0.5 - 0.5 * np.cos(np.pi * k))
    if pts[0][0] > 0:  # before the first point: ease in from the last level
        m = u < pts[0][0]
        k = (u[m] + T - pts[-2][0]) / (pts[0][0] + T - pts[-2][0])
        env[m] = pts[-2][1] + (pts[0][1] - pts[-2][1]) * (0.5 - 0.5 * np.cos(np.pi * k))
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=8)
    ap.add_argument("--arc", help="choir/shimmer level over the loop, e.g. 0:.5,16:1,32:.6")
    ap.add_argument("--wind", help="wind-and-dust level over the loop, e.g. 0:0,24:1")
    ap.add_argument("--voicing", default="sus2", choices=["sus2", "major"],
                    help="sus2 = ethereal and open (A B E A); major = warm and happy (A C# E A)")
    ap.add_argument("--wind-gain", type=float, default=0.22, help="how loud the wind layer gets at level 1")
    ap.add_argument("--wind-hz", type=float, default=700, help="centre of the wind's hiss; higher is harsher")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    T = a.seconds
    step = 1 / T  # smallest loop-safe frequency
    reps = max(2, -(-12 // T) + 1)  # enough passes for the reverb to settle
    t = np.arange(SR * T * reps) / SR
    out = np.zeros_like(t)

    rate = max(1, T // 8)  # keep beating, chorus and shimmer at the 8 s pace whatever the loop length

    def tone(f, amp, detune=0, phase=0.0):
        f = snap(f, T) + detune * rate * step
        return amp * np.sin(2 * np.pi * f * t + phase)

    # one slow swell per loop, like the lamp breathing; never fully drops out
    breath = 0.75 + 0.25 * np.sin(2 * np.pi * step * t - np.pi / 2)
    if a.arc:
        breath = curve(a.arc, T, t)

    # the floor: low A and its fifth, with slow beating pairs
    for f, amp in [(55, 0.30), (82.5, 0.16), (110, 0.14)]:
        out += (tone(f, amp) + tone(f, amp * 0.7, detune=1, phase=1.3)) * ((0.55 + 0.45 * breath) if a.arc else 1)

    # the choir: an A sus2 voicing (A3 B3 E4 A4), each voice built from harmonics
    # shaped by an "ah" vowel (formants ~700 and ~1150 Hz), chorused by detuning
    def vowel(h):
        return np.exp(-((h - 700) / 260) ** 2) + 0.6 * np.exp(-((h - 1150) / 300) ** 2) + 0.15
    rng = np.random.default_rng(7)
    second = 277.18 if a.voicing == "major" else 246.94  # C#4 for warmth, or B3 for air
    for root, amp in [(220, 0.050), (second, 0.034 if a.voicing == "major" else 0.032), (329.63, 0.042), (440, 0.030)]:
        for d in (-1, 0, 1):
            for n in range(1, 14):
                h = snap(root, T) * n
                if h > 4000:
                    break
                out += tone(h, amp * vowel(h) / n ** 0.6, detune=d * n, phase=rng.uniform(0, 6.28)) * breath

    # at the top of the arc, the choir opens upward: E5 and A5
    if a.arc:
        lift = np.clip((breath - 0.7) / 0.3, 0, 1)
        for root, amp in [(659.25, 0.022), (880, 0.016)]:
            for d in (-1, 0, 1):
                for n in range(1, 6):
                    h = snap(root, T) * n
                    out += tone(h, amp * vowel(h) / n ** 0.6, detune=d * n, phase=rng.uniform(0, 6.28)) * lift

    # the shimmer: high partials fading in and out, two and three times a loop
    for f, amp, k in [(1318.5, 0.012, 2), (1760, 0.009, 3), (2637, 0.006, 2)]:
        out += tone(f, amp) * (0.5 + 0.5 * np.sin(2 * np.pi * k * rate * step * t)) * (breath if a.arc else 1)

    # wind and dust: noise band-passed in the frequency domain, so it is periodic too
    if a.wind:
        N = SR * T
        spec = np.fft.rfft(rng.standard_normal(N))
        fr = np.fft.rfftfreq(N, 1 / SR)
        spec *= np.exp(-((np.log(fr + 1) - np.log(a.wind_hz)) / 0.9) ** 2)
        hiss = np.fft.irfft(spec, N)
        hiss /= np.max(np.abs(hiss))
        gust = 0.7 + 0.3 * np.sin(2 * np.pi * 3 * rate * step * t) * np.sin(2 * np.pi * 2 * rate * step * t + 1)
        out += a.wind_gain * np.tile(hiss, reps) * curve(a.wind, T, t) * gust

    # reverb: a 3 s decaying-noise tail, convolved circularly so the loop stays periodic
    n = SR * 3
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * 0.9))
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = np.real(np.fft.ifft(np.fft.fft(out) * np.fft.fft(ir, len(out))))
    mix = 0.55 * out + 0.45 * wet

    loop = mix[-SR * T:]  # last pass: steady state
    loop = loop / np.max(np.abs(loop)) * 0.7  # about -3 dBFS, no clipping
    stereo = np.stack([loop, np.roll(loop, int(SR * 0.012))], axis=1)  # a touch of width

    with wave.open(a.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype("<i2").tobytes())
    print(f"wrote {a.out} ({T}s loop)")


if __name__ == "__main__":
    main()
