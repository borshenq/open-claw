#!/usr/bin/env python3
"""Generate beautifully illustrated EPUB: 一人公司生存手冊（國小科技教師版）"""

import os, re, uuid, datetime, zipfile
from xml.sax.saxutils import escape as xesc
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import illustrations as ill

DIR = "/home/borsheng/.openclaw/workspace/一人公司生存手冊"
OUT = os.path.join(DIR, "一人公司生存手冊.epub")

CHAPTERS = [
    ("01-為什麼國小老師需要一人公司.md", "ch01"),
    ("02-產品-科技教師版.md", "ch02"),
    ("03-定價-科技教師版.md", "ch03"),
    ("04-行銷-科技教師版.md", "ch04"),
    ("05-時間管理-科技教師版.md", "ch05"),
    ("06-財務-科技教師版.md", "ch06"),
    ("07-系統化-科技教師版.md", "ch07"),
    ("08-健康-科技教師版.md", "ch08"),
    ("09-AI工具.md", "ch09"),
    ("10-正職與一人公司.md", "ch10"),
]

TITLE = "一人公司生存手冊（國小科技教師版）"
AUTHOR = "Juang Borsheng"
UID = "urn:uuid:" + str(uuid.uuid4())
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ══════════════════════════════════════════════
# 🎨  CSS
# ══════════════════════════════════════════════

CSS = """\
@page { margin: 1.5em 2em; }

body {
  font-family: 'Noto Serif CJK TC', 'Source Han Serif TC', 'Songti TC', Georgia, 'Times New Roman', serif;
  line-height: 1.9;
  color: #1a1a1a;
  widows: 2;
  orphans: 2;
}

h1 {
  font-size: 1.6em;
  font-weight: 700;
  color: #1a3a5c;
  margin-top: 1em;
  margin-bottom: 0.6em;
  padding-bottom: 0.3em;
  border-bottom: 3px solid #3498db;
  page-break-before: always;
  letter-spacing: 0.02em;
}
h1:first-of-type { page-break-before: avoid; margin-top: 0.5em; }

h2 {
  font-size: 1.25em;
  font-weight: 600;
  color: #2c5282;
  margin-top: 1.5em;
  margin-bottom: 0.4em;
  padding-left: 0.5em;
  border-left: 4px solid #3498db;
}
h3 {
  font-size: 1.08em;
  font-weight: 600;
  color: #444;
  margin-top: 1.2em;
  margin-bottom: 0.3em;
}

p { margin: 0.5em 0; text-indent: 0; text-align: justify; }

blockquote {
  margin: 1em 0;
  padding: 0.6em 1em;
  background: #f0f7ff;
  border-left: 5px solid #2980b9;
  color: #2c3e50;
  font-style: italic;
}
blockquote p { margin: 0.3em 0; }

pre {
  background: #f7f7f7;
  padding: 0.8em 1em;
  font-size: 0.82em;
  font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  border: 1px solid #e0e0e0;
}
code {
  background: #f0f0f0;
  padding: 0.05em 0.3em;
  font-size: 0.88em;
  font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
}
pre code { background: transparent; padding: 0; }

table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  font-size: 0.88em;
}
th, td {
  border: 1px solid #ccc;
  padding: 0.5em 0.7em;
  vertical-align: top;
}
th {
  background: #2980b9;
  color: white;
  font-weight: 600;
  text-align: center;
  letter-spacing: 0.05em;
}
tr:nth-child(even) td { background: #f9f9f9; }

hr {
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, #bbb, transparent);
  margin: 1.5em 0;
}

ul, ol { margin: 0.5em 0; padding-left: 1.5em; }
li { margin: 0.25em 0; }

b, strong { color: #1a3a5c; }
em { color: #2c5282; }

a { color: #2980b9; text-decoration: none; }

/* ── Chapter divider line ── */
.chapter-end {
  margin-top: 2em;
  text-align: center;
  color: #bbb;
  font-size: 0.85em;
}

/* ── SVG illustration container ── */
.chapter-illustration {
  text-align: center;
  margin: 1em 0 0.5em 0;
}

/* ── Cover illustration ── */
.cover-illustration {
  text-align: center;
  margin: 0.5em 0;
}
"""

# ══════════════════════════════════════════════
# 📝  MD → HTML
# ══════════════════════════════════════════════

