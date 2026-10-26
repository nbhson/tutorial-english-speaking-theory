#!/usr/bin/env python3
# Build a single-page study site (index.html) from topics/*.md
# Usage: python3 scripts/build_site.py
import os, re, html, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOPICS_DIR = ROOT / "speaking" / "topics"
IMG_DIR = ROOT / "speaking" / "images"
OUT = ROOT / "speaking" / "index.html"

def git_or_time():
    return datetime.date.today().isoformat()

def md_inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"~~(.+?)~~", r"<del>\1</del>", s)
    s = re.sub(r"`([^`]+?)`", r"<code>\1</code>", s)
    return s

def md_to_html(md: str, stem: str = "") -> str:
    lines = md.split("\n")
    out, i = [], 0
    in_list = False
    list_type = None  # "ul" | "ol" — đóng đúng thẻ tương ứng

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            out.append("</%s>" % list_type)
            in_list, list_type = False, None

    in_code = False
    code_buf = []
    hid = 0
    while i < len(lines):
        line = lines[i]
        # fenced code block?
        if line.strip().startswith("```"):
            if in_code:
                pre = html.escape("\n".join(code_buf))
                out.append('<pre class="dialogue"><code>%s</code></pre>' % pre)
                in_code, code_buf = False, []
            else:
                close_list()
                in_code = True
            i += 1; continue
        if in_code:
            code_buf.append(line)
            i += 1; continue
        # table?
        if re.match(r"\s*\|", line) and i + 1 < len(lines) and re.match(r"\s*\|?[\s:\-\|]+\|?\s*$", lines[i+1]) and set(lines[i+1].replace(" ","")) <= set("|-: "):
            rows_data = []
            while i < len(lines) and re.match(r"\s*\|", lines[i]):
                rows_data.append(lines[i]); i += 1
            # build table
            cells = [r.strip().strip("|") for r in rows_data]
            header = [c.strip() for c in cells[0].split("|")]
            body_rows = [ [c.strip() for c in r.split("|")] for r in cells[2:] ]
            t = ['<div class="table-wrap"><table><thead><tr>']
            t += [f"<th>{md_inline(c)}</th>" for c in header]
            t += ["</tr></thead><tbody>"]
            for r in body_rows:
                t += ["<tr>"] + [f"<td>{md_inline(c)}</td>" for c in r] + ["</tr>"]
            t += ["</tbody></table></div>"]
            out.append("\n".join(t))
            close_list()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_list()
            lvl = len(m.group(1))  # keep true level: "##"→h2 sections, "###"→h3
            hid += 1
            txt = m.group(2)
            cls = ""
            if lvl == 2:  # tô màu theo phân mục I / II / III
                if re.match(r"^III[\.\s]", txt): cls = "sec3"
                elif re.match(r"^II[\.\s]", txt): cls = "sec2"
                elif re.match(r"^I[\.\s]", txt): cls = "sec1"
            cattr = (' class="%s"' % cls) if cls else ""
            out.append('<h%d id="%s-h%d"%s>%s</h%d>' % (lvl, stem, hid, cattr, md_inline(txt), lvl))
            i += 1; continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            if in_list and list_type == "ol":
                close_list()
            if not in_list:
                out.append("<ul>"); in_list, list_type = True, "ul"
            out.append(f"<li>{md_inline(m.group(1))}</li>")
            i += 1; continue
        m = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        if m:
            if in_list and list_type == "ul":
                close_list()
            if not in_list:
                out.append("<ol>"); in_list, list_type = True, "ol"
            out.append(f"<li>{md_inline(m.group(3))}</li>")
            i += 1; continue
        if line.strip() in ("", "---"):
            close_list()
            if line.strip() == "---":
                out.append("<hr>")
            i += 1; continue
        close_list()
        if line.startswith(">"):
            out.append(f"<blockquote>{md_inline(line.lstrip('> '))}</blockquote>")
            i += 1; continue
        out.append(f"<p>{md_inline(line)}</p>")
        i += 1
    close_list()
    return "\n".join(out)

# ---- ảnh BEOD-MAP chính của mỗi topic ----
IMG_EXCLUDE = re.compile(r"(_grammar|_idiom|_voca|_extension|_freetalk|free\s*talk)", re.I)
IMG_SMALL = re.compile(r"[-_]small", re.I)

def pick_map_img(num: int):
    """Chọn ảnh mindmap chính: tXX-...BEOD-MAPS..., bỏ qua variant Grammar/Idiom/Voca/Extension/FreeTalk."""
    if not IMG_DIR.is_dir():
        return None
    pref = "t%02d-" % num
    pat = re.compile(r"^t%02d-.*beod-maps.*\.(png|jpe?g|webp)$" % num, re.I)
    cands = [p.name for p in IMG_DIR.iterdir()
             if pat.match(p.name) and not IMG_EXCLUDE.search(p.name.lower())]
    if not cands:
        return None
    nonsmall = [c for c in cands if not IMG_SMALL.search(c)]
    return sorted(nonsmall or cands)[0]

def reading_minutes(md: str) -> int:
    body = re.sub(r"```.*?```", "", md, flags=re.S)
    words = len(re.findall(r"\S+", body))
    return max(4, round(words / 170) + 1)

