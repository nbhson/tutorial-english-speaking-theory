#!/usr/bin/env python3
# Build JSON data for the Vue 3 app from topics/*.md
# Usage: python3 scripts/build_data.py
import os, re, html, json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOPICS_DIR = ROOT / "speaking" / "topics"
GRAMMAR_DIR = ROOT / "speaking" / "grammar"
IMG_DIR = ROOT / "speaking" / "images"
OUT = ROOT / "speaking" / "data.json"

import importlib.util
spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build_site.py")
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)

def main():
    files = sorted(TOPICS_DIR.glob("topic-*.md"))
    infos, groups = [], []
    for f in files:
        md = f.read_text(encoding="utf-8")
        tmatch = re.match(r"#\s+Topic\s+(\d+)\s+—\s+(.+)", md)
        num = tmatch.group(1)
        rest = tmatch.group(2).strip()
        tv = re.match(r"(.+?)\s+\(([^()]*)\)\s*$", rest)
        en, vi = (tv.group(1).strip(), tv.group(2).strip()) if tv else (rest, "")
        g = re.search(r"Nhóm \*\*(.+?)\*\*", md)
        full_group = g.group(1).strip() if g else ""
        parts = full_group.split(" - ", 1)
        group_en = parts[0].strip()
        group_vi = parts[1].strip() if len(parts) > 1 else ""
        if group_en not in groups:
            groups.append(group_en)
        infos.append({
            "file": f, "stem": f.stem, "num": num, "en": en, "vi": vi,
            "group_en": group_en, "group_vi": group_vi,
            "gi": groups.index(group_en) + 1,
            "img": bs.pick_map_img(int(num)),
            "mins": bs.reading_minutes(md),
            "md": md,
            "isGrammar": False,
        })

    # Grammar vault (g-*.md)
    if GRAMMAR_DIR.is_dir():
        for f in sorted(GRAMMAR_DIR.glob("g-*.md")):
            md = f.read_text(encoding="utf-8")
            tmatch = re.match(r"#\s+Grammar\s+(\d+)\s+—\s+(.+)", md)
            num = tmatch.group(1)
            en = tmatch.group(2).strip()
            infos.append({
                "file": f, "stem": "grammar-%s" % num,
                "num": num, "en": en, "vi": "",
                "group_en": "NGỮ PHÁP VAULT",
                "group_vi": "Giao tiếp trọng tâm",
                "gi": 4,
                "img": None,
                "mins": bs.reading_minutes(md),
                "md": md,
                "isGrammar": True,
            })

    topics = []
    prev_group = None
    for idx, info in enumerate(infos):
        is_gram = info.get("isGrammar", False)
        divider = False
        if (not is_gram) and prev_group is not None and info["group_en"] != prev_group:
            divider = True
        # grammar section has no divider in original
        if is_gram:
            divider = False
        prev_group = info["group_en"]

        md_body = re.sub(r"^>\s*\*\*Nhóm .+?\*\*.*$", "", info["md"], count=1, flags=re.M)
        sub = re.sub(r"^#.*\n", "", md_body, count=1)
        body = bs.md_to_html(sub, info["stem"])

        # speaking topics chain prev/next only among themselves
        prev_speak = (idx > 0 and not is_gram and not infos[idx-1].get("isGrammar", False))
        next_speak = (idx < len(infos) - 1 and not is_gram and not infos[idx+1].get("isGrammar", False))

        topics.append({
            "id": info["stem"],
            "num": info["num"],
            "en": info["en"],
            "vi": info["vi"],
            "groupEn": info["group_en"],
            "groupVi": info["group_vi"],
            "gi": info["gi"],
            "mins": info["mins"],
            "img": info["img"],
            "bodyHtml": body,
            "isGrammar": is_gram,
            "hasDividerBefore": divider,
            "prevId": (infos[idx-1]["stem"] if prev_speak else None),
            "nextId": (infos[idx+1]["stem"] if next_speak else None),
            "prevEn": (infos[idx-1]["en"] if prev_speak else ""),
            "nextEn": (infos[idx+1]["en"] if next_speak else ""),
            "prevNum": (infos[idx-1]["num"] if prev_speak else ""),
            "nextNum": (infos[idx+1]["num"] if next_speak else ""),
        })

    data = {
        "generated": datetime.date.today().isoformat(),
        "groups": groups,
        "topics": topics,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"Built {OUT} with {len(topics)} topics")

if __name__ == "__main__":
    main()
