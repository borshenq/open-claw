# 🌐 大屯國小完整網路拓撲

最後更新: 2026-07-14 09:58

## 🔌 交換器 Port 對接關係（LLDP 實測）

> 2026-07-14 透過 SNMP LLDP + MAC table 交叉比對

```
FortiGate (.254)
  │ port x1  ⇢ Aruba 8100 (.245) 1/1/29
  │ port x2  ⇢ Aruba 8100 (.245) 1/1/31
  │
Aruba CX8100-48F (.245) ← 核心交換器
  │ port 1/1/21  ⇢ Aruba 2930F-A (.246) — uplink (port 27)
  │ port 1/1/23  ⇢ Aruba 2930F-B (.247) — uplink (port 28)
  │ port 1/1/25  ⇢ Aruba 2930F-C (.248) — uplink (port 25)
  │ port 1/1/27  ⇢ Cisco Catalyst (.252) — uplink (Te1/1/4)
  │ port 1/1/29  ⇢ FortiGate (.254) x1
  │ port 1/1/31  ⇢ FortiGate (.254) x2
  │ port 1/1/?   ⇢ Aruba 2930F-110 (.251) — uplink → Aruba B (.247) port 26
  │
Aruba 2930F-A (.246) ← 樓層/機房1
  │ port 1  ⇢ 空（接 Broadcom 10G NIC 本地主機?）
  │ port 2  ⇢ 空（接 Broadcom 10G NIC 本地主機?）
  │ port 12 ⇢ FortiAP 資源班教室 (.122) — MAC: 74:78:A6:56:DD:E8
  │ port 13 ⇢ FortiAP 自然教室 (.149) — MAC: 00:0C:E6:BA:94:C2
  │ port 14 ⇢ FortiAP 新多元 (.145) — MAC: 00:0C:E6:BA:D4:42
  │ port 15 ⇢ FortiAP 會計室 (.169) — MAC: 74:78:A6:56:88:28
  │ port 16 ⇢ FortiAP 4年級 (.141) — MAC: 00:0C:E6:BC:5B:C2
  │ port 17 ⇢ FortiAP 校長室 (.140) — MAC: 84:39:8F:0D:3E:00
  │ port 27 ⇢ Aruba 8100 (.245) — uplink
  │
Aruba 2930F-B (.247) ← 樓層/機房2
  │ port 4  ⇢ ??? MAC: C8:7F:54:16:F2:EE
  │ port 5  ⇢ FortiAP 圖書館 (.143) — MAC: 00:0C:E6:BA:6A:82
  │ port 7  ⇢ ??? MAC: C8:7F:54:16:F2:C8
  │ port 10 ⇢ ??? MAC: 24:4B:FE:E8:52:0C（iPad?）
  │ port 16 ⇢ FortiAP 大辦公室 (.117) — MAC: 00:0C:E6:CA:D7:B2
  │ port 17 ⇢ FortiAP 廚房 (.148) — MAC: 90:6C:AC:5D:3C:38
  │ port 18 ⇢ FortiAP 3年級 (.137) — MAC: 00:0C:E6:BB:90:82
  │ port 19 ⇢ FortiAP 舊多元 (.102) — MAC: 00:0C:E6:BA:E8:42
  │ port 26 ⇢ Aruba 2930F-110 (.251) — downlink
  │ port 28 ⇢ Aruba 8100 (.245) — uplink
  │
Aruba 2930F-C (.248) ← 樓層/機房3
  │ port 13 ⇢ FortiAP 2年級 (.156) — MAC: 00:0C:E6:BC:78:82
  │ port 14 ⇢ FortiAP 1年級 (.170) — MAC: 00:0C:E6:BA:5C:02
  │ port 16 ⇢ FortiAP 幼兒園 (.146) — MAC: 74:78:A6:56:98:28
  │ port 25 ⇢ Aruba 8100 (.245) — uplink
  │
Cisco Catalyst (.252) "PoE-Cisco-252"
  │ port Gi1/0/4  ⇢ Aruba 8100 (.245) — uplink （遠端 port Te1/1/4）
  │ port Gi1/0/32 ⇢ Aruba 8100 (.245) 1/1/27（lacp? 第二條）
  │
D-Link DGS-1510-28XMP (.249) — 無 LLDP（可能管理 VLAN 不同）
  │ SNMP community: private / public 都通（主機名: "Switch"）
  │ MAC table 無法抓取（MIB 不支援 SNMP v2c 跨界）
  │
Aruba 2930F-110 (.251) ← 教室區交換器
  │ LLDP 僅見 Aruba 2930F-B (.247) port 26 為 uplink
  │ 其餘 port 5/6/10/11/12/20 連接未知終端（無 LLDP 回報）
  │ 推測為教室區有線網
```
機房位置: 大屯國小 (DTPS) — 臺北市北投區/貴子坑環教中心

