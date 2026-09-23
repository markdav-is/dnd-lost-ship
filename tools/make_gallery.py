#!/usr/bin/env python3
"""Build the wiki Gallery page: thumbnails of every image in docs/.attachments,
grouped by where they're used, each linking to the full image and its page.

Usage:
    py tools/make_gallery.py            # thumbs + tools/renders/gallery.md
    py tools/make_gallery.py --write    # ...and publish it to /Gallery via the wikidown CLI

Thumbnails go to docs/.attachments/thumbs/ (regenerated only when the source is
newer). Needs Pillow for the thumbnails; the page itself is written through the
wikidown CLI so .order and breadcrumbs stay right — never by hand.
"""

import argparse
import os
import re
import subprocess
import sys

from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True  # a few attachments are slightly truncated; render what's there

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
ATT = os.path.join(DOCS, ".attachments")
THUMBS = os.path.join(ATT, "thumbs")
OUT_MD = os.path.join(HERE, "renders", "gallery.md")
THUMB_W = 360
COLS = 4

# (section title, test on (name, pages)) — first match wins
SECTIONS = [
    ("Dark Sun source art", lambda n, p: n.startswith("darksun_")),
    ("People", lambda n, p: any(x.startswith("NPCs/") or x.startswith("Campaign/The-Party") for x in p)
                            or n.startswith("council_") or n in ("spasistren_sisters.jpeg",)),
    ("Encounters — Return to the Ship", lambda n, p: any(x.startswith("Adventures/Return-to-the-Ship") for x in p)),
    ("Encounters — Return to Frostwatch", lambda n, p: any(x.startswith("Adventures/Return-to-Frostwatch") for x in p)),
    ("The Lost Ship", lambda n, p: any(x.startswith("The-Lost-Ship") for x in p)
                                   or any(x.startswith("Bestiary/Ship-") for x in p)
                                   or n.startswith("level4_") or n.startswith("drop_tube")),
    ("Bestiary", lambda n, p: any(x.startswith("Bestiary/") for x in p)),
    ("The Scarlands", lambda n, p: any(x.startswith("Adventures/") or x.startswith("Locations/") or x == "World/The-Scarlands" for x in p)
                                   or n.startswith("hoversled")),
    ("Aerun & world maps", lambda n, p: any(x.startswith("Aerun-Players-Guide") or x.startswith("World") or x.startswith("Reference/Aerun") for x in p)
                                        or n.startswith("aerun_") or n.endswith("_city.png") or n.startswith("vermoon")),
    ("Game mechanics", lambda n, p: any(x.startswith("Game-Mechanics") for x in p)),
]
DISPLAY_ORDER = [
    "People", "Encounters — Return to the Ship", "Encounters — Return to Frostwatch", "The Lost Ship",
    "Bestiary", "The Scarlands", "Aerun & world maps", "Game mechanics", "Dark Sun source art", "Unplaced",
]
IGNORE_PAGES = {"Reference/Asset-Index", "Gallery"}

IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def scan_pages():
    """name -> {'pages': [...], 'alt': first alt text}"""
    used = {}
    for dirpath, _, files in os.walk(DOCS):
        if ".attachments" in dirpath:
            continue
        for fn in files:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            page = os.path.relpath(path, DOCS).replace("\\", "/")[:-3]
            if page in IGNORE_PAGES or page.endswith("/Flipbook"):
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for alt, src in IMG_RE.findall(text):
                if ".attachments/" not in src or "/thumbs/" in src:
                    continue
                name = src.split(".attachments/")[-1].split(")")[0]
                entry = used.setdefault(name, {"pages": [], "alt": ""})
                if page not in entry["pages"]:
                    entry["pages"].append(page)
                if not entry["alt"] and alt:
                    entry["alt"] = alt
    return used


def make_thumb(name):
    src = os.path.join(ATT, name)
    dst = os.path.join(THUMBS, os.path.splitext(name)[0] + ".jpg")
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    try:
        with Image.open(src) as im:
            if im.mode in ("P", "LA", "RGBA"):
                im = im.convert("RGBA")
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            else:
                im = im.convert("RGB")
            im.thumbnail((THUMB_W, int(THUMB_W * 3)))
            im.save(dst, "JPEG", quality=80, optimize=True)
    except OSError as e:
        print(f"warning: {name}: {e}", file=sys.stderr)
        return None
    return dst


def title_of(page):
    return page.split("/")[-1].replace("-", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="publish to /Gallery via the wikidown CLI")
    args = ap.parse_args()

    os.makedirs(THUMBS, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    used = scan_pages()

    images = sorted(f for f in os.listdir(ATT)
                    if os.path.isfile(os.path.join(ATT, f)) and f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")))
    groups = {title: [] for title, _ in SECTIONS}
    groups["Unplaced"] = []
    for name in images:
        pages = used.get(name, {}).get("pages", [])
        for title, test in SECTIONS:
            if test(name, pages):
                groups[title].append(name)
                break
        else:
            groups["Unplaced"].append(name)
        make_thumb(name)

    lines = [
        "# Gallery",
        "",
        "Every image in the wiki, as thumbnails. Click a picture for the full-size file; the line under it links to the page it lives on. "
        f"Regenerate with `py tools/make_gallery.py --write` after adding art ({len(images)} images).",
        "",
    ]
    for title in DISPLAY_ORDER:
        names = groups[title]
        if not names:
            continue
        lines += [f"## {title}", ""]
        lines.append("| " + " | ".join([" "] * COLS) + " |")
        lines.append("|" + " :---: |" * COLS)
        row = []
        for name in names:
            thumb = ".attachments/thumbs/" + os.path.splitext(name)[0] + ".jpg"
            full = ".attachments/" + name
            info = used.get(name, {"pages": [], "alt": ""})
            alt = (info["alt"] or os.path.splitext(name)[0].replace("_", " ")).replace("|", "-")
            links = " · ".join(f"[{title_of(p)}]({p}.md)" for p in info["pages"][:3]) or "*(not embedded anywhere)*"
            row.append(f"[![{alt}]({thumb})]({full})<br>{links}")
            if len(row) == COLS:
                lines.append("| " + " | ".join(row) + " |")
                row = []
        if row:
            row += [" "] * (COLS - len(row))
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT_MD}  ({len(images)} images, {len(groups['Unplaced'])} unplaced)")

    if args.write:
        cmd = ["wikidown", "write", "--root", DOCS, "--path", "/Gallery", "--file", OUT_MD]
        print(" ".join(cmd))
        sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