def main():
    files = sorted(TOPICS_DIR.glob("topic-*.md"))

    # ---- PASS 1: parse thông tin từng topic ----
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
            "img": pick_map_img(int(num)),
            "mins": reading_minutes(md),
            "md": md,
        })

    # ---- PASS 2: sinh sidebar nav (gom theo nhóm) ----
    nav_items = []
    prev_group = None
    for info in infos:
        if info["group_en"] != prev_group:
            nav_items.append('<div class="nav-group g%d" title="%s">🚩 %s</div>'
                             % (info["gi"], html.escape(info["group_en"], quote=True),
                                html.escape(info["group_en"])))
            prev_group = info["group_en"]
        nav_items.append(
            '<a class="nav-link" href="#%s" data-t="%s" data-g="%d" title="%s">'
            '<span class="n-num">%s</span><span class="n-txt">%s</span><span class="n-check">✓</span></a>'
            % (info["stem"], info["stem"], info["gi"],
               html.escape("Topic %s — %s" % (info["num"], info["en"]), quote=True),
               info["num"], html.escape(info["en"], quote=False)))

    # ---- PASS 3: sinh cards ----
    cards = []
    prev_group = None
    for idx, info in enumerate(infos):
        divider = ""
        if prev_group is not None and info["group_en"] != prev_group:
            gi_prev = infos[idx - 1]["gi"]
            divider = ('<div class="group-divider g%d"><span class="gd-ico">🚩</span>'
                       '<span class="gd-en">%s</span>%s</div>'
                       % (info["gi"], html.escape(info["group_en"]),
                          ('<span class="gd-vi">— %s</span>' % html.escape(info["group_vi"]))
                          if info["group_vi"] else ""))
        prev_group = info["group_en"]

        # bỏ blockquote meta gốc (nhóm/nguồn) — thay bằng chips t-meta
        md_body = re.sub(r"^>\s*Nhóm \*\*.+?\*\*.*$", "", info["md"], count=1, flags=re.M)
        sub = re.sub(r"^#.*\n", "", md_body, count=1)
        body = md_to_html(sub, info["stem"])

        figure = ""
        if info["img"]:
            figure = ('<figure class="mindmap"><img loading="lazy" decoding="async" '
                      'src="images/%s" alt="BEOD-MAP Topic %s">'
                      '<figcaption>🗺️ BEOD-MAP Topic %s — bức bản đồ của cả bài, bấm vào ảnh để phóng to</figcaption></figure>'
                      % (info["img"], info["num"], info["num"]))

        meta = ('<div class="t-meta">'
                '<span class="tag g%d">🚩 %s</span>%s'
                '<span class="tag ghost">⏱ ~%d phút học</span></div>'
                % (info["gi"], html.escape(info["group_en"]),
                   ('<span class="tag ghost">%s</span>' % html.escape(info["group_vi"]))
                   if info["group_vi"] else "",
                   info["mins"]))

        crumb = ('<div class="t-breadcrumb">'
                 '<button class="crumb-home">🏠 Trang chủ</button><i>›</i>'
                 '<button class="crumb-group" style="color:var(--brand-2);font-weight:700">🚩 %s</button><i>›</i>'
                 '<b>Topic %s</b></div>'
                 % (html.escape(info["group_en"]), info["num"]))

        head = ('%s\n<h1 class="topic-title"><span class="t-num g%d">%s</span>'
                '<span class="t-head-txt"><span class="t-en">%s</span>%s</span></h1>\n%s\n%s'
                % (crumb, info["gi"], info["num"], md_inline(info["en"]),
                   ('<span class="t-vi">%s</span>' % md_inline(info["vi"])) if info["vi"] else "",
                   meta, figure))

        prev = infos[idx - 1] if idx > 0 else None
        nxt = infos[idx + 1] if idx < len(infos) - 1 else None
        pn_prev = ('<button class="pn" data-go="prev" title="%s">⬅ %s</button>'
                   % (html.escape(prev["en"], quote=True),
                      html.escape("Topic %s · %s" % (prev["num"], prev["en"][:38])))) if prev \
                  else '<span></span>'
        pn_next = ('<button class="pn" data-go="next" title="%s">%s ➡</button>'
                   % (html.escape(nxt["en"], quote=True),
                      html.escape("Topic %s · %s" % (nxt["num"], nxt["en"][:38])))) if nxt \
                  else '<span></span>'
        pn = '<div class="pn-nav">%s%s</div>' % (pn_prev, pn_next)

        cards.append(divider + '<section class="topic-card" id="%s">\n%s\n%s\n%s\n</section>'
                     % (info["stem"], head, body, pn))

    tpl = (ROOT / "scripts" / "index_template.html").read_text(encoding="utf-8")
    page = tpl.replace("{{NAV}}", "\n".join(nav_items)).replace("{{CARDS}}", "\n".join(cards)).replace("{{DATE}}", git_or_time())
    OUT.write_text(page, encoding="utf-8")
    print(f"Built {OUT} with {len(files)} topics, {len(groups)} groups")

if __name__ == "__main__":
    main()
