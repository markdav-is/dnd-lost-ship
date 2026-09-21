"""Reduce a raw Trello board export to its content, for committing to a public repo.

Whitelist, not blacklist: only board/list/card names, descriptions, labels,
checklists, attachment names, and comment text + date are carried over. Every
id, URL to Trello, member record, and email-to-board / email-to-card address in
the raw export is dropped.

    python tools/sanitize_trello.py assets/2023-dnd-campaign.raw.json assets/2023-dnd-campaign.json
"""
import json
import sys


def sanitize(board):
    checklists = {}
    for cl in board.get("checklists", []):
        checklists.setdefault(cl["idCard"], []).append({
            "name": cl["name"],
            "items": [
                {"name": it["name"], "done": it["state"] == "complete"}
                for it in sorted(cl["checkItems"], key=lambda x: x["pos"])
            ],
        })

    comments = {}
    for a in board.get("actions", []):
        if a["type"] == "commentCard":
            comments.setdefault(a["data"]["card"]["id"], []).append(
                {"date": a["date"][:10], "text": a["data"]["text"]}
            )

    lists = []
    for l in sorted(board["lists"], key=lambda x: x["pos"]):
        cards = []
        for c in sorted((c for c in board["cards"] if c["idList"] == l["id"]), key=lambda x: x["pos"]):
            cards.append({
                "name": c["name"],
                "archived": c["closed"],
                "desc": c.get("desc") or "",
                "labels": [x.get("name") or x.get("color") for x in c.get("labels", [])],
                "checklists": checklists.get(c["id"], []),
                "attachments": [a.get("name") for a in c.get("attachments", [])],
                "comments": sorted(comments.get(c["id"], []), key=lambda x: x["date"]),
            })
        lists.append({"name": l["name"], "archived": l["closed"], "cards": cards})

    return {
        "board": board["name"],
        "note": "Sanitized Trello export: content only. Ids, member records, Trello URLs and email-to-board addresses removed by tools/sanitize_trello.py.",
        "lists": lists,
    }


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        out = sanitize(json.load(f))
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(out['lists'])} lists, {sum(len(l['cards']) for l in out['lists'])} cards -> {dst}")
