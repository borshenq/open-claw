# 🌐 南港機房網路拓撲

最後更新: 2026-04-30

## 發現方式
從 OpenClaw VM (192.60.1.107, QEMU/KVM, Ubuntu 24.04) 在 Synology DS925+ 上，透過 ARP table + nmap + port scan + HTTP header 分析整個 192.60.1.0/24 網段。

> SNMP (community `public` / `SnmpPublic@TPC`) 從此 VM 無法連通，可能因 ACL 或 VMM 虛擬交換器隔離。

---

## 🖥️ 虛擬機架構

```
Synology DS925+ (192.60.1.127) — AMD Ryzen V1500B / 8GB / 2TB SSD
  └── VMM 虛擬機 → Ubuntu VM (openclaw, 192.60.1.107)
        ├── OpenClaw Gateway (Port 18789)
        ├── Redmine (Port 3000, puma)
        ├── FastAPI 網站 (Port 8000, uvicorn)
        ├── SearXNG (Docker, Port 8888)
        └── Tailscale (100.85.131.58)
```

---

## 🌐 網路拓撲

```
Internet
   │
   ▼
Ubiquiti UniFi Gateway (192.60.1.254)
   │
   ├── VMware ESXi 主機 (.7)  ← Zyxel MAC
   │     └── 可能跑其他 VM
   │
   ├── D-Link 接入交換器群 (00:0C:E6 系, 共 10 台)
   │     │
   │     ├── 辦公電腦 (Intel/ASUS MAC 群)
   │     ├── 印表機 (Brother, FUJIFILM, HP)
   │     ├── 網路攝影機 (Axis × 2)
   │     ├── 小米設備 (Xiaomi × 3)
   │     ├── Samsung 裝置 (×2)
   │     ├── Apple 裝置 (×1)
   │     ├── TP-Link AP/設備 (×1)
   │     └── Huawei 設備 (×1)
   │
   ├── 機房區
   │     ├── Synology RackStation FS (.5) — 全快閃？
   │     ├── Synology RackStation w2 (.6)
   │     ├── Cisco 交換器 (.200)
   │     ├── 台達 UPS 管理 ×5 (.245-.249)
   │     └── Siemon 佈線系統 (.97-.99)
   │
   └── (VLAN 隔離?) IoT/物聯網區
```

---

## 📋 完整裝置清單

### 🖥️ 伺服器 / NAS

| IP | MAC | 廠牌 | 推測型號 | 用途 |
|:--:|:---:|:----:|---------|------|
| .127 | 90:09:D0 | Synology | **DS925+** | 主 NAS，跑 VMM (OpenClaw VM) 及 DSM 服務 |
| .5 | 00:11:32* | Synology | **FS RackStation** | 全快閃機架式 NAS |
| .6 | 00:11:32* | Synology | **w2 RackStation** | 機架式 NAS（備份/儲存） |
| .7 | BC:97:E1 | Zyxel | **VMware ESXi** | 虛擬化主機 |
| .107 | (虛擬) | QEMU | **OpenClaw VM** | 我的 Ubuntu VM (on DS925+ VMM) |

\* MAC 透過 Zyxel 交換器轉發顯示

### 🌐 網路設備

| IP | MAC 前6 | 廠牌 | 推測型號 |
|:--:|:-------:|:----:|---------|
| .254 | 04:D5:90 | **Ubiquiti** | **UniFi Gateway / UDM-Pro** |
| .200 | 00:03:21 | **Cisco** | **Cisco 交換器** |
| .102 | 00:0C:E6 | **D-Link** | **DGS 系列交換器** |
| .117 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .137 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .141 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .142 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .143 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .145 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .149 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .156 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .170 | 00:0C:E6 | D-Link | DGS 系列交換器 |
| .97-99 | 00:20:6B | Siemon | 智慧佈線/PoE |
| .21 | DC:A6:32 | TP-Link | TP-Link AP/路由器 |

### 🖨️ 印表機

| IP | MAC | 型號 | 備註 |
|:--:|:---:|:----|------|
| .151 | B4:22:00:4F:C7:71 | **Brother MFC-L2715DW** | 黑白雷射多功能事務機 |
| .138 | B4:22:00:47:F0:46 | **Brother MFC-L2715DW** | 黑白雷射 (南港廠裡) |
| .240 | 1C:7D:22:62:0D:DC | **FUJIFILM ApeosPrint C325 dw** | 彩色雷射 |
| .17 | 00:90:E8:5D:2E:39 | **HP** | HP 網路列印介面 |

