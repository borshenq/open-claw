#!/usr/bin/env python3
"""繪製大屯國小網路拓撲圖 — 純 Pillow PNG"""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1100, 1150
FONT_DIR = "/usr/share/fonts"
BG = (248, 250, 252)
FG = (23, 20, 51)
MUTED = (91, 100, 117)
LINE = (100, 116, 139)

def load_font(size):
    paths = [
        os.path.join(FONT_DIR, "truetype/noto/NotoSansCJK-Regular.ttc"),
        os.path.join(FONT_DIR, "opentype/noto/NotoSansCJK-Regular.ttc"),
        os.path.join(FONT_DIR, "truetype/wqy/wqy-zenhei.ttc"),
        os.path.join(FONT_DIR, "truetype/droid/DroidSansFallbackFull.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                return ImageFont.truetype(p, size, encoding="unic")
    return ImageFont.load_default()

F10 = load_font(10)
F11 = load_font(11)
F12 = load_font(12)
F13 = load_font(13)
F14 = load_font(14)

def center(draw, y, text, font=F12, fill=FG):
    bb = draw.textbbox((0, 0), text, font=font)
    x = (W - (bb[2]-bb[0])) // 2
    draw.text((x, y), text, font=font, fill=fill)

def left(draw, x, y, text, font=F10, fill=MUTED):
    draw.text((x, y), text, font=font, fill=fill)

def rbox(draw, x, y, w, h, fill, text="", font=F10, text_fill=FG, radius=5, thick=1):
    draw.rounded_rectangle((x, y, x+w, y+h), radius=radius, fill=fill, outline=LINE, width=thick)
    if text:
        bb = draw.textbbox((0, 0), text, font=font)
        tx = x + (w - (bb[2]-bb[0])) // 2
        ty = y + (h - (bb[3]-bb[1])) // 2
        draw.text((tx, ty), text, font=font, fill=text_fill)

def arrow(draw, x1, y1, x2, y2, color=LINE, width=1):
    draw.line((x1, y1, x2, y2), fill=color, width=width)

def port_box(draw, x, y, title, lines, uplink=""):
    """Draw a port mapping box"""
    bh = 30 + len(lines) * 16 + (12 if uplink else 0)
    bw = 210
    draw.rounded_rectangle((x, y, x+bw, y+bh), radius=6, fill=(235, 240, 249), outline=LINE, width=1)
    # Title
    bb = draw.textbbox((0, 0), title, font=F11)
    draw.text((x + (bw - (bb[2]-bb[0]))//2, y + 6), title, font=F11, fill=(88, 28, 135))
    # Lines
    for i, line in enumerate(lines):
        draw.text((x + 8, y + 26 + i*16), line, font=F10, fill=MUTED)
    # Uplink
    if uplink:
        draw.text((x + 8, y + bh - 16), uplink, font=F10, fill=(88, 28, 135))


img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# WAN
center(draw, 10, "☁ WAN (163.21.221.124/25 — 教育部連線)", F12, MUTED)
arrow(draw, W//2, 28, W//2, 60)

# FortiGate
rbox(draw, 370, 65, 360, 55, (191, 219, 254))
center(draw, 72, "FortiGate-500E · 192.60.1.254", F13)
center(draw, 88, "DTPS-FG5H0ETB19909536 · FortiOS 7.0.17 ✅ SNMP", F10, MUTED)
center(draw, 104, "📡 CAPWAP port8:5247 · 16 FortiAPs 管控中", F10, MUTED)
arrow(draw, W//2, 120, W//2, 155)

# Core Switch
rbox(draw, 340, 160, 420, 50, (199, 210, 254))
center(draw, 168, "🔀 Aruba 8100 核心交換器 (.245) · 48x SFP+ 10G ✅SNMP", F12)
center(draw, 184, "Port1→FS(.5) · Port5→FS備 · Port29→.254主 · Port31→.254備", F10, MUTED)
center(draw, 198, "Port17→HP.17+NVR.167+UPS.249 · Port27→OpenClaw.153+Konica.97+Huawei.131", F10, MUTED)

# Downlink labels
down_y = 235
for px, label in [(360, "Port23→.246"), (440, "Port27→.247"), (520, "Port25→.248"),
                  (600, "Port21→AP"), (680, "Port17→終端"), (760, "Port27→3050")]:
    arrow(draw, px+6, 210, px+6, 245, width=1)
    F9 = load_font(9)
draw.text((px-10, 228), label, font=F9, fill=(88, 28, 135))

# FortiAP Zone
draw.rounded_rectangle((20, 255, 280, 400), radius=8, fill=(235,240,249), outline=LINE, width=1)
left(draw, 40, 264, "📡 FortiAP 群 (CAPWAP→.254:5247)", F11, (88,28,135))
draw.line((540, 210, 160, 255), fill=LINE, width=1)
aps = [
    "A1大辦公室 .117    A2校長室 .140",
    "4年級 .141    5年級 .142    3年級 .137",
    "2年級 .156    1年級 .170    圖書館 .143",
    "自然教室 .149    資源班 .122",
    "舊多元 .102    新多元 .145",
    "B1警衛室 .155    B2廚房 .148",
    "幼兒園 .146    會計室 .169",
]
for i, a in enumerate(aps):
    draw.text((30, 283 + i*16), f"📍 {a}", font=F10, fill=MUTED)

# Switches row1: .246, .247, .248
for i, (sx, label, uplink) in enumerate([
    (320, "Aruba 2930F (.246) ✅", "Uplink Port27→核心Port23"),
    (530, "Aruba 2930F (.247) ✅", "Uplink Port28→核心Port27"),
    (740, "Aruba 2930F (.248) ✅", "Uplink Port25→核心Port25"),
]):
    rbox(draw, sx, 255, 160, 36, (187, 247, 208))
    center(draw, sy:=263, label, F11)
    draw.text((sx+5, sy+15), uplink, font=F10, fill=MUTED)

# Port boxes row1
port_boxes = {
    "📌 .246 Port Map": [
        "P4: Intel .136       P5: Brother .151",
        "P12: 會計室 .169    P13: AP 自然 .149",
        "P14: AP 5年級 .142",
        "P15: 幼兒園 .146",
        "P16: AP 4年級 .141",
        "P17: 校長室 .140",
        "P20: IoT/辦公",
    ],
    "📌 .247 Port Map": [
        "P5: AP 圖書館 .143",
        "P7: ASUS .111/.116",
        "P9: Cisco .200 / Konica .98",
        "P10: Intel .105    P12: Apple .158",
        "P13: AP A1大辦公室 .117",
        "P18/19: AP 3年級 .137",
        "P26: ↔ Aruba .251",
    ],
    "📌 .248 Port Map": [
        "P11: Fujifilm .240",
        "P12: Brother .138",
        "P13: AP 2年級 .156",
        "P14: AP 1年級 .170",
        "P16: 幼兒園",
    ],
}
port_y = 300
for title, lines in port_boxes.items():
    port_box(draw, 320 if "246" in title else 530 if "247" in title else 740, port_y, title, lines, "⬆ Uplink to Core")

# Arrow to .251/.252
arrow(draw, 546+6, 300, 570, 475)
arrow(draw, 656+6, 300, 630, 475)

# .251 & .252
rbox(draw, 330, 480, 160, 36, (187, 247, 208))
center(draw, 488, "Aruba 2930F (.251) ✅", F11)
draw.text((335, 500), "Uplink Port28→核心", font=F10, fill=MUTED)

rbox(draw, 540, 480, 160, 36, (187, 247, 208))
center(draw, 488, "Cisco Catalyst (.252) ✅", F11)
draw.text((545, 500), "Uplink Port32→核心", font=F10, fill=MUTED)

port_box(draw, 320, 525, "📌 .251 Port Map", [
    "P1: HP .31        P2: HP .32",
    "P6: Intel .148    P10: Intel .105",
    "P11: ASUS .116    P12: Konica .99",
    "P18: ASUS .188 IoT",
], "⬆ Port28→核心")

port_box(draw, 530, 525, "📌 .252 Port Map", [
    "P1: ASUS .30      P8: Konica .97",
    "P11: Apple .158   P12: Huawei .131",
    "P15: Intel .154",
], "⬆ Port32→核心")

# Terminal devices
ty = 710
draw.rounded_rectangle((20, ty, W-20, ty+180), radius=8, fill=(235,240,249), outline=LINE, width=1)
center(draw, ty+12, "💻 有線終端設備", F11, (88,28,135))
lines = [
    "【 NAS/伺服器 】Synology DS925+ .127  ·  FS .5  ·  w2 .6  ·  VMware ESXi .7",
    "【 虛擬主機 】OpenClaw VM .153  ·  FortiGate VM  ·  Redmine  ·  FastAPI  ·  SearXNG",
    "【 印表機 ×9 】Brother MFC .138/.151  ·  Fujifilm C325 .240  ·  Konica ×3",
    "【 監控 & 環境 】Axis 攝影 .42/.125  ·  GeoVision NVR .167  ·  Delta UPS .249",
    "【 辦公電腦 】Intel/ASUS: .105 .111 .116 .120 .148 .152 .155",
    "【 離線電腦 】.20 .129 .134 .135 .136 .144 .147 .150 .154 .168",
    "【 IoT/其他 】Huawei .131  ·  Apple .158",
]
for i, l in enumerate(lines):
    draw.text((30, ty + 32 + i*20), l, font=F10, fill=MUTED)

# SSID
sy2 = 910
draw.rounded_rectangle((20, sy2, W-20, sy2+75), radius=8, fill=(235,240,249), outline=LINE, width=1)
center(draw, sy2+12, "📱 SSID / VLAN 結構", F11, (88,28,135))
ssid_lines = [
    "🏫 staff (192.60.1.x)    📚 class (192.168.0.x)    📱 st (192.168.50.x)",
    "🌐 iTaiwan (10.168.201.x)    🎓 TANetRoaming (10.168.202.x)    eduroam (10.168.203.x)",
    "📹 監控 VLAN (192.168.10.x)",
]
for i, l in enumerate(ssid_lines):
    draw.text((30, sy2 + 34 + i*18), l, font=F10, fill=MUTED)

# Wireless Clients
wy = 1005
draw.rounded_rectangle((20, wy, W-20, wy+75), radius=8, fill=(235,240,249), outline=LINE, width=1)
center(draw, wy+12, "📊 23 台無線用戶端在線", F11, (88,28,135))
wl_lines = [
    "🏫 4年級 16台    5年級 12台    📚 圖書館 13台 (iPad A05~A35)",
    "📍 A1大辦公室 · A2校長室 · 資源班 · 新多元 · 幼兒園 · 會計室",
    "📱 iOS/iPadOS ~50+    💻 macOS ~6    🖥️ Windows ~5    🤖 Android ~2",
]
for i, l in enumerate(wl_lines):
    draw.text((30, wy + 34 + i*18), l, font=F10, fill=MUTED)

# Footer
draw.text((20, 1105), "🌐 DTPS 大屯國小 · 臺北市北投區", font=F10, fill=MUTED)
center(draw, 1105, "🤖 Flora 🌸 自動產生 · 2026-06-17", F10, MUTED)
bb = draw.textbbox((0,0), "SNMP: SnmpPublic@TPC ✅", font=F10)
draw.text((W-bb[2]-10, 1105), "SNMP: SnmpPublic@TPC ✅", font=F10, fill=MUTED)

out = "/home/borsheng/.openclaw/workspace/dtps-topology.png"
img.save(out, "PNG")
print(f"✅ Saved {out} ({os.path.getsize(out)} bytes)")
