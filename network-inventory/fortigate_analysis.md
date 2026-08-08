# FortiGate DTPS-FG5H0ETB19909536 組態分析

來源：FortiGate #show 完整組態（Borsheng 提供, 2026-08-08 14:25）

## 🔧 裝置
- 主機名: DTPS-FG5H0ETB19909536（alias/serial FG200D4615802385）
- Firmware: FG5H0E-7.0.17-FW-build0682（2025-01-13）
- VDOM: 停用（單一 root vdom）
- switch-controller: enable（內建交換器控制器，管理 FortiAP/FortiSwitch）

## 🔀 實體埠分組（switch-interface）
| 群組 | 成員埠 | 對應網段 |
|---|---|---|
| lan_sw | port1 x1 port2 port10 | 192.60.1.0/24（主網段/AP）|
| lan_sw_class | port3 port9 x2 port4 port5 | 192.168.0.0/24（class）|
| ipcam | port6 | 192.168.10.0/24（攝影機）|

## 🌐 介面網段
| 介面 | IP | 用途 |
|---|---|---|
| mgmt | 192.168.2.99/24 | 專屬管理埠 |
| port7 | 192.168.90.1/24 | — |
| port8 | 163.21.221.124/25 + IPv6 2001:288:127a:ffff::1/64 | 對外 TANet |
| port12 | 192.168.190.1/24 | alias N-Parnter |
| lan_sw | 192.60.1.253/24 + IPv6 | **主網段（我們盤點）** |
| lan_sw_class | 192.168.0.253/24 | alias class |
| ipcam | 192.168.10.254/24 | 攝影機網段 |
| fortilink | 169.254.1.1/24 | FortiLink Fabric |
| st | 192.168.50.254/24 | vap-switch, SSID st |
| class | (vap-switch) | SSID b |
| iTaiwan | 10.168.201.254/24 | vap-switch |
| TANetRoaming | 10.168.202.254/24 | vap-switch |
| eduroam | 10.168.203.254/24 | vap-switch |
| dtps_113 | vrf 4 (vap-switch) | SSID b |

## 📡 無線 SSID 網段（vap-switch, 對應 AP 群組）
- st = 192.168.50.0/24
- class / dtps_113 = SSID "b"（dtps_113 用 vrf 4 隔離）
- iTaiwan / TANetRoaming / eduroam = 10.168.201-203.0/24
- AP 清單的群組(class/dtps/st)對應此處

## 🔐 管理帳號（含 trusthost 白名單）
- admin / adminAAA / zerone / fortinet-tech-support: super_admin
- tpe: super_admin（trusthost 163.21/16, 61.220.72/24, 192.168.1/24, 59.124.82.62, 114.32.12.100）
- mertec: super_admin（trusthost 59.124.246.1, 192.168.2/24, 192.60.1/24）
- api: Readonly（trusthost 163.21.135/24）

## 📝 DNS
- 主 163.21.249.166 / 次 168.95.1.1
- IPv6 主 2001:288:1200::166 / 次 2001:288:1200::167

## 🔗 與庫存之關聯
- 本機 lan_sw = **192.60.1.253**（庫存 .253 FortiGate-500E ✅ 一致）
- ipcam 網段 192.168.10.0/24 與庫存 Axis 攝影機(.42/.125)可能相關（待確認是否在同一網段）
- SSID class/dtps_113 = "b"，對應 AP 清單 R2 群組
