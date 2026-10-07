#!/usr/bin/env python3
"""Animate a still into a short clip with Google Veo (GEMINI_API_KEY).

Usage:
    py tools/gen_video.py --image tools/refs/lighthouse_canon_9x16.jpg --loop \
        --prompt-file tools/prompts/vid_lighthouse_awe.txt --aspect 9:16 \
        --out docs/.attachments/lighthouse_awe.mp4

--image is the first frame. --loop passes the same image as the last frame too,
so the clip ends where it began and loops without a seam (keep the camera locked
in the prompt, or the middle will wander). --last <image> sets a different end
frame. --fast uses veo-3.1-fast (cheaper, a little rougher).

Veo bills per second of video; an 8 s clip on the standard model costs a few
dollars. The final prompt and settings are saved as tools/renders/<name>.prompt.txt.
Stdlib only.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://generativelanguage.googleapis.com/v1beta/"
MODELS = {"std": "veo-3.1-generate-preview", "fast": "veo-3.1-fast-generate-preview"}


def http(url, key, payload=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code} on {url.split('?')[0]}: {e.read().decode(errors='replace')[:800]}")


def frame(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return {"bytesBase64Encoded": data, "mimeType": mimetypes.guess_type(path)[0] or "image/jpeg"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="?")
    ap.add_argument("--prompt-file")
    ap.add_argument("--image", required=True, help="first frame")
    ap.add_argument("--last", help="last frame")
    ap.add_argument("--loop", action="store_true", help="last frame = first frame")
    ap.add_argument("--negative", default="camera movement, zoom, pan, cuts, text, people, figures")
    ap.add_argument("--aspect", default="16:9", choices=["16:9", "9:16"])
    ap.add_argument("--seconds", type=int, default=8, choices=[4, 6, 8])
    ap.add_argument("--resolution", default="1080p", choices=["720p", "1080p"])
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY") or sys.exit("GEMINI_API_KEY not set")
    prompt = open(a.prompt_file, encoding="utf-8").read().strip() if a.prompt_file else a.prompt
    if not prompt:
        sys.exit("need a prompt or --prompt-file")
    model = MODELS["fast" if a.fast else "std"]

    inst = {"prompt": prompt, "image": frame(a.image)}
    last = a.image if a.loop else a.last
    if last:
        inst["lastFrame"] = frame(last)
    params = {"aspectRatio": a.aspect, "durationSeconds": a.seconds,
              "resolution": a.resolution, "negativePrompt": a.negative}

    op = json.loads(http(f"{API}models/{model}:predictLongRunning", key, {"instances": [inst], "parameters": params}))
    print(f"{model}: started {op['name']}", file=sys.stderr)
    while not op.get("done"):
        time.sleep(10)
        op = json.loads(http(API + op["name"], key))
        print(".", end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)
    if "error" in op:
        sys.exit(f"Veo error: {op['error']}")
    samples = op["response"]["generateVideoResponse"].get("generatedSamples")
    if not samples:
        sys.exit(f"no video returned (filtered?): {json.dumps(op['response'])[:800]}")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(http(samples[0]["video"]["uri"], key))
    print(f"wrote {a.out}", file=sys.stderr)

    log = os.path.join(HERE, "renders", os.path.basename(a.out) + ".prompt.txt")
    with open(log, "w", encoding="utf-8") as f:
        f.write(f"model: {model}\nimage: {a.image}\nlast: {last}\n"
                f"params: {json.dumps(params)}\n\n{prompt}\n")


if __name__ == "__main__":
    main()