## 發現方式
從 **OpenClaw VM (192.60.1.153)** 透過以下方式分析整個 192.60.1.0/24 網段：
- ✅ **SNMP v1 (community `SnmpPublic@TPC`)** — Aruba x5, Cisco x1, FortiGate x1
- ✅ **FortiGate CLI** — 透過 Borsheng 下指令查詢 CAPWAP AP 列表
- ✅ **ARP table** + nmap port scan + HTTP header + HTTPS 憑證
- ✅ **MAC Address Analysis Report** — Borsheng 提供的無線用戶端歷史資料

---

## 🏗️ 整體架構

```
Internet (163.21.221.124/25 WAN) → port8
   │
FortiGate / UniFi Gateway (.254)
  DTPS-FG5H0ETB19909536
  FortiOS 7.0.17 (GA.M) — 已 SNMP ✅
  CAPWAP 控制器 (5247)
  │
  ├── [SSID] staff ── 教職員無線網
  ├── [SSID] class ── 教室無線網
  ├── [SSID] st ───── 學生無線網
  ├── [SSID] iTaiwan ── 公眾無線
  ├── [SSID] TANetRoaming ── 漫遊
  ├── [SSID] eduroam ── 學術漫遊
  │
  ├── Aruba 8100 核心交換器 (.245) ─── SNMP ✅
  │     ├── Aruba 2930F PoE (.246) ─── SNMP ✅
  │     ├── Aruba 2930F PoE (.247) ─── SNMP ✅
  │     ├── Aruba 2930F PoE (.248) ─── SNMP ✅
  │     ├── Aruba 2930F PoE (.251) ─── SNMP ✅
  │     ├── Cisco Catalyst PoE (.252) ─── SNMP ✅
  │     ├── FortiAP × 16 (CAPWAP → .254:5247)
  │     ├── Synology NAS × 3
  │     └── 筆電/桌機/印表機群
  │
  ├── [VLAN 192.168.0.x] class SSID 用戶
  ├── [VLAN 192.168.50.x] st SSID 用戶
  ├── [VLAN 192.168.90.x] port7 區
  ├── [VLAN 192.168.190.x] N-Partner 區
  ├── [VLAN 192.168.10.x] ipcam 監控區
  └── FortiLink → 169.254.1.1
```

---

## 🖥️ 虛擬機架構

```
Synology DS925+ (192.60.1.127)
  AMD Ryzen V1500B / 8GB / 2TB SSD
  │
  └── VMM 虛擬機 → Ubuntu VM (openclaw, .153)
        ├── OpenClaw Gateway (Port 18789)
        ├── Redmine (Port 3000, puma)
        ├── FastAPI 網站 (Port 8000, uvicorn)
        ├── SearXNG (Docker, Port 8888)
        └── Tailscale (100.85.131.58)
```

---

## 🌐 核心設備 (SNMP 已通 ✅)

