# DTPS 設備 ➜ 交換器 ➜ Port 對照表

> 產生日期：2026-08-14
> 來源：`dtps_inventory.csv`（FDB 跨交換器學習解析，實體接線埠）

## 🟦 Aruba 2930F-1
- Port 1｜VM-134 (134)、VMware ESXi (7)
- Port 12｜5年級AP (142)、不明-123 (125)
- Port 13｜新多元newAP (139)
- Port 14｜舊多元AP (140)
- Port 15｜會計室AP-142 (130)
- Port 3｜SMAA10-11301 (154)
- Port 4｜ACCOUNT (102)
- Port 5｜Brother印表機-2 (151)
- Port 6｜AP-105 (152)
- 本體｜Aruba 2930F-1 (246)

## 🟦 Aruba 2930F-2
- Port 10｜PAPER101 標籤列印站 (20)
- Port 17｜FortiAP-108 (135)
- Port 18｜資源班AP (122)
- Port 19｜3年級AP (141)
- Port 5｜大辦公室AP (145)
- Port 7｜SMAA10-11203 (133)、SMAA10-11204 (107)
- Port 9｜Konica C224e-2 (98)、Reco儀器設備 (200)
- 本體｜Aruba 2930F-2 (247)

## 🟦 Aruba 2930F-3
- Port 11｜FUJIFILM C325dw (240)
- Port 12｜Brother印表機 (138)
- Port 13｜A1大辦公室AP (147)
- Port 15｜4年級AP (132)
- Port 16｜資源班教室AP (136)
- 本體｜Aruba 2930F-3 (248)

## 🟦 Aruba 2930F-4
- Port 1｜IPCam-31 (31)
- Port 10｜BXB廣播主機 (153)
- Port 11｜ASUS-Win主機 (106)
- Port 12｜3年級AP (124)
- Port 18｜Konica C224e-3 (99)
- Port 2｜IPCam-32 (32)
- Port 20｜Axis攝影機-1 (123)
- Port 6｜VMware-VM (111)
- 本體｜Aruba 2930F-4 (251)

## 🟩 Cisco Catalyst 9K
- Bluetooth0/4｜RPi-21 (21)
- Gi0/0｜Ruckus-ZoneDirector (30)
- Gi1/0/4｜DS925+ (127)、MSI設備-131 (131)
- Gi1/0/7｜SMAA10-Win130 (104)
- unrouted VLAN 1003｜Konica C224e-1 (97)
- 本體｜Cisco Catalyst (252)

## 🟨 CX8100-核心
- 1/1/29｜FortiGate-500E (253)、w2 RackStation (6)
- 1/1/47｜PA-1420 (254)
- 1/1/48｜PA-1420-介面2 (250)
- 1/1/5｜FS RackStation (5)

## 🟪 DGS-1510（D-Link）
- Port 12｜未知-150 (150)
- Port 24｜SMAA10_GUARD (149)、警衛室AP (155)
- Port 5｜MOXA NPort 5210 (17)
- 本體｜DGS-1510 (249)

---
## 備註
- CSV 共 80 筆已填好 Switch+Port；因 FDB 跨交換器學習，多數實體埠已正確歸位
- 「(僅見於上聯)」的設備（如 1年級離線AP）暫無下聯直連資訊，之後可再追
