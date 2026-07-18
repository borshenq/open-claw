#!/usr/bin/env python3
"""Generate EPUB: 一人公司生存手冊（國小科技教師版）v2"""

import os, re, uuid, datetime
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
h1 { font-size: 1.5em; color: #2c3e50; margin-top: 1.5em; margin-bottom: 0.5em; border-bottom: 2px solid #3498db; padding-bottom: 0.3em; }
h2 { font-size: 1.2em; color: #34495e; margin-top: 1.2em; margin-bottom: 0.4em; }
h3 { font-size: 1.05em; color: #555; margin-top: 1em; margin-bottom: 0.3em; }
p { margin: 0.4em 0; }
blockquote { border-left: 4px solid #3498db; margin: 0.8em 0; padding: 0.4em 1em; background: #f0f7ff; }
pre { background: #f5f5f5; padding: 0.8em; border-radius: 4px; font-size: 0.85em; white-space: pre-wrap; }
code { background: #f0f0f0; padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.9em; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 0.9em; }
th, td { border: 1px solid #ccc; padding: 0.4em; }
th { background: #3498db; color: white; }
tr:nth-child(even) { background: #f9f9f9; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.2em 0; }
ul, ol { margin: 0.4em 0; padding-left: 1.5em; }
li { margin: 0.2em 0; }
"""

def md_to_html(text):
    """Robust markdown to HTML conversion."""
    lines = text.split("\n")
    out = []
    i = 0
    in_code = False
    code_lines = []
    in_table = False

    while i < len(lines):
        line = lines[i]

        # Code block
        if line.startswith("```"):
            if in_code:
                out.append(f"<pre>{xesc(chr(10).join(code_lines))}</pre>")
                code_lines = []
                in_code = False
                i += 1
                continue
            else:
                in_code = True
                i += 1
                continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Table
        if line.startswith("|") and line.endswith("|"):
            if not in_table:
                out.append("<table>")
                in_table = True
            cells = [c.strip() for c in line.split("|")[1:-1]]
            # determine header row: next line is separator
            is_header = False
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if re.match(r'^[\s\|:\-]+$', next_line) and '|' in next_line and ('-' in next_line or ':' in next_line):
                    is_header = True
                    i += 1  # skip separator
            tag = "th" if is_header else "td"
            out.append("<tr>" + "".join(f"<{tag}>{md_inline(c)}</{tag}>" for c in cells) + "</tr>")
            i += 1
            continue
        else:
            if in_table:
                out.append("</table>")
                in_table = False

        # Headers
        m = re.match(r'^(#{1,3})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{md_inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^-{3,}$', line.strip()):
            out.append("<hr/>")
            i += 1
            continue

        # Blockquote
        if line.startswith(">"):
            text = re.sub(r'^>\s?', '', line).strip()
            out.append(f"<blockquote><p>{md_inline(text)}</p></blockquote>")
            i += 1
            continue

        # Unordered list
        if re.match(r'^[\s]*[-*+]\s+', line):
            out.append(f"<ul>\n<li>{md_inline(re.sub(r'^[\s]*[-*+]\s+', '', line))}</li>")
            i += 1
            while i < len(lines) and re.match(r'^[\s]*[-*+]\s+', lines[i]):
                out.append(f"<li>{md_inline(re.sub(r'^[\s]*[-*+]\s+', '', lines[i]))}</li>")
                i += 1
            out.append("</ul>")
            continue

        # Ordered list (1. 2. etc)
        if re.match(r'^\s*\d+[\.\)]\s+', line):
            out.append(f"<ol>\n<li>{md_inline(re.sub(r'^\s*\d+[\.\)]\s+', '', line))}</li>")
            i += 1
            while i < len(lines) and re.match(r'^\s*\d+[\.\)]\s+', lines[i]):
                out.append(f"<li>{md_inline(re.sub(r'^\s*\d+[\.\)]\s+', '', lines[i]))}</li>")
                i += 1
            out.append("</ol>")
            continue

        # Empty line
        if line.strip() == "":
            out.append("")
            i += 1
            continue

        # Regular paragraph
        out.append(f"<p>{md_inline(line)}</p>")
        i += 1

    if in_code:
        out.append(f"<pre>{xesc(chr(10).join(code_lines))}</pre>")
    if in_table:
        out.append("</table>")

    return "\n".join(out)

def md_inline(text):
    """Convert inline markdown to HTML: bold, italic, code, links."""
    t = xesc(text)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    # links: [text](url)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

# ── Build EPUB ──
import zipfile

os.chdir(DIR)

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    # META-INF
    zf.writestr("META-INF/container.xml", '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>''')

    # CSS
    zf.writestr("OEBPS/style.css", CSS)

    # Cover
    zf.writestr("OEBPS/cover.xhtml", f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{xesc(TITLE)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body style="text-align:center;padding-top:20%;">
<h1 style="font-size:2em;border:none;">{xesc(TITLE)}</h1>
<p style="font-size:1.2em;color:#666;margin-top:2em;">{xesc(AUTHOR)}</p>
<p style="font-size:0.9em;color:#999;margin-top:3em;">2026 年 7 月</p>
</body></html>''')

    manifest = [("ncx","toc.ncx"), ("css","style.css"), ("cover","cover.xhtml")]
    spine = ["cover"]
    ncx_items = [("cover","cover.xhtml","封面")]
    total_chinese = 0

    for filename, ch_id in CHAPTERS:
        with open(filename, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Extract title
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ch_id

        # Convert
        body_html = md_to_html(md_content)
        chinese = len(re.findall(r'[\u4e00-\u9fff]', body_html))
        total_chinese += chinese

        xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{xesc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>\n{body_html}\n</body></html>'''

        fname = f"{ch_id}.xhtml"
        zf.writestr(f"OEBPS/{fname}", xhtml.encode('utf-8'))
        manifest.append((ch_id, fname))
        spine.append(ch_id)
        ncx_items.append((ch_id, fname, title))

    # OPF
    man = "\n".join(f'    <item id="{i}" href="{f}" media-type="application/xhtml+xml"/>' for i, f in manifest)
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
    pts = "\n".join(
        f'    <navPoint id="{i}" playOrder="{n}">'
        f'<navLabel><text>{xesc(t)}</text></navLabel>'
        f'<content src="{f}"/></navPoint>'
        for n, (i, f, t) in enumerate(ncx_items, 1)
    )
    zf.writestr("OEBPS/toc.ncx", f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="{UID}"/></head>
  <docTitle><text>{xesc(TITLE)}</text></docTitle>
  <navMap>{pts}</navMap>
</ncx>''')

print(f"✅ EPUB v2 已產生：{OUT}")
print(f"   大小：{os.path.getsize(OUT)/1024:.1f} KB")
print(f"   中文字：{total_chinese} 字")
print(f"   章節：{len(CHAPTERS)} 篇 + 封面")
