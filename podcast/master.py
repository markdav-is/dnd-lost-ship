#!/usr/bin/env python3
"""Master a Wandering Aerun episode: stitch clips, apply the far-speaker radio
filter to [radio] scenes, and produce build/<slug>/<slug>.mp3.

Usage:
    python master.py ep001-the-long-reach

Requires ffmpeg on PATH. [dry] scenes stay warm and close (the Wanderer at the
set); [radio] scenes get a bandpass + compression so they sound like they came
over the Relay.
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GAP = 0.32  # seconds of silence between clips
DIALOGUE_TEMPO = 1.06  # gentle pitch-preserving speedup for dialogue clips only

RADIO_FILTER = (
    "highpass=f=280,lowpass=f=3400,"
    "acompressor=threshold=-18dB:ratio=4:attack=5:release=120,"
    "volume=1.5,aresample=44100,aformat=channel_layouts=mono"
)
DRY_FILTER = (
    "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,"
    "volume=1.2,aresample=44100,aformat=channel_layouts=mono"
)


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


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python master.py <episode-slug>")
    slug = sys.argv[1]
    build = os.path.join(HERE, "build", slug)
    with open(os.path.join(build, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)

    exe = ffmpeg()
    proc_dir = os.path.join(build, "processed")
    os.makedirs(proc_dir, exist_ok=True)

    concat_list = []
    silence = os.path.join(proc_dir, "gap.wav")
    run([exe, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(GAP), silence])

    for i, item in enumerate(manifest):
        if "pause" in item:
            p = os.path.join(proc_dir, f"{i:03d}-pause.wav")
            run([exe, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(item["pause"]), p])
            concat_list.append(p)
            continue
        if not os.path.exists(item["file"]):
            sys.exit(f"Missing clip {item['file']} - run generate.py first.")
        out = os.path.join(proc_dir, f"{i:03d}.wav")
        filt = RADIO_FILTER if item["mode"] == "radio" else DRY_FILTER
        if item.get("kind") == "dialogue":
            filt = f"atempo={DIALOGUE_TEMPO}," + filt
        run([exe, "-y", "-i", item["file"], "-af", filt, out])
        concat_list.append(out)
        concat_list.append(silence)

    list_file = os.path.join(proc_dir, "concat.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for p in concat_list:
            f.write(f"file '{p}'\n")

    final = os.path.join(build, f"{slug}.mp3")
    run([exe, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-codec:a", "libmp3lame", "-b:a", "128k", final])
    print(f"Mastered: {final}")


if __name__ == "__main__":
    main()
