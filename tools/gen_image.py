#!/usr/bin/env python3
"""Generate campaign art with Flux (Black Forest Labs) or Gemini (Nano Banana).

Usage:
    python gen_image.py "prompt text" --out ../docs/.attachments/foo.jpg
    python gen_image.py --prompt-file prompts/s42.txt --style alpha --out out.jpg
    python gen_image.py "..." --ref ../docs/.attachments/medical_android.png --ref old.jpg
    python gen_image.py "..." --backend gemini      # force a backend
    python gen_image.py "..." --pro                 # dearer model on either backend
    python gen_image.py --list-styles

Backend is picked from whichever key is set: BFL_API_KEY (Flux, preferred for
painterly encounter art) or GEMINI_API_KEY (Nano Banana, better for maps and
anything with text). Set both and use --backend to choose. Stdlib only.

--style prepends a house-style block from tools/styles/<name>.txt so scene prompts
stay short. --ref attaches reference images (a layout to keep, a character to
match). The final prompt is saved as tools/renders/<name>.prompt.txt so a pass
can be reproduced or tweaked.
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
STYLES_DIR = os.path.join(HERE, "styles")

GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_MODELS = {"std": "gemini-3.1-flash-image", "pro": "gemini-3-pro-image"}

FLUX_API = "https://api.bfl.ai/v1/"
FLUX_MODELS = {"std": "flux-2-pro", "pro": "flux-2-max"}

# width x height per aspect at ~1 MP ("1K") and ~3.5 MP ("2K"); multiples of 32
FLUX_SIZES = {
    "3:2": {"1K": (1248, 832), "2K": (2304, 1536)},
    "2:3": {"1K": (832, 1248), "2K": (1536, 2304)},
    "16:9": {"1K": (1344, 768), "2K": (2560, 1440)},
    "1:1": {"1K": (1024, 1024), "2K": (1920, 1920)},
    "4:3": {"1K": (1184, 896), "2K": (2048, 1536)},
    "21:9": {"1K": (1536, 640), "2K": (2688, 1152)},
}


def http(url, payload=None, headers=None, method=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json", **(headers or {})},
        method=method or ("POST" if payload is not None else "GET"),
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code} on {url.split('?')[0]}: {e.read().decode(errors='replace')[:800]}")


def list_styles():
    if not os.path.isdir(STYLES_DIR):
        print("(no styles dir)")
        return
    for name in sorted(os.listdir(STYLES_DIR)):
        if name.endswith(".txt"):
            with open(os.path.join(STYLES_DIR, name), encoding="utf-8") as f:
                first = f.readline().strip()
            print(f"{name[:-4]:<12} {first}")


def load_style(name):
    path = os.path.join(STYLES_DIR, name + ".txt")
    if not os.path.exists(path):
        sys.exit(f"no style '{name}' — see --list-styles")
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def read_ref(path):
    if not os.path.exists(path):
        sys.exit(f"reference image not found: {path}")
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        return mime, base64.b64encode(f.read()).decode()


# ---------------------------------------------------------------- Gemini

def find_image(obj):
    """Return (mime, base64) for the first image block anywhere in the response."""
    if isinstance(obj, dict):
        out = obj.get("output_image")
        if isinstance(out, dict) and out.get("data"):
            return out.get("mime_type", "image/png"), out["data"]
        if obj.get("type") == "image" and obj.get("data"):
            return obj.get("mime_type", "image/png"), obj["data"]
        inline = obj.get("inlineData") or obj.get("inline_data")
        if isinstance(inline, dict) and inline.get("data"):
            return inline.get("mimeType") or inline.get("mime_type") or "image/png", inline["data"]
        for v in obj.values():
            hit = find_image(v)
            if hit:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = find_image(v)
            if hit:
                return hit
    return None


def gen_gemini(prompt, refs, aspect, size, pro, mime_out):
    key = os.environ["GEMINI_API_KEY"]
    model = GEMINI_MODELS["pro" if pro else "std"]
    inputs = [{"type": "text", "text": prompt}]
    for ref in refs:
        mime, data = read_ref(ref)
        inputs.append({"type": "image", "mime_type": mime, "data": data})
    payload = {
        "model": model,
        "input": inputs,
        "response_format": {"type": "image", "mime_type": mime_out, "aspect_ratio": aspect, "image_size": size},
    }
    print(f"gemini {model}  {aspect} {size}  refs={len(refs)}", file=sys.stderr)
    resp = json.loads(http(GEMINI_API, payload, {"x-goog-api-key": key}))
    hit = find_image(resp)
    if not hit:
        sys.exit("no image in response:\n" + json.dumps(resp, indent=2)[:2000])
    return model, hit[0], base64.b64decode(hit[1])


# ---------------------------------------------------------------- Flux

def gen_flux(prompt, refs, aspect, size, pro, mime_out, safety):
    key = os.environ["BFL_API_KEY"]
    model = FLUX_MODELS["pro" if pro else "std"]
    if aspect not in FLUX_SIZES:
        sys.exit(f"flux: aspect {aspect} not in {', '.join(FLUX_SIZES)} (or add it to FLUX_SIZES)")
    w, h = FLUX_SIZES[aspect]["2K" if size in ("2K", "4K") else "1K"]
    payload = {
        "prompt": prompt,
        "width": w,
        "height": h,
        "output_format": "jpeg" if mime_out == "image/jpeg" else "png",
        "safety_tolerance": safety,
    }
    for i, ref in enumerate(refs[:8]):
        mime, data = read_ref(ref)
        payload["input_image" if i == 0 else f"input_image_{i + 1}"] = f"data:{mime};base64,{data}"
    print(f"flux {model}  {w}x{h}  refs={len(refs)}", file=sys.stderr)
    sub = json.loads(http(FLUX_API + model, payload, {"x-key": key, "accept": "application/json"}))
    poll = sub.get("polling_url") or (FLUX_API + "get_result?id=" + sub["id"])
    if "cost" in sub:
        print(f"cost: {sub['cost']} credits", file=sys.stderr)
    for _ in range(300):
        time.sleep(2)
        res = json.loads(http(poll, headers={"x-key": key, "accept": "application/json"}))
        status = res.get("status")
        if status == "Ready":
            url = (res.get("result") or {}).get("sample")
            if not url:
                sys.exit("Ready but no result.sample:\n" + json.dumps(res, indent=2)[:2000])
            # the signed URL expires within minutes — fetch it now
            data = http(url, headers={}, method="GET")
            return model, mime_out, data
        if status in ("Error", "Request Moderated", "Content Moderated", "Task not found"):
            sys.exit(f"flux {status}:\n" + json.dumps(res, indent=2)[:2000])
    sys.exit("flux: timed out waiting for the result")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt", nargs="?", help="scene prompt (or use --prompt-file)")
    ap.add_argument("--prompt-file", help="read the scene prompt from a file")
    ap.add_argument("--style", help="prepend tools/styles/<name>.txt to the prompt")
    ap.add_argument("--ref", action="append", default=[], help="reference image (repeatable)")
    ap.add_argument("--out", default="out.jpg", help="output image path (default: out.jpg)")
    ap.add_argument("--aspect", default="3:2", help="aspect ratio (default 3:2, matching the existing art)")
    ap.add_argument("--size", default="2K", choices=["512", "1K", "2K", "4K"], help="image size (default 2K)")
    ap.add_argument("--backend", choices=["flux", "gemini"], help="default: flux if BFL_API_KEY is set, else gemini")
    ap.add_argument("--pro", action="store_true", help="dearer model: flux-2-max / gemini-3-pro-image")
    ap.add_argument("--safety", type=int, default=4, help="flux safety_tolerance 0-5 (default 4; 5 = loosest)")
    ap.add_argument("--list-styles", action="store_true")
    args = ap.parse_args()

    if args.list_styles:
        list_styles()
        return

    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as f:
            scene = f.read().strip()
    elif args.prompt:
        scene = args.prompt
    else:
        ap.error("give a prompt or --prompt-file")

    prompt = (load_style(args.style) + "\n\n" + scene) if args.style else scene

    backend = args.backend or ("flux" if os.environ.get("BFL_API_KEY") else "gemini")
    need = "BFL_API_KEY" if backend == "flux" else "GEMINI_API_KEY"
    if not os.environ.get(need):
        where = "https://dashboard.bfl.ai (API → Keys)" if backend == "flux" else "https://aistudio.google.com/apikey"
        sys.exit(f"{need} is not set. Get one at {where}")

    mime_out = "image/jpeg" if args.out.lower().endswith((".jpg", ".jpeg")) else "image/png"
    if backend == "flux":
        model, mime, data = gen_flux(prompt, args.ref, args.aspect, args.size, args.pro, mime_out, args.safety)
    else:
        model, mime, data = gen_gemini(prompt, args.ref, args.aspect, args.size, args.pro, mime_out)

    out = args.out
    if mime == "image/png" and out.lower().endswith((".jpg", ".jpeg")):
        print("note: API returned PNG; saving as .png", file=sys.stderr)
        out = os.path.splitext(out)[0] + ".png"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    records = os.path.join(HERE, "renders")
    os.makedirs(records, exist_ok=True)
    with open(os.path.join(records, os.path.basename(out) + ".prompt.txt"), "w", encoding="utf-8") as f:
        f.write(f"backend: {backend}\nmodel: {model}\naspect: {args.aspect}\nsize: {args.size}\n"
                f"refs: {', '.join(args.ref) or '-'}\n\n{prompt}\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
