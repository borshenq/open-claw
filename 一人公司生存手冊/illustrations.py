#!/usr/bin/env python3
"""SVG illustrations for each chapter of 一人公司生存手冊."""

from xml.sax.saxutils import escape as xesc

# Color palette
C_PRIMARY = "#2980b9"   # blue
C_ACCENT = "#3498db"    # light blue
C_LIGHT = "#d4e6f9"    # very light blue
C_DARK = "#1a3a5c"     # dark navy
C_GRAY = "#888888"     # gray
C_BG = "#f0f7ff"       # background

def _svg(w, h, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
{body}</svg>'''

# ── Chapter 1: 種子 / 成長 ──
# A hand planting a sprout in soil
def ch01():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- soil -->
  <ellipse cx="100" cy="105" rx="60" ry="15" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1.5"/>
  <!-- sprout stem -->
  <path d="M100 105 L100 65" stroke="{C_PRIMARY}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <!-- leaves -->
  <path d="M100 75 Q85 60 95 70 Q100 65 100 75" fill="{C_ACCENT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <path d="M100 60 Q115 45 105 55 Q100 50 100 60" fill="{C_ACCENT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <!-- small flower -->
  <circle cx="100" cy="50" r="4" fill="white" stroke="{C_PRIMARY}" stroke-width="1"/>
  <circle cx="96" cy="47" r="3" fill="white" stroke="{C_PRIMARY}" stroke-width="0.8"/>
  <circle cx="104" cy="47" r="3" fill="white" stroke="{C_PRIMARY}" stroke-width="0.8"/>
  <circle cx="97" cy="53" r="3" fill="white" stroke="{C_PRIMARY}" stroke-width="0.8"/>
  <circle cx="103" cy="53" r="3" fill="white" stroke="{C_PRIMARY}" stroke-width="0.8"/>
''')

# ── Chapter 2: 產品 / 盒子 ──
# Gift box with ribbon
def ch02():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- box body -->
  <rect x="65" y="55" width="70" height="60" rx="4" fill="white" stroke="{C_PRIMARY}" stroke-width="2"/>
  <!-- lid -->
  <rect x="60" y="45" width="80" height="15" rx="4" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="2"/>
  <!-- ribbon vertical -->
  <line x1="100" y1="45" x2="100" y2="115" stroke="{C_ACCENT}" stroke-width="3"/>
  <!-- ribbon horizontal -->
  <line x1="65" y1="52" x2="135" y2="52" stroke="{C_ACCENT}" stroke-width="3"/>
  <!-- bow -->
  <path d="M100 40 Q85 25 100 35 Q115 25 100 40" fill="{C_ACCENT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <!-- price tag -->
  <text x="100" y="100" text-anchor="middle" font-size="11" fill="{C_DARK}" font-family="sans-serif">NT$</text>
''')

# ── Chapter 3: 定價 / 標籤 ──
# Price tag with coin
def ch03():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- coin -->
  <circle cx="100" cy="65" r="25" fill="white" stroke="{C_PRIMARY}" stroke-width="2"/>
  <circle cx="100" cy="65" r="20" fill="none" stroke="{C_ACCENT}" stroke-width="1" stroke-dasharray="3,3"/>
  <!-- dollar sign -->
  <!-- <text x="100" y="72" text-anchor="middle" font-size="22" font-weight="bold" fill="{C_DARK}">$</text> -->
  <!-- price tag -->
  <circle cx="100" cy="65" r="10" fill="{C_ACCENT}" stroke="none"/>
  <text x="100" y="70" text-anchor="middle" font-size="14" font-weight="bold" fill="white">$</text>
  <!-- arrows up -->
  <path d="M60 115 L100 95 L140 115" stroke="{C_GRAY}" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M100 95 L100 82" stroke="{C_PRIMARY}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <polygon points="97,85 103,85 100,77" fill="{C_PRIMARY}"/>
  <!-- label -->
  <rect x="45" y="118" width="110" height="16" rx="8" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <text x="100" y="130" text-anchor="middle" font-size="9" fill="{C_DARK}" font-family="sans-serif">你的專業值得多少？</text>
''')

