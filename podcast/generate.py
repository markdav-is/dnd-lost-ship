#!/usr/bin/env python3
"""Generate audio clips for a Wandering Aerun episode via the ElevenLabs API.

Usage:
    python generate.py episodes/ep001-the-long-reach.md
    python generate.py --list-voices
    python generate.py episodes/ep001-the-long-reach.md --scene interview   # regen one scene

Reads ELEVENLABS_API_KEY from the environment. Clips are cached in
build/<slug>/clips/ by content hash - editing one line only re-bills that chunk.
Stdlib only; no pip installs needed.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error

API = "https://api.elevenlabs.io/v1"
DIALOGUE_CHAR_LIMIT = 1900  # API limit is 2000 across all inputs; keep headroom
HERE = os.path.dirname(os.path.abspath(__file__))


def api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set. See README.md for setup.")
    return key


def call(path, payload=None, method="GET"):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"xi-api-key": api_key(), "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code} on {path}: {e.read().decode(errors='replace')[:500]}")


def list_voices():
    data = json.loads(call("/voices"))
    for v in data.get("voices", []):
        labels = ", ".join(f"{k}={x}" for k, x in (v.get("labels") or {}).items())
        print(f"{v['voice_id']}  {v['name']:<20} {labels}")


def load_voices():
    with open(os.path.join(HERE, "voices.json"), encoding="utf-8") as f:
        return {k: v for k, v in json.load(f).items() if not k.startswith("_")}


def parse_script(path):
    """Return (slug, [scene]) where scene = {name, mode, items}.
    items: ("dialogue", [(speaker, text), ...]) | ("sfx", desc, secs) | ("pause", secs)
    """
    slug = os.path.splitext(os.path.basename(path))[0]
    scenes = []
    scene = None
    with open(path, encoding="utf-8") as f:
        text = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^## scene:\s*([\w-]+)\s*(?:\[(\w+)\])?", line)
        if m:
            scene = {"name": m.group(1), "mode": m.group(2) or "radio", "items": []}
            scenes.append(scene)
            continue
        if scene is None or line.startswith("#"):
            continue
        if line.startswith("BED:"):
            continue  # episode-wide ambience, handled by parse_bed()
        # Optional third field = prompt_influence (0-1). Left out of the payload
        # when absent, so existing cached clips keep their hashes.
        m = re.match(r"^SFX:\s*(.+?)\s*\|\s*([\d.]+)(?:\s*\|\s*([\d.]+))?$", line)
        if m:
            infl = float(m.group(3)) if m.group(3) else None
            scene["items"].append(("sfx", m.group(1), float(m.group(2)), infl))
            continue
        m = re.match(r"^MUSIC:\s*(.+?)\s*\|\s*([\d.]+)$", line)
        if m:
            scene["items"].append(("music", m.group(1), float(m.group(2))))
            continue
        m = re.match(r"^PAUSE:\s*([\d.]+)$", line)
        if m:
            scene["items"].append(("pause", float(m.group(1))))
            continue
        m = re.match(r"^([A-Z][A-Z0-9_]*):\s*(.+)$", line)
        if m:
            if scene["items"] and scene["items"][-1][0] == "dialogue":
                scene["items"][-1][1].append((m.group(1), m.group(2)))
            else:
                scene["items"].append(("dialogue", [(m.group(1), m.group(2))]))
    return slug, scenes


def parse_bed(path):
    """Return (desc, secs, influence|None) for an optional episode-wide ambience line:
        BED: description | seconds [| prompt_influence]
    The bed is generated as a seamless loop and mixed UNDER the whole episode by
    master.py. It may appear anywhere in the script (top of file is conventional)."""
    with open(path, encoding="utf-8") as f:
        text = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
    m = re.search(r"^BED:\s*(.+?)\s*\|\s*([\d.]+)(?:\s*\|\s*([\d.]+))?\s*$", text, flags=re.M)
    if not m:
        return None
    return m.group(1), float(m.group(2)), (float(m.group(3)) if m.group(3) else None)


def chunk_dialogue(lines):
    """Split a run of dialogue lines into chunks under the API char limit."""
    chunks, cur, size = [], [], 0
    for speaker, text in lines:
        if cur and size + len(text) > DIALOGUE_CHAR_LIMIT:
            chunks.append(cur)
            cur, size = [], 0
        cur.append((speaker, text))
        size += len(text)
    if cur:
        chunks.append(cur)
    return chunks


def have(path):
    return os.path.exists(path) and os.path.getsize(path) > 0


def save(path, data):
    if not data:
        sys.exit(f"API returned empty audio for {os.path.basename(path)} - retry the run.")
    tmp = path + ".tmp"
    open(tmp, "wb").write(data)
    os.replace(tmp, path)


def cache_path(clips_dir, prefix, payload):
    # Identity is content-only, so reordering scenes never re-bills a clip.
    h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
    return os.path.join(clips_dir, f"{h}.mp3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", nargs="?", help="episode script .md")
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--scene", help="only (re)generate this scene")
    args = ap.parse_args()

    if args.list_voices:
        list_voices()
        return
    if not args.script:
        ap.error("script path required (or --list-voices)")

    voices = load_voices()
    slug, scenes = parse_script(args.script)
    build = os.path.join(HERE, "build", slug)
    # Shared across episodes: identical content (theme music, recurring SFX,
    # unchanged sponsor reads) is generated once for the whole show.
    clips_dir = os.path.join(HERE, "build", "_cache")
    os.makedirs(clips_dir, exist_ok=True)
    os.makedirs(build, exist_ok=True)

    manifest = []  # ordered [{scene, mode, file|pause}]
    bed = parse_bed(args.script)
    if bed:
        payload = {"text": bed[0], "duration_seconds": min(bed[1], 22), "loop": True}
        if bed[2] is not None:
            payload["prompt_influence"] = bed[2]
        out = cache_path(clips_dir, "bed", payload)
        if args.scene is None and not have(out):
            print(f"[bed]      {bed[0][:60]}")
            save(out, call("/sound-generation", payload, "POST"))
        manifest.append({"scene": "_bed", "mode": "radio", "kind": "bed", "file": out})
    for si, scene in enumerate(scenes):
        wanted = args.scene is None or args.scene == scene["name"]
        ci = 0
        for item in scene["items"]:
            ci += 1
            prefix = f"{si:02d}-{scene['name']}-{ci:02d}"
            if item[0] == "pause":
                manifest.append({"scene": scene["name"], "mode": scene["mode"], "pause": item[1]})
                continue
            if item[0] == "music":
                payload = {"prompt": item[1], "music_length_ms": int(item[2] * 1000)}
                out = cache_path(clips_dir, prefix + "-music", payload)
                if wanted and not have(out):
                    print(f"[music]    {prefix}: {item[1][:60]}")
                    save(out, call("/music", payload, "POST"))
                manifest.append({"scene": scene["name"], "mode": scene["mode"], "kind": "music", "file": out})
                continue
            if item[0] == "sfx":
                payload = {"text": item[1], "duration_seconds": min(item[2], 22)}
                if len(item) > 3 and item[3] is not None:
                    payload["prompt_influence"] = item[3]
                out = cache_path(clips_dir, prefix + "-sfx", payload)
                if wanted and not have(out):
                    print(f"[sfx]      {prefix}: {item[1][:60]}")
                    save(out, call("/sound-generation", payload, "POST"))
                manifest.append({"scene": scene["name"], "mode": scene["mode"], "kind": "sfx", "file": out})
                continue
            for chunk in chunk_dialogue(item[1]):
                missing = [s for s, _ in chunk if s not in voices]
                if missing:
                    sys.exit(f"Speakers missing from voices.json: {missing}")
                payload = {
                    "inputs": [{"text": t, "voice_id": voices[s]["voice_id"]} for s, t in chunk],
                    "model_id": "eleven_v3",
                    # stability 0.0 = "creative": livelier, more performed delivery
                    "settings": {"stability": 0.0},
                }
                out = cache_path(clips_dir, prefix, payload)
                if wanted and not have(out):
                    print(f"[dialogue] {prefix}: {len(chunk)} lines, {sum(len(t) for _, t in chunk)} chars")
                    save(out, call("/text-to-dialogue", payload, "POST"))
                manifest.append({"scene": scene["name"], "mode": scene["mode"], "kind": "dialogue", "file": out})
                ci += 1

    with open(os.path.join(build, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    done = sum(1 for m in manifest if "file" in m and os.path.exists(m["file"]))
    total = sum(1 for m in manifest if "file" in m)
    print(f"\n{done}/{total} clips present in {build}")
    print(f"Next: python master.py {slug}")


if __name__ == "__main__":
    main()
