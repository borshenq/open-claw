# 全域網路資產與算力盤點清冊

| 設備名稱 / 類型 | IP 位址 | 物理位置 / 功能備註 | 算力 / 關鍵服務 |
| :--- | :--- | :--- | :--- |
| **🚀 核心算力 PC (GPU)** | 192.60.1.110 | 算力中心 | **220 TPS** (qwen3.5:latest) |
| **🛡️ 數據中心 NAS (CPU)** | 192.60.1.107 | 算力備援 / 數據存儲 | (因記憶體不足，已移除算力功能) |
| **🗄️ Synology RackStation** | 192.60.1.6 | 核心存儲 / 監控中心 | FTP, SSH, SMB, RTSP (Webcam) |
| **🗄️ Synology NAS (DS925)** | 192.60.1.127 | 存儲中心 (Batch 2) | iSCSI, SMB, Port 5000 (Ready) |
| **🗄️ Synology DiskStation** | 192.60.1.153 | 存儲中心 (Batch 2) | AFP, SMB, Port 5000 (Ready) |
| **🖥️ VMware ESXi 伺服器** | 192.60.1.7 | 虛擬機主機 (dpts-srv) | ESXi 7.0.2 |
| **🌐 Ruckus ZoneDirector** | 192.60.1.30 | 無線網路控制器 | Wi-Fi AP 管理 |
| **📸 IP Camera (1)** | 192.60.1.31 | 網路攝影機 | DD-WRT, Live555 |
| **📸 IP Camera (2)** | 192.60.1.32 | 網路攝影機 | DD-WRT, Live555 |
| **🛡️ Fortinet 防火牆陣列** | 192.60.1.102, .140-.145, .149 | 網路安全與 VPN | FortiOS |
| **💻 Windows 工作站 (A)** | 192.60.1.103 | 辦公室工作站 | AnyDesk, IIS 10.0 |
| **💻 Windows 工作站 (B)** | 192.60.1.105 | 監控工作站 (Nagios) | AnyDesk |
| **💻 Windows 工作站 (C)** | 192.60.1.116 | 企業版工作站 | Win10 Enterprise |
| **💻 Windows 工作站 (D)** | 192.60.1.120 | 辦公室工作站 (Batch 2) | Win10 Enterprise |
| **💻 Windows 工作站 (E)** | 192.60.1.121 | 辦公室工作站 (Batch 2) | Win10 Enterprise |
| **🔍 Unbound DNS** | 192.60.1.122, .146 | 域名解析服務 | DNS (Batch 2) |
| **🖨️ Konica Minolta 367** | 192.60.1.97 | **輔導室** | 印表機 (IPP, JetDirect) |
| **🖨️ Konica Minolta C227** | 192.60.1.98 | **總務處** | 印表機 (IPP, JetDirect) |
| **🖨️ Konica Minolta C227** | 192.60.1.99 | **大辦公室** (第二台) | 印表機 (IPP, JetDirect) |
| **🖨️ Brother MFC-L2715DW** | 192.60.1.138 | **二年級** (第二台) | 印表機 |
| **🖨️ Brother MFC-L2715DW** | 192.60.1.151 | **會計室** | 印表機 |
| **🖨️ Brother MFC-L2715DW** | USB Direct | **校長室** (第三台) | 印表機 (USB直連) |
| **🖨️ Fuji ApeosPrint** | 192.60.1.240 | **幼兒園** | 印表機 |
| **🖨️ DocuPrint M375z** | 192.168.0.51 | **電腦教室** | 印表機 |

---
*最後更新日期：2026-04-03*
*數據來源：Flora 日常維護更新*
