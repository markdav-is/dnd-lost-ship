#!/usr/bin/env python3
"""Master a Wandering Aerun episode: stitch clips, apply the far-speaker radio
filter to [radio] scenes, and produce build/<slug>/<slug>.mp3.

Usage:
    python master.py ep001-the-long-reach
    python master.py bonus01-the-ladder --bed-db -34     # louder ambience bed
    python master.py bonus01-the-ladder --no-bed         # writes <slug>-nobed.mp3

Requires ffmpeg on PATH. [dry] scenes stay warm and close (the Wanderer at the
set); [radio] scenes get a bandpass + compression so they sound like they came
over the Relay.

SFX: the sound-generation API returns ambient sounds (hum, static, room tone)
20-40 dB quieter than dialogue, so every SFX clip is measured and lifted to
SFX_TARGET_MEAN before it is stitched in. SFX in [radio] scenes also skip the
280 Hz high-pass - it deletes hum and low thumps outright.

BED: an optional looping ambience (see generate.py parse_bed) mixed under the
whole episode AFTER loudness normalisation, so the normaliser cannot pump it up
in the pauses. If the episode opens / closes with an SFX clip, the bed fades in
during the opening clip and out under the closing one.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
GAP = 0.32  # seconds of silence between clips
DIALOGUE_TEMPO = 1.06  # gentle pitch-preserving speedup for dialogue clips only
# Tighten dialogue: strip the lead-in / tail silence the TTS leaves on every clip, and
# collapse any internal pause longer than DIALOGUE_MAX_PAUSE down to DIALOGUE_KEEP_PAUSE
# (v3 multi-speaker clips put a breath between every call and response). Music and SFX
# are left alone.
DIALOGUE_MAX_PAUSE = 0.45
DIALOGUE_KEEP_PAUSE = 0.28
DIALOGUE_TIGHTEN = (
    "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.08,"
    "areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.12,areverse,"
    f"silenceremove=stop_periods=-1:stop_duration={DIALOGUE_MAX_PAUSE}:stop_threshold=-42dB:stop_silence={DIALOGUE_KEEP_PAUSE}"
)
DIALOGUE_GAP = 0.18  # seconds between two consecutive dialogue clips (GAP applies elsewhere)

SFX_TARGET_MEAN = -31.0  # dB, pre-loudnorm; lands ~6 dB under the voice in the final mix
SFX_LIFT_BELOW = -26.0   # clips already louder than this are left alone (the stings)
# Upward levelling for quiet SFX: up to 10x (20 dB) of gain on the quiet stretches.
SFX_LEVELER = "dynaudnorm=f=200:g=7:m=10:p=0.8"
TARGET_LUFS = -16.0
LIMITER = "alimiter=limit=0.84:level=0:attack=5:release=80"  # -1.5 dBFS ceiling, no auto-level
BED_DB = -36.0           # mean level of the ambience bed under a -16 LUFS program

RADIO_FILTER = (
    "highpass=f=280,lowpass=f=3400,"
    "acompressor=threshold=-18dB:ratio=4:attack=5:release=120,"
    "volume=1.5,aresample=44100,aformat=channel_layouts=mono"
)
# Same lo-fi top end, but keeps the lows so hum and thumps survive.
RADIO_SFX_FILTER = (
    "highpass=f=60,lowpass=f=3400,"
    "aresample=44100,aformat=channel_layouts=mono"
)
DRY_FILTER = (
    "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,"
    "volume=1.2,aresample=44100,aformat=channel_layouts=mono"
)
DRY_SFX_FILTER = "aresample=44100,aformat=channel_layouts=mono"
BED_FILTER = "highpass=f=90,lowpass=f=3400,aresample=44100,aformat=channel_layouts=mono"


def ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        links = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe")
        if os.path.exists(links):
            return links
    if not exe:
        sys.exit("ffmpeg not found on PATH. Open a new terminal after installing, or add it to PATH.")
    return exe


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{r.stderr[-1500:]}")
    return r.stderr


def levels(exe, path, filt):
    """(mean_dB, max_dB) of a clip after `filt`."""
    err = run([exe, "-hide_banner", "-i", path, "-af", filt + ",volumedetect", "-f", "null", "-"])
    mean = re.search(r"mean_volume:\s*(-?[\d.]+|-inf)", err)
    peak = re.search(r"max_volume:\s*(-?[\d.]+|-inf)", err)
    f = lambda m: -91.0 if (not m or m.group(1) == "-inf") else float(m.group(1))
    return f(mean), f(peak)


def wav_seconds(path):
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def loudnorm_filter(exe, list_file):
    """Measure the stitched program, then bring it to -16 LUFS with ONE constant gain
    plus a true limiter.

    Why not plain loudnorm: single-pass loudnorm is a dynamic leveller that rides the
    gain up on whatever opens the file, so an opening SFX always came out as loud as
    speech however it was levelled. loudnorm's linear mode is no help either - speech
    peaks sit near 0 dBFS after the radio filter, so it cannot fit the gain under the
    true-peak target and silently reverts to dynamic. Dialogue clips leave the radio
    filter within ~1 LU of each other, so a fixed gain loses nothing.
    NB alimiter auto-levels its output unless level=0."""
    err = run([exe, "-hide_banner", "-f", "concat", "-safe", "0", "-i", list_file,
               "-af", "loudnorm=I=-16:TP=-1.5:LRA=20:print_format=json", "-f", "null", "-"])
    m = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', err)
    if not m:
        return "loudnorm=I=-16:TP=-1.5:LRA=11"
    gain = TARGET_LUFS - float(m.group(1)) + 0.6  # +0.6: the limiter shaves a little loudness
    return f"volume={gain:.2f}dB,{LIMITER}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--no-bed", action="store_true", help="skip the ambience bed; writes <slug>-nobed.mp3")
    ap.add_argument("--bed-db", type=float, default=BED_DB, help=f"bed mean level in dB (default {BED_DB})")
    args = ap.parse_args()
    slug = args.slug
    build = os.path.join(HERE, "build", slug)
    with open(os.path.join(build, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)

    bed = next((m for m in manifest if m.get("kind") == "bed"), None)
    manifest = [m for m in manifest if m.get("kind") != "bed"]

    exe = ffmpeg()
    proc_dir = os.path.join(build, "processed")
    os.makedirs(proc_dir, exist_ok=True)

    concat_list = []
    silence = os.path.join(proc_dir, "gap.wav")
    run([exe, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(GAP), silence])
    short_gap = os.path.join(proc_dir, "gap-dialogue.wav")
    run([exe, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(DIALOGUE_GAP), short_gap])

    spans = []  # (kind, start_seconds, end_seconds) of every real clip in the program
    t = 0.0
    for i, item in enumerate(manifest):
        if "pause" in item:
            p = os.path.join(proc_dir, f"{i:03d}-pause.wav")
            run([exe, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(item["pause"]), p])
            concat_list.append(p)
            t += wav_seconds(p)
            continue
        if not os.path.exists(item["file"]):
            sys.exit(f"Missing clip {item['file']} - run generate.py first.")
        out = os.path.join(proc_dir, f"{i:03d}.wav")
        radio = item["mode"] == "radio"
        kind = item.get("kind")
        if kind == "sfx":
            filt = RADIO_SFX_FILTER if radio else DRY_SFX_FILTER
            mean, peak = levels(exe, item["file"], filt)
            if mean < SFX_LIFT_BELOW:
                # Generated SFX put transients (a switch clunk) at full scale and the
                # ambience behind them 40+ dB down. Level the clip dynamically first so
                # the quiet tail comes up, THEN trim the whole clip to the target mean.
                filt += "," + SFX_LEVELER
                mean2, peak2 = levels(exe, item["file"], filt)
                gain = max(-12.0, min(20.0, SFX_TARGET_MEAN - mean2))
                filt += f",volume={gain:.1f}dB,alimiter=limit=0.89:level=0"
                print(f"[sfx] clip {i:03d}: mean {mean:.1f} dB (peak {peak:.1f}) -> levelled {mean2:.1f} dB -> {gain:+.1f} dB")
            elif radio:
                filt = RADIO_FILTER  # already loud (the stings): keep the established sound
        else:
            filt = RADIO_FILTER if radio else DRY_FILTER
            if kind == "dialogue":
                filt = f"{DIALOGUE_TIGHTEN},atempo={DIALOGUE_TEMPO}," + filt
        run([exe, "-y", "-i", item["file"], "-af", filt, out])
        d = wav_seconds(out)
        spans.append((kind, t, t + d))
        nxt = next((m for m in manifest[i + 1:] if "pause" not in m), None)
        gap_file = silence
        if kind == "dialogue" and nxt and nxt.get("kind") == "dialogue":
            gap_file = short_gap
        t += d + wav_seconds(gap_file)
        concat_list.append(out)
        concat_list.append(gap_file)

    list_file = os.path.join(proc_dir, "concat.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for p in concat_list:
            f.write(f"file '{p}'\n")

    use_bed = bed is not None and not args.no_bed
    suffix = "-nobed" if (bed is not None and args.no_bed) else ""
    final = os.path.join(build, f"{slug}{suffix}.mp3")
    encode = ["-codec:a", "libmp3lame", "-b:a", "128k", final]
    norm = loudnorm_filter(exe, list_file)

    if not use_bed:
        run([exe, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
             "-af", norm, "-ar", "44100"] + encode)
        print(f"Mastered: {final}")
        return

    if not os.path.exists(bed["file"]):
        sys.exit(f"Missing bed clip {bed['file']} - run generate.py first.")
    program = os.path.join(proc_dir, "program.wav")
    run([exe, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
         "-af", norm, "-ar", "44100", "-ac", "1", program])
    total = wav_seconds(program)

    # The bed arrives with the set switching on and leaves with it switching off.
    start, end = 0.0, total
    if spans and spans[0][0] == "sfx":
        start = spans[0][1] + (spans[0][2] - spans[0][1]) * 0.5
    if spans and spans[-1][0] == "sfx":
        end = min(total, spans[-1][1] + (spans[-1][2] - spans[-1][1]) * 0.6)
    length = max(1.0, end - start)
    fade_in, fade_out = min(3.0, length / 4), min(2.5, length / 4)

    mean, _ = levels(exe, bed["file"], BED_FILTER)
    gain = args.bed_db - mean
    print(f"[bed] raw mean {mean:.1f} dB -> {gain:+.1f} dB, {start:.1f}s to {end:.1f}s of {total:.1f}s")
    graph = (
        f"[1:a]{BED_FILTER},volume={gain:.1f}dB,atrim=0:{length:.3f},"
        f"afade=t=in:st=0:d={fade_in:.2f},afade=t=out:st={length - fade_out:.3f}:d={fade_out:.2f},"
        f"adelay={int(start * 1000)}:all=1[bed];"
        f"[0:a][bed]amix=inputs=2:duration=first:normalize=0,{LIMITER}[mix]"
    )
    run([exe, "-y", "-i", program, "-stream_loop", "-1", "-i", bed["file"],
         "-filter_complex", graph, "-map", "[mix]"] + encode)
    print(f"Mastered: {final}")


if __name__ == "__main__":
    main()