### FortiGate (UniFi / 網關路由器)
| 項目 | 內容 |
|:----|:------|
| IP | **192.60.1.254** |
| 主機名 | **DTPS-FG5H0ETB19909536** |
| 型號 | FortiGate (UniFi Controller 整合) |
| 序號 | FGT5H0ETB19909536 |
| FortiOS | v7.0.17,build0682,250113 (GA.M) |
| SNMP | ✅ **SnmpPublic@TPC** v1/v2c |
| 電源 | 雙備援 (PS1/PS2, 47 個硬體感測器) |
| 上線 | **49 天 10:19** 未重啟 |
| WAN | port8 → 163.21.221.124/25 |
| LAN | lan_sw → 192.60.1.254 (SNMP/HTTPS/SSH) |
| VLAN | 192.168.0.x(class), 192.168.50.x(st), 192.168.90.x(port7), 192.168.190.x(N-Partner), 192.168.10.x(ipcam) |
| CAPWAP AP | 16 台 FortiAP，全部連到 .254:5247 |
| 無線用戶 | 目前 **23 台**在線 |

### FortiAP 基地台 (16 台 via CAPWAP 管控)

| # | 位置 | IP | 型號 | 序號 | MAC | Profile |
|:-:|:----|:--:|:----|:-----|:---:|:-------|
| 1 | **A1 大辦公室** | .117 | FortiAP-431F | PU431FTH20016878 | 00:0C:E6:CA:D7:B0 | PU431_110 |
| 2 | **A2 校長室** | .140 | FortiAP-431F | PU431FTHxxxxx | 84:39:8F:0D:3E:00 | PU431_110 |
| 3 | **B1 警衛室** | .155 | FortiAP-221C | FP221C3Xxxxxx | 90:6C:AC:5D:3C:C8 | FAP221C-110 |
| 4 | **B2 廚房** | .148 | FortiAP-221C | FP221C3Xxxxxx | 90:6C:AC:5D:3C:38 | FAP221C-110 |
| 5 | **1年級** | .170 | FortiAP-431F | PU431FTH20006828 | 00:0C:E6:BA:5C:00 | PU431_110 |
| 6 | **2年級** | .156 | FortiAP-431F | PU431FTH20008990 | 00:0C:E6:BC:78:80 | PU431_110 |
| 7 | **3年級** | .137 | FortiAP-431F | PU431FTH20008062 | 00:0C:E6:BB:90:80 | PU431_110 |
| 8 | **4年級** | .141 | FortiAP-431F | PU431FTH20008875 | 00:0C:E6:BC:5B:C0 | PU431_110 |
| 9 | **5年級** | .142 | FortiAP-431F | PU431FTH20005630 | 00:0C:E6:B9:30:80 | FAP431F-DTPS |
| 10 | **自然教室** | .149 | FortiAP-431F | PU431FTH20007055 | 00:0C:E6:BA:94:C0 | PU431_110 |
| 11 | **資源班教室** | .122 | FortiAP-431F | PU431FTHxxxxx | 74:78:A6:56:DD:E8 | PU431_110 |
| 12 | **圖書館** | .143 | FortiAP-431F | PU431FTH20006886 | 00:0C:E6:BA:6A:80 | PU431_110 |
| 13 | **舊多元** | .102 | FortiAP-431F | PU431FTH20007389 | 00:0C:E6:BA:E8:40 | PU431_110 |
| 14 | **新多元new** | .145 | FortiAP-431F | PU431FTH20007309 | 00:0C:E6:BA:D4:40 | FAP431F-DTPS |
| 15 | **幼兒園辦公室** | .146 | FortiAP-431F | PU431FTHxxxxx | 74:78:A6:56:98:28 | PU431_110 |
| 16 | **會計室** | .169 | FortiAP-431F | PU431FTHxxxxx | 74:78:A6:56:88:28 | FAP431F-DTPS |