### 🔌 UPS 不斷電系統

| IP | MAC | 廠牌 | 備註 |
|:--:|:---:|:----|------|
| .245 | E8:1C:A5 | ASUS (管理卡) | Delta UPS (nginx redirect) |
| .246 | F8:60:F0 | **Delta** | 台達 UPS #1 (有 Web UI) |
| .247 | F8:60:F0 | **Delta** | 台達 UPS #2 |
| .248 | F8:60:F0 | **Delta** | 台達 UPS #3 |
| .249 | 40:9B:CD | **Delta** | 台達 UPS #4 |

### 📹 網路攝影機

| IP | MAC | 廠牌 | 備註 |
|:--:|:---:|:----|------|
| .125 | 00:18:1A | **Axis** | Axis 網路攝影機 (401 Unauthorized) |
| .42 | E0:10:7F | **Axis** | Axis 網路攝影機 |

### 💻 辦公電腦

| IP | MAC 前6 | 廠牌 | 備註 |
|:--:|:-------:|:----|------|
| .20 | 24:4B:FE | Intel | 辦公電腦 |
| .104 | FC:34:97 | Intel | 辦公電腦 |
| .105 | 90:6D:05 | Intel | 辦公電腦 (有 HTTP 80) |
| .129 | E8:9C:25 | Intel | 辦公電腦 |
| .134 | 24:4B:FE | Intel | 辦公電腦 |
| .135 | E8:9C:25 | Intel | 辦公電腦 |
| .136 | 04:D9:F5 | Intel | 辦公電腦 |
| .144 | A0:AD:9F | Intel | 辦公電腦 |
| .147 | FC:34:97 | Intel | 辦公電腦 |
| .148 | 90:6C:AC | Intel | 辦公電腦 |
| .150 | FC:34:97 | Intel | 辦公電腦 |
| .154 | A0:AD:9F | Intel | 辦公電腦 |
| .155 | 90:6C:AC | Intel | 辦公電腦 |
| .116 | C8:7F:54 | ASUS | 辦公電腦 |
| .118 | C8:7F:54 | ASUS | 辦公電腦 |
| .120 | C8:7F:54 | ASUS | 辦公電腦 |
| .121 | C8:7F:54 | ASUS | 辦公電腦 |
| .188 | F4:ED:5F | ASUS | 辦公裝置 |

### 📱 行動/IoT 裝置

| IP | MAC 前6 | 廠牌 | 推測 |
|:--:|:-------:|:----|------|
| .122 | 74:78:A6 | **Xiaomi** | 小米智慧設備 #1 |
| .146 | 74:78:A6 | **Xiaomi** | 小米智慧設備 #2 |
| .169 | 74:78:A6 | **Xiaomi** | 小米智慧設備 #3 |
| .251 | B8:D4:E7 | **Samsung** | 三星裝置 #1 |
| .252 | D0:09:C8 | **Samsung** | 三星裝置 #2 |
| .158 | 70:4D:7B | **Apple** | Apple 裝置 |
| .131 | 04:7C:16 | **Huawei** | 華為裝置 |

### ❓ 不明裝置

| IP | MAC 前6 | 廠牌 | 備註 |
|:--:|:-------:|:----|------|
| .161 | CE:61:D4 | 不明 | 私有 MAC |
| .167 | 10:7C:61 | Shenzhen | 有 Web 登入頁面 |
| .139 | F4:4D:30 | Intelbras | 巴西廠牌網路設備 |
| .140 | 84:39:8F | Fiberhome | 中國光通訊設備 |
| .30 | 6C:AA:B3 | ASUS | 不明裝置 |
| .31 | 00:0F:0D | HP | HP 裝置 |
| .32 | 00:0F:0D | HP | HP 裝置 |

---

## 🧩 注意事項

- **SNMP 不通**: community `public` / `SnmpPublic@TPC` 從此 VM 無法連線（可能 ACL 限制或 VMM 虛擬交換器隔離）
- **MAC 廠商推測**: 部分 MAC 可能因交換器轉發而非真實裝置 MAC
- **推測為主**: Port 對照為 IP 分群 + MAC 分析推測，非實際交換器設定
- **DNS**: `dns.tp.edu.tw` — 臺北市教育局 DNS
- **Tailscale**: `tail93ddd3.ts.net`
- **環境**: 學校/環教中心機房（明德國中、貴子坑環教相關）