def md_to_html(text):
    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # fenced code
        if line.startswith("```"):
            i += 1
            cb = []
            while i < n and not lines[i].startswith("```"):
                cb.append(lines[i])
                i += 1
            i += 1
            out.append(f"<pre><code>{xesc(chr(10).join(cb))}</code></pre>")
            continue

        # table
        if line.startswith("|") and line.endswith("|") and '|' in line[1:-1]:
            rows = []
            while i < n and lines[i].startswith("|") and lines[i].endswith("|") and '|' in lines[i][1:-1]:
                rows.append(lines[i])
                i += 1
            out.append(convert_table(rows))
            continue

        # atx headers
        m = re.match(r'^(#{1,3})\s+(.+)$', line)
        if m:
            tag = f"h{len(m.group(1))}"
            out.append(f"<{tag}>{md_inline(m.group(2).strip())}</{tag}>")
            i += 1
            continue

        # hr
        if re.match(r'^-{3,}$', line.strip()):
            out.append("<hr/>")
            i += 1
            continue

        # blockquote
        if line.startswith(">"):
            qlines = []
            while i < n and lines[i].startswith(">"):
                qlines.append(re.sub(r'^>\s?', '', lines[i]).strip())
                i += 1
            out.append(f"<blockquote><p>{md_inline(' '.join(qlines))}</p></blockquote>")
            continue

        # ul
        if re.match(r'^[\s]*[-*+]\s+', line):
            items = []
            while i < n and re.match(r'^[\s]*[-*+]\s+', lines[i]):
                items.append(md_inline(re.sub(r'^[\s]*[-*+]\s+', '', lines[i])))
                i += 1
            out.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
            continue

        # ol
        if re.match(r'^\s*\d+[\.\)]\s+', line):
            items = []
            while i < n and re.match(r'^\s*\d+[\.\)]\s+', lines[i]):
                items.append(md_inline(re.sub(r'^\s*\d+[\.\)]\s+', '', lines[i])))
                i += 1
            out.append("<ol>" + "".join(f"<li>{it}</li>" for it in items) + "</ol>")
            continue

        # empty line
        if line.strip() == "":
            i += 1
            continue

        # paragraph (multi-line)
        para = []
        while i < n and lines[i].strip():
            l = lines[i]
            if l.startswith("#") or l.startswith("```") or l.startswith("|") or l.startswith(">") or \
               re.match(r'^\s*[-*+]\s+', l) or re.match(r'^\s*\d+[\.\)]\s+', l) or \
               re.match(r'^-{3,}$', l.strip()):
                break
            para.append(l)
            i += 1
        out.append("<p>" + md_inline(" ".join(para).strip()) + "</p>")

    return "\n".join(out)


def convert_table(rows):
    data_start = 0
    is_header = False
    if len(rows) >= 2 and re.match(r'^[\s\|:\-]+$', rows[1]) and '|' in rows[1] and ('-' in rows[1] or ':' in rows[1]):
        is_header = True
        data_start = 2
    html = "<table>"
    if is_header:
        cells = [c.strip() for c in rows[0].split("|")[1:-1]]
        html += "<tr>" + "".join(f"<th>{md_inline(c)}</th>" for c in cells) + "</tr>"
    for r in rows[data_start:]:
        cells = [c.strip() for c in r.split("|")[1:-1]]
        html += "<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in cells) + "</tr>"
    html += "</table>"
    return html


def md_inline(text):
    t = xesc(text)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t


# ══════════════════════════════════════════════
# 🎨  COVER
# ══════════════════════════════════════════════

def make_cover():
    # Big decorative icon
    cover_icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 100" width="120" height="100">
  <!-- abstract sprout / book -->
  <path d="M60 95 L60 40" stroke="#d4e6f9" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M60 50 Q35 35 25 50 Q40 40 60 50" fill="#b3d4f0" opacity="0.8"/>
  <path d="M60 45 Q85 30 95 45 Q80 35 60 45" fill="#b3d4f0" opacity="0.8"/>
  <path d="M60 40 Q80 25 90 38 Q75 28 60 40" fill="#d4e6f9" opacity="0.6"/>
  <circle cx="60" cy="35" r="4" fill="white" opacity="0.5"/>
  <!-- book base -->
  <rect x="25" y="82" width="70" height="8" rx="2" fill="#d4e6f9" opacity="0.3"/>
