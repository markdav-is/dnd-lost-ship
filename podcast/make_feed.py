#!/usr/bin/env python3
"""Build feed.xml (podcast RSS) for Wandering Aerun from show.json + feed_episodes.json.

Usage:
    python make_feed.py

feed_episodes.json is the list of PUBLISHED episodes (newest additions appended):
[
  {
    "slug": "ep001-the-long-reach",
    "title": "The Long Reach",
    "summary": "The Compiler opens the frequency...",
    "pubdate": "Tue, 25 Aug 2026 20:00:00 GMT",
    "bytes": 123456,
    "duration": "6:12"
  }
]
Audio URL is derived as https://archive.org/download/<archive_item>/<slug>.mp3.
Upload the mp3, cover.jpg, and the generated feed.xml to the archive.org item.
"""

import json
import os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(os.path.join(HERE, "show.json"), encoding="utf-8") as f:
        show = json.load(f)
    eps_path = os.path.join(HERE, "feed_episodes.json")
    with open(eps_path, encoding="utf-8") as f:
        episodes = json.load(f)

    base = f"https://archive.org/download/{show['archive_item']}"
    items = []
    for i, ep in enumerate(reversed(episodes)):  # newest first in feed
        url = f"{base}/{ep['slug']}.mp3"
        items.append(f"""    <item>
      <title>{escape(ep['title'])}</title>
      <description>{escape(ep['summary'])}</description>
      <pubDate>{ep['pubdate']}</pubDate>
      <enclosure url="{url}" length="{ep['bytes']}" type="audio/mpeg"/>
      <guid isPermaLink="false">{show['archive_item']}-{escape(ep['slug'])}</guid>
      <itunes:duration>{ep['duration']}</itunes:duration>
      <itunes:episode>{len(episodes) - i}</itunes:episode>
      <itunes:explicit>false</itunes:explicit>
    </item>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(show['title'])}</title>
    <link>{show['site_url']}</link>
    <atom:link href="{show['feed_url']}" rel="self" type="application/rss+xml"/>
    <language>{show['language']}</language>
    <description>{escape(show['description'])}</description>
    <itunes:author>{escape(show['author'])}</itunes:author>
    <itunes:owner>
      <itunes:name>{escape(show['author'])}</itunes:name>
      <itunes:email>{show['owner_email']}</itunes:email>
    </itunes:owner>
    <itunes:image href="{show['cover_url']}"/>
    <itunes:category text="{show['category']}">
      <itunes:category text="{show['subcategory']}"/>
    </itunes:category>
    <itunes:explicit>{'true' if show['explicit'] else 'false'}</itunes:explicit>
{chr(10).join(items)}
  </channel>
</rss>
"""
    out = os.path.join(HERE, "feed.xml")
    with open(out, "w", encoding="utf-8") as f:
        f.write(feed)
    print(f"Wrote {out} with {len(episodes)} episode(s).")
    print(f"Upload it (plus mp3s and cover.jpg) to https://archive.org/details/{show['archive_item']}")


if __name__ == "__main__":
    main()
