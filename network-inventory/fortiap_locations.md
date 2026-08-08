# DTPS FortiAP 位置對照表

來源：FortiGate 管理介面（Borsheng 提供, 2026-08-08 14:15）
說明：IP 為 DHCP（動態），對齊須以**交換器+埠**為錨點（IP/MAC 會漂移）
交換器代號：A-246=Aruba 2930F-A(.246) / B-247=Aruba 2930F-B(.247) / C-248=Aruba 2930F-C(.248)

| AP名稱 | 型號/FW | 連線埠 | 狀態 | 位置 | SSID群組 |
|---|---|---|---|---|---|
| FAP431F-DTPS | FP431F-v7.0-build0034 | 2930F-A-246 :15 | 上線 | 幼兒園辦公室 | lan_sw |
| FAP431F-DTPS | FP431F-v7.0-build0034 | 2930F-C-248 :16 | 上線 | 資源班教室 | lan_sw |
| FAP431F-DTPS | FP431F-v7.0-build0034 | 2930F-A-246 :12 | 上線 | 5年級 | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-B-247 :13 | **離線** | 1年級 | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-C-248 :14 | 上線 | 圖書館 | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-B-247 :5 | 上線 | 自然教室 | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-A-246 :13 | 上線 | 新多元new | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-A-246 :14 | 上線 | 舊多元 | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-B-247 :19 | 上線 | 3年級 | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-C-248 :15 | 上線 | 4年級 | lan_sw |
| PU431_110 | PU431F-v6.2-build0220 | 2930F-A-246 :16 | 上線 | 2年級 | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-C-248 :13 | 上線 | A1大辦公室 | lan_sw |
| PU431_110 (已覆蓋) | PU431F-v6.2-build0237 | 2930F-B-247 :16 | 上線 | A2校長室 | lan_sw |
| PU431_110 | PU431F-v6.2-build0237 | 2930F-A-246 :17 | 上線 | 6年級 | lan_sw |
| PU431_110 | PU431F-v7.0-build0146 | 2930F-B-247 :18 | (提取資訊) | ?(未標位置) | lan_sw |

## 交換器對應
- Aruba 2930F-A = 192.60.1.246 (Aruba 2930F-1)
- Aruba 2930F-B = 192.60.1.247 (Aruba 2930F-2)
- Aruba 2930F-C = 192.60.1.248 (Aruba 2930F-3)

## 備註
- 15 台 FortiAP 全部連到 3 台 Aruba 2930F-PoE 交換器（.246/.247/.248）
- 1年級 AP 目前離線
- SSID 群組：lan_sw（教室區）