> ⚠️ FortiAP 韌體: **FortiAP OS 6.2 build 0237** — SNMP agent 無法獨立啟用
> ⚠️ CAPWAP 全數終止於 **.254:5247**（FortiGate 自身）
> ⚠️ 15x FortiAP-431F + 2x FortiAP-221C（教室命名對應大屯國小教室分佈）

### Aruba 8100 核心交換器 (.245)
| 項目 | 內容 |
|:----|:------|
| 型號 | Aruba 8100-48XF4C (R9W96A) |
| SNMP | ✅ sysLocation: "" |
| 規格 | 48x SFP+ （10G） + 4x QSFP28 (100G) |

### Aruba 2930F PoE+ 接入交換器 (×4)
| IP | 型號 | SNMP | 位置推測 |
|:--:|:----|:----:|:--------|
| .246 | JL263A 2930F-24G-PoE+-4SFP+-TAA | ✅ | 機房/樓層1 |
| .247 | JL263A 2930F-24G-PoE+-4SFP+-TAA | ✅ | 機房/樓層2 |
| .248 | JL263A 2930F-24G-PoE+-4SFP+-TAA | ✅ | 機房/樓層3 |
| .251 | JL255A 2930F-24G-PoE+-4SFP+ | ✅ | 教室區 |

### Cisco Catalyst (.252)
| 項目 | 內容 |
|:----|:------|
| 主機名 | **PoE-Cisco-252** |
| SNMP | ✅ |

---

## 🌐 SSID 與 VLAN 結構

| SSID | VLAN | IP 網段 | 用途 |
|:----|:----:|:--------|:----|
| staff | 無 | 192.60.1.x | 教職員（直接接內網） |
| class | 192.168.0.x | 192.168.0.0/24 | 教室平板、電腦 |
| st | 192.168.50.x | 192.168.50.0/24 | 學生手機 |
| iTaiwan | 10.168.201.x | 10.168.201.0/24 | iTaiwan 公眾 WiFi |
| TANetRoaming | 10.168.202.x | 10.168.202.0/24 | 教育漫遊 |
| eduroam | 10.168.203.x | 10.168.203.0/24 | 學術漫遊 |
| dtps_113 | VRF4 | — | 113 學年度專用 |
| 監控 | 192.168.10.x | 192.168.10.0/24 | IP Camera VLAN（ipcam 介面） |
| N-Partner | 192.168.190.x | 192.168.190.0/24 | 合作廠商網段 |

---

## 📱 無線用戶端分布（即時）

從 MAC Address Analysis Report 提取的**活躍在線用戶端**（最新資料）：

### 🏫 各處室/教室在線設備

| 位置 | 連接 AP | iPhone/iPad | Mac | Windows | Android/其他 |
|:----|:-------:|:-----------:|:---:|:-------:|:----------:|
| **A1 大辦公室** | .117 | 5 | 0 | 2 | 0 |
| **A2 校長室** | .140 | 3 | 0 | 0 | 0 |
| **B1 警衛室** | .155 | 1 | 0 | 0 | 0 |
| **B2 廚房** | .148 | 1 | 0 | 0 | 1 |
| **1年級** | .170 | 1 | 0 | 0 | 0 |
| **2年級** | .156 | 1 | 0 | 0 | 0 |
| **3年級** | .137 | 0 | 0 | 0 | 0 |
| **4年級** | .141 | **16** | 2 | 0 | 0 |
| **5年級** | .142 | **12** | 2 | 0 | 0 |
| **自然教室** | .149 | 1 | 0 | 0 | 0 |
| **資源班教室** | .122 | 2 | 0 | 1 | 0 |
| **圖書館** | .143 | **13+** | 0 | 0 | 0 |
| **舊多元** | .102 | 1 | 0 | 1 | 1 |
| **新多元new** | .145 | 4 | 0 | 0 | 0 |
| **幼兒園辦公室** | .146 | 1 | 0 | 0 | 0 |
| **會計室** | .169 | 1 | 0 | 0 | 0 |

