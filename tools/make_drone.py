#!/usr/bin/env python3
"""Synthesize a seamless ambient drone loop, for laying under a looping clip.

Usage:
    py tools/make_drone.py --seconds 8 --out drone.wav
    ffmpeg -i clip.mp4 -i drone.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out.mp4

Every frequency is a whole number of cycles per loop (a multiple of 1/seconds Hz),
and the reverb is rendered to steady state over several loops before one loop is
cut out, so the end joins the start with no click. Needs numpy.
"""

import argparse
import wave

import numpy as np

SR = 48000


def snap(f, seconds):
    """Round a frequency to a whole number of cycles per loop."""
    return round(f * seconds) / seconds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    T = a.seconds
    step = 1 / T  # smallest loop-safe frequency
    reps = 4
    t = np.arange(SR * T * reps) / SR
    out = np.zeros_like(t)

    def tone(f, amp, detune=0, phase=0.0):
        f = snap(f, T) + detune * step
        return amp * np.sin(2 * np.pi * f * t + phase)

    # one slow swell per loop, like the lamp breathing; never fully drops out
    breath = 0.75 + 0.25 * np.sin(2 * np.pi * step * t - np.pi / 2)

    # the floor: low A and its fifth, with slow beating pairs
    for f, amp in [(55, 0.30), (82.5, 0.16), (110, 0.14)]:
        out += tone(f, amp) + tone(f, amp * 0.7, detune=1, phase=1.3)

    # the choir: an A sus2 voicing (A3 B3 E4 A4), each voice built from harmonics
    # shaped by an "ah" vowel (formants ~700 and ~1150 Hz), chorused by detuning
    def vowel(h):
        return np.exp(-((h - 700) / 260) ** 2) + 0.6 * np.exp(-((h - 1150) / 300) ** 2) + 0.15
    rng = np.random.default_rng(7)
    for root, amp in [(220, 0.050), (246.94, 0.032), (329.63, 0.042), (440, 0.030)]:
        for d in (-1, 0, 1):
            for n in range(1, 14):
                h = snap(root, T) * n
                if h > 4000:
                    break
                out += tone(h, amp * vowel(h) / n ** 0.6, detune=d * n, phase=rng.uniform(0, 6.28)) * breath

    # the shimmer: high partials fading in and out, two and three times a loop
    for f, amp, k in [(1318.5, 0.012, 2), (1760, 0.009, 3), (2637, 0.006, 2)]:
        out += tone(f, amp) * (0.5 + 0.5 * np.sin(2 * np.pi * k * step * t))

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
