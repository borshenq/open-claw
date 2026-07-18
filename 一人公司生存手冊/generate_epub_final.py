#!/usr/bin/env python3
"""Generate faithful EPUB from markdown files."""

import os, re, uuid, datetime, zipfile
from xml.sax.saxutils import escape as xesc

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

CSS = """\
@page { margin: 1em 1.5em; }
body { font-family: serif; line-height: 1.8; color: #222; }
h1 { font-size: 1.5em; color: #2c3e50; margin-top: 1.5em; margin-bottom: 0.5em; border-bottom: 2px solid #3498db; padding-bottom: 0.3em; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 1.2em; color: #34495e; margin-top: 1.2em; margin-bottom: 0.4em; }
h3 { font-size: 1.05em; color: #555; margin-top: 1em; margin-bottom: 0.3em; }
p { margin: 0.4em 0; }
blockquote { border-left: 4px solid #3498db; margin: 0.8em 0; padding: 0.4em 1em; background: #f0f7ff; }
blockquote p { margin: 0.2em 0; }
pre { background: #f5f5f5; padding: 0.8em; font-size: 0.85em; white-space: pre-wrap; word-wrap: break-word; border: 1px solid #ddd; }
code { background: #f0f0f0; padding: 0.1em 0.3em; font-size: 0.9em; }
pre code { background: transparent; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 0.9em; }
th, td { border: 1px solid #ccc; padding: 0.4em 0.6em; vertical-align: top; }
th { background: #3498db; color: white; }
tr:nth-child(even) td { background: #f9f9f9; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.2em 0; }
ul, ol { margin: 0.4em 0; padding-left: 1.5em; }
li { margin: 0.2em 0; }
"""

# ◈◈◈◈◈ BLOCK-LEVEL MD → HTML ◈◈◈◈◈

def md_to_html(text):
    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # fenced code block
        if line.startswith("```"):
            lang = line[3:].strip()
            i += 1
            cb = []
            while i < n and not lines[i].startswith("```"):
                cb.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            out.append(f"<pre><code>{xesc(chr(10).join(cb))}</code></pre>")
            continue

        # table
        if line.startswith("|") and line.endswith("|") and '|' in line[1:-1]:
            rows = []
            in_table = False
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

        # empty
        if line.strip() == "":
            i += 1
            continue

        # paragraph
        para = []
        while i < n and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith("```") and not lines[i].startswith("|") and not lines[i].startswith(">") and not re.match(r'^\s*[-*+]\s+', lines[i]) and not re.match(r'^\s*\d+[\.\)]\s+', lines[i]) and not re.match(r'^-{3,}$', lines[i].strip()):
            para.append(lines[i])
            i += 1
        out.append("<p>" + md_inline(" ".join(para).strip()) + "</p>")

    return "\n".join(out)


def convert_table(rows):
    """Convert markdown table rows to HTML table."""
    # skip separator row (row 1 if it's dashes)
    data_start = 0
    is_header = False
    if len(rows) >= 2 and re.match(r'^[\s\|:\-]+$', rows[1]) and '|' in rows[1] and ('-' in rows[1] or ':' in rows[1]):
        is_header = True
        data_start = 2

    html = ["<table>"]
    if is_header:
        cells = [c.strip() for c in rows[0].split("|")[1:-1]]
        html.append("<tr>" + "".join(f"<th>{md_inline(c)}</th>" for c in cells) + "</tr>")
    for r in rows[data_start:]:
        cells = [c.strip() for c in r.split("|")[1:-1]]
        html.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in cells) + "</tr>")
    html.append("</table>")
    return "\n".join(html)


def md_inline(text):
    t = xesc(text)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    # remove extra spaces from xml escaping
    return t


# ◈◈◈◈◈ BUILD EPUB ◈◈◈◈◈

os.chdir(DIR)

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    # container.xml
    zf.writestr("META-INF/container.xml",
        '<?xml version="1.0"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
        '</rootfiles></container>')

    # CSS
    zf.writestr("OEBPS/style.css", CSS)

    # Cover
    zf.writestr("OEBPS/cover.xhtml", f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>{xesc(TITLE)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body style="text-align:center;padding-top:20%;">
<h1 style="font-size:2em;border:none;page-break-before:avoid;">{xesc(TITLE)}</h1>
<p style="font-size:1.2em;color:#666;margin-top:2em;">{xesc(AUTHOR)}</p>
<p style="font-size:0.9em;color:#999;margin-top:3em;">2026 年 7 月</p>
</body></html>''')

    manifest = [("ncx","toc.ncx"), ("css","style.css"), ("cover","cover.xhtml")]
    spine = ["cover"]
    ncx_items = [("cover","cover.xhtml","封面")]
    total_chinese = 0

    for fname, ch_id in CHAPTERS:
        with open(fname, 'r', encoding='utf-8') as f:
            md = f.read()
        # title from first heading
        tmatch = re.search(r'^#\s+(.+)$', md, re.MULTILINE)
        title = tmatch.group(1).strip() if tmatch else ch_id

        body = md_to_html(md)
        cn = len(re.findall(r'[\u4e00-\u9fff]', body))
        total_chinese += cn

        xh = f'<?xml version="1.0" encoding="UTF-8"?>\n<html xmlns="http://www.w3.org/1999/xhtml"><head><title>{xesc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>\n{body}\n</body></html>'
        xf = f"{ch_id}.xhtml"
        zf.writestr(f"OEBPS/{xf}", xh.encode('utf-8'))
        manifest.append((ch_id, xf))
        spine.append(ch_id)
        ncx_items.append((ch_id, xf, title))

    # OPF
    man = "\n".join(f'    <item id="{i}" href="{f}" media-type="application/xhtml+xml"/>' for i,f in manifest)
    sp = "\n".join(f'    <itemref idref="{i}"/>' for i in spine)
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

print(f"✅ EPUB 已產生：{OUT}")
print(f"   大小：{os.path.getsize(OUT)/1024:.1f} KB")
print(f"   中文字：{total_chinese} 字")