### 在線用戶端 OS 分布
- 📱 **iOS/iPadOS**: 約 50+（包含 iPad A05~A35 教室平板群）
- 💻 **macOS**: 約 6（4年級教室 + 5年級教室各 2）
- 🖥️ **Windows**: 約 5（資源班教室、大辦公室）
- 🤖 **Android**: 約 2（廚房、舊多元）

### 學校 iPad 教室平板編號（圖書館區在線中）
A05, A08, A09, A15, A29, A33, A35, T00, T01, 110T-02, 以及多台未命名 iPad

---

## 🖨️ 印表機

| IP | 型號 | 備註 |
|:--:|:----|:----|
| .138 | Brother MFC-L2715DW | ✅ 在線 |
| .151 | Brother MFC-L2715DW | ✅ 在線 |
| .240 | FUJIFILM ApeosPrint C325 dw | 彩色雷射 ✅ |
| .97 | Konica Minolta BizHub C224e | ✅ |
| .98 | Konica Minolta BizHub C224e | ✅ |
| .99 | Konica Minolta BizHub C224e | ✅ |
| .17 | HP 網路列印 | ❌ 列印埠關 |
| .31 | HP 雷射 | ❌ 列印埠關 |
| .32 | HP 雷射 | ❌ 列印埠關 |

## 📹 監控設備

| IP | 廠牌 | 備註 |
|:--:|:----|:------|
| .125 | Axis 攝影機 | ✅ |
| .42 | Axis 攝影機 | ✅ |
| .167 | **GeoVision NVR** | 監控主機，14 埠，TeamViewer |

## 🔌 UPS 不斷電系統

| IP | 廠牌 | 備註 |
|:--:|:----|:------|
| .249 | **Delta 台達** UPS #5 | ⚠️ Telnet/HTTP only |

---

## 📋 SNMP Community 完整對照表

> ### 可用 Community 字串一覽
>
> | Community | 權限 | 使用設備 | 來源 |
> |:----------|:----:|:---------|:----|
> | **`SnmpPublic@TPC`** | Read | Aruba×6 + Cisco Catalyst + **FortiGate .254** | FortiGate conf edit 2 |
> | **`public`** | Read | D-Link .249, Brother .138/.151, OpenClaw .153, Fuji .240 | 設備預設 |
> | **`private`** | Read | **D-Link DGS-1510 .249**（比 public 完整） | 設備預設 |
> | **`internal`** | Read | **Brother 印表機 .138/.151** | FortiGate conf 出現 |
> | **`all`** ⚡ | Read+? | **僅限 .21 SNMP 管理站**存取 FortiGate .254 | FortiGate conf edit 1 |

### 各設備適用 Community

| 設備 | IP | SNMP | Community | MAC Table |
|:----|:--:|:----:|:---------|:---------:|
| **FortiGate 500E** | .254 | ✅ | SnmpPublic@TPC | 1 筆 |
| **Aruba CX8100-48F** | .245 | ✅ | SnmpPublic@TPC | 85 MACs |
| **Aruba 2930F-A** (JL263A) | .246 | ✅ | SnmpPublic@TPC | 88 MACs |
| **Aruba 2930F-B** (JL263A) | .247 | ✅ | SnmpPublic@TPC | 71 MACs |
| **Aruba 2930F-C** (JL263A) | .248 | ✅ | SnmpPublic@TPC | 68 MACs |
| **Aruba 2930F-110** (JL255A) | .251 | ✅ | SnmpPublic@TPC | 58 MACs |
| **Cisco Catalyst 9K** | .252 | ✅ | SnmpPublic@TPC | 59 MACs |
| **D-Link DGS-1510-28XMP** | .249 | ✅ | private > public | 59 MACs |
| **Brother 印表機** .138 | .138 | ✅ | internal / public | N/A |
| **Brother 印表機** .151 | .151 | ✅ | internal / public | N/A |
| **OpenClaw VM** | .153 | ✅ | public | N/A |
| **Fuji ApeosPrint .240** | .240 | ✅ | public | N/A |
| FortiAP ×16 | 各 IP | ❌ | 韌體不支援 | — |
| Delta UPS | .249 | ❌ | Telnet/HTTP only | — |
| 其他主機 (NAS/PC/VM) | 其餘 | ❌ | 未啟用 SNMP | — |