# ── Chapter 4: 行銷 / 目標 ──
# Bullseye target
def ch04():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- target circles -->
  <circle cx="100" cy="75" r="40" fill="none" stroke="{C_GRAY}" stroke-width="1.5"/>
  <circle cx="100" cy="75" r="30" fill="none" stroke="{C_ACCENT}" stroke-width="2"/>
  <circle cx="100" cy="75" r="20" fill="none" stroke="{C_PRIMARY}" stroke-width="2"/>
  <circle cx="100" cy="75" r="10" fill="{C_PRIMARY}" stroke="none"/>
  <!-- crosshairs -->
  <line x1="50" y1="75" x2="150" y2="75" stroke="{C_DARK}" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="100" y1="35" x2="100" y2="115" stroke="{C_DARK}" stroke-width="1" stroke-dasharray="4,4"/>
  <!-- arrow hitting center -->
  <line x1="155" y1="55" x2="115" y2="70" stroke="{C_DARK}" stroke-width="2" stroke-linecap="round"/>
  <polygon points="155,55 148,52 153,60" fill="{C_DARK}"/>
  <!-- label -->
  <text x="100" y="132" text-anchor="middle" font-size="9" fill="{C_DARK}" font-family="sans-serif">客戶在哪裡？</text>
''')

# ── Chapter 5: 時間 / 時鐘 ──
# Clock with priority
def ch05():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- clock face -->
  <circle cx="100" cy="65" r="35" fill="white" stroke="{C_PRIMARY}" stroke-width="2.5"/>
  <!-- hour markers -->
  <line x1="100" y1="32" x2="100" y2="40" stroke="{C_DARK}" stroke-width="1.5"/>
  <line x1="100" y1="90" x2="100" y2="98" stroke="{C_DARK}" stroke-width="1.5"/>
  <line x1="67" y1="65" x2="75" y2="65" stroke="{C_DARK}" stroke-width="1.5"/>
  <line x1="125" y1="65" x2="133" y2="65" stroke="{C_DARK}" stroke-width="1.5"/>
  <!-- hands: 10:10 -->
  <line x1="100" y1="65" x2="80" y2="45" stroke="{C_DARK}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="100" y1="65" x2="115" y2="52" stroke="{C_DARK}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="100" cy="65" r="3" fill="{C_PRIMARY}"/>
  <!-- small gear icon -->
  <circle cx="150" cy="110" r="12" fill="none" stroke="{C_ACCENT}" stroke-width="1.5"/>
  <circle cx="150" cy="110" r="5" fill="none" stroke="{C_ACCENT}" stroke-width="1"/>
  <line x1="150" y1="100" x2="150" y2="98" stroke="{C_ACCENT}" stroke-width="1.5"/>
  <line x1="150" y1="120" x2="150" y2="122" stroke="{C_ACCENT}" stroke-width="1.5"/>
  <line x1="140" y1="110" x2="138" y2="110" stroke="{C_ACCENT}" stroke-width="1.5"/>
  <line x1="160" y1="110" x2="162" y2="110" stroke="{C_ACCENT}" stroke-width="1.5"/>
  <!-- weekend highlight -->
  <text x="35" y="120" font-size="8" fill="{C_GRAY}" font-family="sans-serif">平日養素材</text>
  <text x="35" y="132" font-size="8" fill="{C_PRIMARY}" font-family="sans-serif">週末 2h 產出</text>
''')

# ── Chapter 6: 財務 / 階梯 ──
# Staircase going up
def ch06():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- staircase -->
  <rect x="40" y="105" width="30" height="12" rx="2" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <rect x="70" y="90" width="30" height="27" rx="2" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <rect x="100" y="72" width="30" height="45" rx="2" fill="{C_ACCENT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <rect x="130" y="50" width="30" height="67" rx="2" fill="{C_PRIMARY}" stroke="{C_DARK}" stroke-width="1"/>
  <!-- arrow going up -->
  <path d="M45 30 L100 30 L100 50" stroke="{C_DARK}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <polygon points="97,47 103,47 100,55" fill="{C_DARK}"/>
  <!-- labels -->
  <text x="55" y="100" text-anchor="middle" font-size="7" fill="{C_DARK}" font-family="sans-serif">1k</text>
  <text x="85" y="85" text-anchor="middle" font-size="7" fill="{C_DARK}" font-family="sans-serif">5k</text>
  <text x="115" y="68" text-anchor="middle" font-size="7" fill="white" font-family="sans-serif">2w</text>
  <text x="145" y="47" text-anchor="middle" font-size="7" fill="white" font-family="sans-serif">5w+</text>
  <!-- revenue tiers -->
  <text x="100" y="135" text-anchor="middle" font-size="8" fill="{C_GRAY}" font-family="sans-serif">被動收入階梯</text>
