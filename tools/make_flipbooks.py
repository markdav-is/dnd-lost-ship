#!/usr/bin/env python3
"""Build a Flipbook page under each adventure: just its images, in play order.

Usage:
    py tools/make_flipbooks.py            # print what would be written
    py tools/make_flipbooks.py --write    # publish /Adventures/<X>/Flipbook via the wikidown CLI

For each adventure page in /Adventures (in .order order), collects every image
embedded on the adventure page and then on its subpages (in their .order order),
drops duplicates, and writes /Adventures/<X>/Flipbook: the images one after
another with no text, so the DM can page through them at the table. Adventures
with no images are skipped. Re-run after adding or replacing encounter art.
Publishing goes through the wikidown CLI so .order and breadcrumbs stay right.
"""

import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.normpath(os.path.join(HERE, "..", "docs"))
ADV = os.path.join(DOCS, "Adventures")
IMG = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")

# images to show first, whatever their page order (e.g. where the next session opens)
FIRST = {"Return-to-the-Ship": ["enc_ropers_lights_on.jpg"]}


def order(folder):
    path = os.path.join(folder, ".order")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def images(md_path):
    """(alt, attachment filename) for each image on a page, in order."""
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    out = []
    for alt, src in IMG.findall(text):
        if ".attachments/" in src:
            out.append((alt, src.split(".attachments/", 1)[1]))
    return out


def build(name):
    pages = [os.path.join(ADV, name + ".md")]
    sub = os.path.join(ADV, name)
    pages += [os.path.join(sub, p + ".md") for p in order(sub) if p != "Flipbook"]
    seen, shots = set(), []
    for page in pages:
        if not os.path.exists(page):
            continue
        for alt, fname in images(page):
            if fname not in seen:
                seen.add(fname)
                shots.append((alt, fname))
    if not shots:
        return None
    lead = FIRST.get(name, [])
    shots.sort(key=lambda shot: lead.index(shot[1]) if shot[1] in lead else len(lead))
    title = name.replace("-", " ")
    lines = [f"# {title}: Flipbook", ""]
    for alt, fname in shots:
        lines += [f"![{alt}](../../.attachments/{fname})", ""]
    return "\n".join(lines)


def main():
    write = "--write" in sys.argv
    for name in order(ADV):
        md = build(name)
        if md is None:
            print(f"skip {name} (no images)")
            continue
        count = md.count("![")
        if not write:
            print(f"/Adventures/{name}/Flipbook  {count} images")
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(md)
            tmp = f.name
        path = f"/Adventures/{name}/Flipbook"
        exists = os.path.exists(os.path.join(ADV, name, "Flipbook.md"))
        cmd = ["wikidown", "write" if exists else "new", "--root", DOCS, "--path", path, "--file", tmp]
        if not exists:
            cmd += ["--title", "Flipbook"]
        rc = subprocess.call(cmd)
        os.unlink(tmp)
        if rc:
            sys.exit(rc)
        print(f"wrote {path}  {count} images")


if __name__ == "__main__":
    main()