### 掃 Community 用過的指令

```bash
# 測試某設備的 SNMP 名稱
snmpget -v2c -c <COMMUNITY> <IP> 1.3.6.1.2.1.1.5.0

# 抓 MAC table
snmpwalk -v2c -c <COMMUNITY> <IP> 1.3.6.1.2.1.17.4.3.1.1

# 抓 Port 列表
snmpwalk -v2c -c <COMMUNITY> <IP> 1.3.6.1.2.1.2.2.1.2
```

### FortiGate conf 中的 SNMP 設定

```
config system snmp sysinfo
    set status enable
    set description "DTPS"
    set contact-info "admin@dtps"
    set location "Taipei"
end
config system snmp community
    edit 1
        set name "all"
        config hosts
            edit 1
                set ip 192.60.1.21 255.255.255.255
            next
        end
    next
    edit 2
        set name "SnmpPublic@TPC"
        config hosts
            edit 2
            next
            edit 1
                set ip 192.60.1.0 255.255.255.0
            next
        end
    next
end
```

> ⚠️ **Security Note**: `all` community 僅開放給 .21，推測為 SNMP 管理站主機
> ✅ **實測可用**: `SnmpPublic@TPC` 可完整讀取全部 7 台 Switch + FortiGate
> 💡 建議將所有非必要設備的 SNMP community 改為唯讀或關閉

### 已試過但無回應的 Community

`SNMP109_edu`, `SNMP_dtps`, `snmp`, `admin`, `switch`, `cisco`, `hp`,
`dell`, `netgear`, `synology`, `ubnt`, `unifi`, `aruba`, `SNMP`,
`read`, `write`, `readonly`, `readwrite`, `secret`, `default`,
`monitor`, `manager`, `trap`, `password`, `pass`

---

## 🔒 安全提醒

| 等級 | 問題 | 受影響主機 |
|:----:|:----|:----------|
| 🔴 | Telnet 未加密 | .246-.249, .251 |
| 🔴 | FTP 明文傳輸 | .6, .21, .30, .99, .107 |
| 🔴 | SMB 對外開放 | .99, .105, .111, .116, .120, .127, .152 |
| 🟡 | RDP 未鎖 IP | .107 (OpenClaw VM) |
| 🟡 | IRC (6666/6667) | .105 |
| 🟡 | MQTT (1883) | .32 (HP) |
| 🟡 | TeamViewer (5938) | .167 (GeoVision NVR) |
| 🟡 | 高埠全開 (24) | .188 (IoT 控制台?) |

---

## 📝 備註

- **DNS**: `dns.tp.edu.tw` — 臺北市教育局
- **Tailscale**: `tail93ddd3.ts.net` (VM: 100.85.131.58)
- **OpenClaw VM** IP 歷史: 曾為 `.107`，重開機後換為 `.153`（DHCP，MAC: 02:11:32:2a:ca:30）
- **完整掃描報告**: `network_scan_2026-06-17.md` (50 hosts)
- **環境**: 學校/環教中心機房，大屯國小（DTPS = 大屯國小）

## 2026-07-14 11:03 網路異動

### 🟢 新發現主機
- **192.60.1.142** — 開 22(ssh), 443(http)

### ⚠️ 埠口變動
- **192.60.1.107 (OpenClaw VM)** — 移除 21/tcp (FTP 關閉)