''')

# ── Chapter 7: 系統化 / 齒輪 ──
# Interlocking gears
def ch07():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- large gear -->
  <circle cx="85" cy="70" r="30" fill="none" stroke="{C_PRIMARY}" stroke-width="2.5"/>
  <circle cx="85" cy="70" r="22" fill="none" stroke="{C_ACCENT}" stroke-width="1.5" stroke-dasharray="4,4"/>
  <circle cx="85" cy="70" r="10" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1.5"/>
  <circle cx="85" cy="70" r="4" fill="{C_PRIMARY}" />
  <!-- gear teeth large -->
  <g stroke="{C_PRIMARY}" stroke-width="2" stroke-linecap="round">
    <line x1="85" y1="38" x2="85" y2="32"/>
    <line x1="85" y1="102" x2="85" y2="108"/>
    <line x1="53" y1="70" x2="47" y2="70"/>
    <line x1="117" y1="70" x2="123" y2="70"/>
    <line x1="62" y1="47" x2="58" y2="43"/>
    <line x1="108" y1="93" x2="112" y2="97"/>
  </g>
  <!-- small gear -->
  <circle cx="130" cy="95" r="15" fill="none" stroke="{C_ACCENT}" stroke-width="2"/>
  <circle cx="130" cy="95" r="6" fill="{C_LIGHT}" stroke="{C_ACCENT}" stroke-width="1"/>
  <circle cx="130" cy="95" r="2.5" fill="{C_ACCENT}"/>
  <g stroke="{C_ACCENT}" stroke-width="1.5" stroke-linecap="round">
    <line x1="130" y1="78" x2="130" y2="74"/>
    <line x1="130" y1="112" x2="130" y2="116"/>
    <line x1="113" y1="95" x2="109" y2="95"/>
    <line x1="147" y1="95" x2="151" y2="95"/>
  </g>
  <!-- flow arrows between gears -->
  <path d="M105 55 Q115 50 120 70" stroke="{C_DARK}" stroke-width="1.5" fill="none" stroke-dasharray="3,3"/>
  <text x="100" y="133" text-anchor="middle" font-size="9" fill="{C_DARK}" font-family="sans-serif">讓系統自動運轉</text>
''')

# ── Chapter 8: 健康 / 心＋身體 ──
# Heart and body silhouette
def ch08():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- person silhouette (simple figure) -->
  <!-- head -->
  <circle cx="80" cy="48" r="12" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="2"/>
  <!-- body -->
  <line x1="80" y1="60" x2="80" y2="95" stroke="{C_PRIMARY}" stroke-width="2.5" stroke-linecap="round"/>
  <!-- arms -->
  <line x1="65" y1="70" x2="95" y2="70" stroke="{C_PRIMARY}" stroke-width="2" stroke-linecap="round"/>
  <!-- legs -->
  <line x1="80" y1="95" x2="65" y2="115" stroke="{C_PRIMARY}" stroke-width="2" stroke-linecap="round"/>
  <line x1="80" y1="95" x2="95" y2="115" stroke="{C_PRIMARY}" stroke-width="2" stroke-linecap="round"/>
  <!-- heart on chest -->
  <path d="M80 72 Q72 65 68 70 Q64 76 80 85 Q96 76 92 70 Q88 65 80 72" fill="{C_ACCENT}" stroke="{C_PRIMARY}" stroke-width="1.2"/>
  <!-- microphone (voice care) -->
  <rect x="125" y="35" width="6" height="20" rx="3" fill="{C_GRAY}" stroke="{C_DARK}" stroke-width="1"/>
  <circle cx="128" cy="33" r="8" fill="none" stroke="{C_ACCENT}" stroke-width="1.5"/>
  <!-- small waves -->
  <path d="M133 28 Q138 25 138 33" stroke="{C_ACCENT}" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M136 24 Q142 20 142 33" stroke="{C_ACCENT}" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <text x="100" y="133" text-anchor="middle" font-size="9" fill="{C_DARK}" font-family="sans-serif">保留教學的體力</text>