</svg>'''

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{xesc(TITLE)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body style="text-align:center;padding:12% 5% 5% 5%;background:linear-gradient(180deg,#1a3a5c 0%,#2980b9 40%,#3498db 70%,#f0f7ff 100%);color:white;">
  <div class="cover-illustration">{cover_icon}</div>
  <p style="font-size:0.85em;letter-spacing:0.15em;opacity:0.7;margin-top:1.5em;margin-bottom:1.5em;">2026 年 7 月</p>
  <h1 style="font-size:2.2em;border:none;color:white;font-weight:700;line-height:1.25;margin-bottom:0.6em;page-break-before:avoid;text-shadow:0 2px 8px rgba(0,0,0,0.3);">
    一人公司<br/>生存手冊
  </h1>
  <p style="font-size:1em;color:#d4e6f9;margin-bottom:2em;letter-spacing:0.05em;">國小科技教師版</p>
  <hr style="width:35%;margin:1.5em auto;border:none;height:2px;background:rgba(255,255,255,0.4);"/>
  <p style="font-size:1.05em;color:white;margin-top:1.5em;font-weight:300;">{xesc(AUTHOR)}</p>
  <p style="font-size:0.78em;color:#b3d4f0;margin-top:3em;line-height:1.6;">
    一本寫給國小科技教師的實戰手冊<br/>
    教你用教學專業，創造第二收入曲線
  </p>
</body></html>'''


# ══════════════════════════════════════════════
# 📖  CHAPTER HTML
# ══════════════════════════════════════════════

def make_chapter_html(ch_num, title, body_html):
    svg_ill = ill.get_illustration(ch_num)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:svg="http://www.w3.org/2000/svg">
<head><title>{xesc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
<div class="chapter-illustration">{svg_ill}</div>
{body_html}
<div class="chapter-end">◆ ◇ ◆</div>
</body></html>'''


# ══════════════════════════════════════════════
# 🏗️  BUILD EPUB
# ══════════════════════════════════════════════

os.chdir(DIR)

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    # META-INF
    zf.writestr("META-INF/container.xml",
        '<?xml version="1.0"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
        '</rootfiles></container>')

    # CSS
    zf.writestr("OEBPS/style.css", CSS)

    # Cover
    zf.writestr("OEBPS/cover.xhtml", make_cover())

    manifest = [("ncx","toc.ncx"), ("css","style.css"), ("cover","cover.xhtml")]
    spine = ["cover"]
    ncx_items = [("cover","cover.xhtml","封面")]
    total_chinese = 0

    for idx, (fname, ch_id) in enumerate(CHAPTERS):
        ch_num = idx + 1
        with open(fname, 'r', encoding='utf-8') as f:
            md = f.read()
        tmatch = re.search(r'^#\s+(.+)$', md, re.MULTILINE)
        title = tmatch.group(1).strip() if tmatch else f"第{ch_num}章"

        body = md_to_html(md)
        cn = len(re.findall(r'[\u4e00-\u9fff]', body))
        total_chinese += cn

        xhtml = make_chapter_html(ch_num, title, body)
        xf = f"{ch_id}.xhtml"
        zf.writestr(f"OEBPS/{xf}", xhtml.encode('utf-8'))
        manifest.append((ch_id, xf))
        spine.append(ch_id)
        ncx_items.append((ch_id, xf, title))
        print(f"  {ch_id:5s}  {title:25s}  {cn:>5d} 字  SVG {len(xhtml)}b ✅")

    # OPF
    man = "\n".join(f'    <item id="{i}" href="{f}" media-type="application/xhtml+xml"/>' for i,f in manifest)
    sp  = "\n".join(f'    <itemref idref="{i}"/>' for i in spine)
    zf.writestr("OEBPS/content.opf", f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="BookId">{UID}</dc:identifier>
<dc:title>{xesc(TITLE)}</dc:title>
<dc:creator>{xesc(AUTHOR)}</dc:creator>
<dc:language>zh-TW</dc:language>
<dc:date>{NOW}</dc:date>
</metadata>
<manifest>
<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
<item id="css" href="style.css" media-type="text/css"/>
<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
{man}
</manifest>
<spine toc="ncx">{sp}</spine>
</package>''')

    # NCX
    pts = "\n".join(f'    <navPoint id="{i}" playOrder="{n}"><navLabel><text>{xesc(t)}</text></navLabel><content src="{f}"/></navPoint>' for n,(i,f,t) in enumerate(ncx_items,1))
    zf.writestr("OEBPS/toc.ncx", f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="{UID}"/></head>
<docTitle><text>{xesc(TITLE)}</text></docTitle>
<navMap>{pts}</navMap></ncx>''')

    svg_count = sum(1 for f in zf.namelist() if f.endswith('.xhtml'))
    print(f"\n{'─'*50}")
    print(f"  📖 EPUB：{OUT}")
    print(f"  📦  大小：{os.path.getsize(OUT)/1024:.1f} KB")
    print(f"  📝 中文字：{total_chinese} 字")
    print(f"  🎨  SVG 內嵌插圖：{len(CHAPTERS)} 張")
    print(f"  📄  頁面數（含封面）：{len(spine)}")
    print(f"  {'─'*50}")
