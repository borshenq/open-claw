#!/usr/bin/env python3
"""Generate EPUB: 一人公司生存手冊（國小科技教師版）"""

import os, re, uuid, datetime, html
from xml.sax.saxutils import escape as xml_escape

DIR = "/home/borsheng/.openclaw/workspace/一人公司生存手冊"
OUT = os.path.join(DIR, "一人公司生存手冊.epub")

# ── Chapters in order ──
CHAPTERS = [
    ("01-為什麼國小老師需要一人公司.md", "01-為什麼國小老師需要一人公司.md"),
    ("02-產品-科技教師版.md", "02-產品"),
    ("03-定價-科技教師版.md", "03-定價"),
    ("04-行銷-科技教師版.md", "04-客戶從哪裡來？"),
    ("05-時間管理-科技教師版.md", "05-時間管理"),
    ("06-財務-科技教師版.md", "06-財務"),
    ("07-系統化-科技教師版.md", "07-系統化"),
    ("08-健康-科技教師版.md", "08-健康"),
    ("09-AI工具.md", "09-AI工具"),
    ("10-正職與一人公司.md", "10-一人公司 × 學校正職"),
]

BOOK_TITLE = "一人公司生存手冊（國小科技教師版）"
BOOK_AUTHOR = "Juang Borsheng"
BOOK_ID = "urn:uuid:" + str(uuid.uuid4())
NOW = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Simple markdown to HTML ──
def md_to_html(text):
    lines = text.split("\n")
    out = []
    in_table = False
    in_code = False
    code_buf = []
    for line in lines:
        # Code block
        if line.startswith("```"):
            if in_code:
                out.append("<pre>" + xml_escape("\n".join(code_buf)) + "</pre>")
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        # Empty line
        if line.strip() == "":
            if in_table:
                out.append("</table>")
                in_table = False
            out.append("")
            continue
        # Table separator
        if re.match(r'^[\s\|:,\-]+$', line) and '|' in line and ('-' in line or ':' in line):
            continue
        # Table row
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not in_table:
                out.append("<table>")
                out.append("<tr>" + "".join(f"<th>{xml_escape(c)}</th>" for c in cells) + "</tr>")
                in_table = True
            else:
                out.append("<tr>" + "".join(f"<td>{xml_escape(c)}</td>" for c in cells) + "</tr>")
            continue
        # Headers
        m = re.match(r'^(#{1,3})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            out.append(f"<h{level}>{xml_escape(text)}</h{level}>")
            continue
        # Horizontal rule
        if re.match(r'^---+$', line.strip()):
            out.append("<hr/>")
            continue
        # Blockquote
        if line.startswith(">"):
            text = line.lstrip("> ").strip()
            out.append(f"<blockquote><p>{xml_escape(text)}</p></blockquote>")
            continue
        # Bold/Italic within line
        text = xml_escape(line)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        # Inline code
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        out.append(f"<p>{text}</p>")
    if in_table:
        out.append("</table>")
    # Remove trailing empty paragraphs
    result = "\n".join(out)
    result = re.sub(r'<p></p>\n*', '', result)
    return result

# ── Read chapter content ──
def read_chapter(filepath):
    path = os.path.join(DIR, filepath)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ── Build EPUB components ──
CSS = """\
body { font-family: 'Noto Sans TC', 'Helvetica Neue', Arial, sans-serif;
       line-height: 1.8; color: #333; padding: 1em; }
h1 { font-size: 1.6em; color: #2c3e50; margin-top: 1.5em; border-bottom: 2px solid #3498db; padding-bottom: 0.3em; }
h2 { font-size: 1.3em; color: #34495e; margin-top: 1.2em; }
h3 { font-size: 1.1em; color: #555; margin-top: 1em; }
p { margin: 0.5em 0; text-indent: 0; }
blockquote { border-left: 4px solid #3498db; margin: 1em 0; padding: 0.5em 1em; background: #f0f7ff; color: #2c3e50; }
blockquote p { margin: 0; }
pre { background: #f5f5f5; padding: 1em; border-radius: 4px; font-size: 0.85em; overflow-x: auto; }
code { background: #f0f0f0; padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.9em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9em; }
th, td { border: 1px solid #ddd; padding: 0.5em; text-align: left; }
th { background: #3498db; color: white; }
tr:nth-child(even) { background: #f9f9f9; }
hr { border: none; border-top: 1px solid #ddd; margin: 1.5em 0; }
"""

def make_container():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

def make_opf(manifest_items, spine_order):
    man = "\n".join(f'    <item id="{i}" href="{f}" media-type="application/xhtml+xml"/>' for i, f in manifest_items)
    spine = "\n".join(f'    <itemref idref="{i}"/>' for i in spine_order)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="BookId">{BOOK_ID}</dc:identifier>
    <dc:title>{xml_escape(BOOK_TITLE)}</dc:title>
    <dc:creator>{xml_escape(BOOK_AUTHOR)}</dc:creator>
    <dc:language>zh-TW</dc:language>
    <dc:date>{NOW}</dc:date>
    <meta name="cover" content="cover"/>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
{man}
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover"/>
{spine}
  </spine>
  <guide>
    <reference type="cover" title="封面" href="cover.xhtml"/>
  </guide>
</package>'''

def make_ncx(items):
    points = "\n".join(
        f'    <navPoint id="{i}" playOrder="{n}">'
        f'<navLabel><text>{xml_escape(title)}</text></navLabel>'
        f'<content src="{file}"/></navPoint>'
        for n, (i, file, title) in enumerate(items, 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.dtd.org/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{BOOK_ID}"/>
  </head>
  <docTitle><text>{xml_escape(BOOK_TITLE)}</text></docTitle>
  <navMap>
{points}
  </navMap>
</ncx>'''

def make_cover():
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{xml_escape(BOOK_TITLE)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body style="text-align:center; padding-top:20%;">
<h1 style="font-size:2em; border:none;">{xml_escape(BOOK_TITLE)}</h1>
<p style="font-size:1.2em; color:#666; margin-top:2em;">{xml_escape(BOOK_AUTHOR)}</p>
<p style="font-size:0.9em; color:#999; margin-top:3em;">2026 年 7 月</p>
</body></html>'''

def make_chapter_xhtml(content, title):
    body_html = md_to_html(content)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{xml_escape(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{body_html}
</body></html>'''

# ── Generate EPUB ──
import zipfile

os.chdir(DIR)

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    # META-INF
    zf.writestr("META-INF/container.xml", make_container())

    # CSS
    zf.writestr("OEBPS/style.css", CSS)

    # Cover
    zf.writestr("OEBPS/cover.xhtml", make_cover())

    manifest = [
        ("ncx", "toc.ncx"),
        ("css", "style.css"),
        ("cover", "cover.xhtml"),
    ]
    spine = []
    ncx_items = [("cover", "cover.xhtml", "封面")]

    for idx, (filename, short_title) in enumerate(CHAPTERS):
        content = read_chapter(filename)
        # Extract actual title from first h1
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else short_title
        xhtml = make_chapter_xhtml(content, title)

        id_name = f"ch{idx+1:02d}"
        xhtml_file = f"ch{idx+1:02d}.xhtml"

        zf.writestr(f"OEBPS/{xhtml_file}", xhtml.encode("utf-8"))
        manifest.append((id_name, xhtml_file))
        spine.append(id_name)
        ncx_items.append((id_name, xhtml_file, title))

    # OPF
    zf.writestr("OEBPS/content.opf", make_opf(manifest, spine))

    # NCX
    zf.writestr("OEBPS/toc.ncx", make_ncx(ncx_items))

print(f"✅ EPUB 已產生：{OUT}")
print(f"   大小：{os.path.getsize(OUT) / 1024:.1f} KB")
print(f"   包含：1 封面 + 10 章節 + CSS + 目錄")