''')

# ── Chapter 9: AI / 機器人 ──
# Robot head
def ch09():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- robot head -->
  <rect x="70" y="40" width="60" height="50" rx="8" fill="white" stroke="{C_PRIMARY}" stroke-width="2.5"/>
  <!-- antenna -->
  <line x1="100" y1="40" x2="100" y2="25" stroke="{C_ACCENT}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="100" cy="22" r="4" fill="{C_LIGHT}" stroke="{C_ACCENT}" stroke-width="1.5"/>
  <!-- eyes -->
  <circle cx="85" cy="60" r="6" fill="{C_ACCENT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <circle cx="115" cy="60" r="6" fill="{C_ACCENT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <circle cx="85" cy="60" r="2.5" fill="white"/>
  <circle cx="115" cy="60" r="2.5" fill="white"/>
  <!-- mouth -->
  <rect x="85" y="74" width="30" height="6" rx="3" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1"/>
  <!-- ears -->
  <rect x="62" y="52" width="8" height="16" rx="3" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1.5"/>
  <rect x="130" y="52" width="8" height="16" rx="3" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1.5"/>
  <!-- speech bubble -->
  <path d="M140 35 Q160 25 155 40 Q170 35 155 50" fill="white" stroke="{C_ACCENT}" stroke-width="1.5"/>
  <text x="155" y="42" text-anchor="middle" font-size="8" fill="{C_DARK}" font-family="sans-serif">AI</text>
  <!-- label -->
  <text x="100" y="118" text-anchor="middle" font-size="9" fill="{C_DARK}" font-family="sans-serif">你的免費助教</text>
  <!-- small light beams -->
  <line x1="80" y1="32" x2="85" y2="25" stroke="{C_ACCENT}" stroke-width="1" opacity="0.6"/>
  <line x1="100" y1="30" x2="100" y2="18" stroke="{C_ACCENT}" stroke-width="1" opacity="0.6"/>
  <line x1="120" y1="32" x2="115" y2="25" stroke="{C_ACCENT}" stroke-width="1" opacity="0.6"/>
''')

# ── Chapter 10: 平衡 / 天平 ──
# Balance scale
def ch10():
    return _svg(200, 140, f'''
  <rect width="200" height="140" fill="{C_BG}" rx="8"/>
  <!-- base -->
  <polygon points="85,120 115,120 110,108 90,108" fill="{C_DARK}" stroke="#1a2a40" stroke-width="1"/>
  <!-- pillar -->
  <rect x="96" y="45" width="8" height="63" rx="2" fill="{C_DARK}"/>
  <!-- beam -->
  <line x1="45" y1="48" x2="155" y2="48" stroke="{C_PRIMARY}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="100" cy="48" r="6" fill="{C_ACCENT}" stroke="{C_PRIMARY}" stroke-width="1.5"/>
  <!-- left pan (school) -->
  <path d="M45 48 L30 110" stroke="{C_PRIMARY}" stroke-width="2"/>
  <path d="M15 118 Q30 123 45 118 L45 115 Q30 120 15 115 Z" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1.5"/>
  <text x="30" y="107" text-anchor="middle" font-size="8" fill="{C_DARK}" font-family="sans-serif">學校</text>
  <!-- right pan (one-person) -->
  <path d="M155 48 L170 110" stroke="{C_PRIMARY}" stroke-width="2"/>
  <path d="M155 118 Q170 123 185 118 L185 115 Q170 120 155 115 Z" fill="{C_LIGHT}" stroke="{C_PRIMARY}" stroke-width="1.5"/>
  <text x="170" y="107" text-anchor="middle" font-size="8" fill="{C_DARK}" font-family="sans-serif">一人</text>
  <!-- balanced -->
  <text x="100" y="138" text-anchor="middle" font-size="9" fill="{C_DARK}" font-family="sans-serif">平衡共存的智慧</text>
''')


CHAPTER_ILLUSTRATIONS = [
    ch01, ch02, ch03, ch04, ch05,
    ch06, ch07, ch08, ch09, ch10,
]

def get_illustration(ch_num):
    """Return SVG string for chapter number (1-indexed)."""
    if 1 <= ch_num <= len(CHAPTER_ILLUSTRATIONS):
        return CHAPTER_ILLUSTRATIONS[ch_num - 1]()
    return ""
