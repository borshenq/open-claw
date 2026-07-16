#!/usr/bin/env python3
"""
🌐 Network Watch - 網路埠口異動自動監控工具
=============================================
功能：
  1. 定時掃描指定網段的埠口狀態
  2. 與上次掃描結果比對，找出異動
  3. 透過 Telegram 通知異動
  4. 記錄異動日誌

使用方式：
  python watcher.py              # 執行一次掃描
  python watcher.py --force      # 強制重新掃描（忽略冷卻時間）

排程建議（crontab -e）：
  0 */4 * * * cd /path/network_watch && python watcher.py
"""

import os
import sys
import json
import subprocess
import xml.etree.ElementTree as ET
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import yaml

# ─── 路徑設定 ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.yaml"
STATE_DIR = BASE_DIR / "state"
LOGS_DIR = BASE_DIR / "logs"
LAST_SCAN_FILE = STATE_DIR / "last_scan.json"

# 台灣時區
TZ = timezone(timedelta(hours=8))

# ─── 通用名稱對照 ─────────────────────────────────────────
PORT_NAMES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 139: "NetBIOS",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
    587: "SMTP", 993: "IMAPS", 995: "POP3S", 1433: "MSSQL",
    1521: "Oracle", 2049: "NFS", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 5901: "VNC-1", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 9090: "WebAdmin",
    27017: "MongoDB",
}


def load_config() -> dict:
    """載入設定檔"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging():
    """設定 logging"""
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def parse_ports(ports: List) -> List[int]:
    """解析埠口列表（支援單埠號與範圍）"""
    result = []
    for p in ports:
        p_str = str(p)
        if "-" in p_str:
            parts = p_str.split("-")
            if len(parts) == 2:
                result.extend(range(int(parts[0]), int(parts[1]) + 1))
        else:
            result.append(int(p_str))
    return sorted(set(result))


def nmap_scan(target: str, ports: List[int], timing: str) -> Optional[str]:
    """
    對指定 target 執行 nmap 掃描
    回傳 XML 格式的結果字串
    """
    port_str = ",".join(str(p) for p in ports)
    cmd = [
        "nmap",
        "-sT",           # TCP Connect 掃描（不需 root）
        "-n",            # 不做 DNS 反解
        f"-{timing}",    # 速度模板
        "--open",        # 只顯示開放的埠口
        "-oX", "-",      # 輸出 XML 到 stdout
        "-p", port_str,
        "--host-timeout", "30s",
        target,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 單一網段最長 5 分鐘
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        logging.warning(f"⚠️ 掃描 {target} 逾時")
        return None
    except Exception as e:
        logging.error(f"❌ nmap 執行錯誤: {e}")
        return None


def parse_nmap_xml(xml_str: str) -> Dict[str, List[int]]:
    """
    解析 nmap XML 結果
    回傳 { ip: [port, port, ...] }
    """
    result = {}
    try:
        root = ET.fromstring(xml_str)
        for host in root.findall(".//host"):
            # 只處理存活的 host
            status = host.find("status")
            if status is None or status.get("state") != "up":
                continue

            # 取 IP 位址
            addr = host.find("address")
            if addr is None:
                continue
            ip = addr.get("addr")
            if not ip:
                continue

            # 收集開放埠口
            ports = []
            for port_elem in host.findall(".//port"):
                state = port_elem.find("state")
                if state is not None and state.get("state") == "open":
                    port_id = int(port_elem.get("portid", "0"))
                    if port_id > 0:
                        ports.append(port_id)

            if ports:
                result[ip] = sorted(ports)

    except ET.ParseError as e:
        logging.error(f"❌ 解析 nmap XML 失敗: {e}")

    return result


def scan(config: dict) -> Dict[str, List[int]]:
    """
    掃描所有設定的網段
    回傳合併後的 { ip: [port, ...] }
    """
    targets = config.get("targets", [])
    ports_def = config.get("ports", [80, 443])
    timing = config.get("scan", {}).get("timing_template", "T4")
    exclude = set(config.get("exclude", []))

    ports = parse_ports(ports_def)
    all_hosts = {}

    logging.info(f"🔍 開始掃描 {len(targets)} 個網段，共 {len(ports)} 個埠口")

    for target in targets:
        logging.info(f"  📡 掃描 {target} ...")
        xml_result = nmap_scan(target, ports, timing)
        if xml_result:
            hosts = parse_nmap_xml(xml_result)
            for ip, open_ports in hosts.items():
                if ip not in exclude:
                    if ip in all_hosts:
                        # 合併跨網段的同 IP 掃描結果
                        all_hosts[ip] = sorted(set(all_hosts[ip] + open_ports))
                    else:
                        all_hosts[ip] = open_ports
        else:
            logging.warning(f"  ⚠️ {target} 掃描失敗")

    logging.info(f"✅ 掃描完成，發現 {len(all_hosts)} 台主機")
    return all_hosts


def load_last_scan() -> Dict[str, List[int]]:
    """載入上次掃描結果"""
    if LAST_SCAN_FILE.exists():
        try:
            with open(LAST_SCAN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 防呆：回傳主機資料
                return data.get("hosts", data)
        except (json.JSONDecodeError, KeyError):
            logging.warning("⚠️ 上次掃描記錄格式異常，當作首次掃描")
    return {}


def save_scan(current: Dict[str, List[int]]):
    """儲存本次掃描結果"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "timestamp": datetime.now(TZ).isoformat(),
        "hosts": current,
    }
    with open(LAST_SCAN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def port_str(port_list: List[int]) -> str:
    """格式化埠口列表為可讀字串"""
    parts = []
    for p in port_list:
        name = PORT_NAMES.get(p, "")
        if name:
            parts.append(f"{p}({name})")
        else:
            parts.append(str(p))
    return ", ".join(parts)


def diff_scan(current: Dict[str, List[int]],
              last: Dict[str, List[int]]) -> List[str]:
    """
    比對兩次掃描結果的差異
    回傳通知訊息行列表（無變化則回傳空列表）
    """
    messages = []
    current_ips = set(current.keys())
    last_ips = set(last.keys())

    # 新主機上線
    new_ips = current_ips - last_ips
    for ip in sorted(new_ips):
        ports = current[ip]
        if ports:
            messages.append(f"  ➕ **{ip}** 上線，開放埠口：{port_str(ports)}")
        else:
            messages.append(f"  ➕ **{ip}** 上線（無開放埠口）")

    # 主機離線
    gone_ips = last_ips - current_ips
    for ip in sorted(gone_ips):
        ports = last[ip]
        if ports:
            messages.append(f"  ➖ **{ip}** 離線（曾開放：{port_str(ports)}）")
        else:
            messages.append(f"  ➖ **{ip}** 離線")

    # 埠口異動（同一台主機）
    common_ips = current_ips & last_ips
    for ip in sorted(common_ips):
        cur_ports = set(current[ip])
        last_ports = set(last[ip])

        new_ports = cur_ports - last_ports
        closed_ports = last_ports - cur_ports

        if new_ports:
            messages.append(
                f"  ⬆️ **{ip}** 新增埠口：{port_str(sorted(new_ports))}"
            )
        if closed_ports:
            messages.append(
                f"  ⬇️ **{ip}** 關閉埠口：{port_str(sorted(closed_ports))}"
            )

    return messages


def send_telegram_notification(messages: list, config: dict):
    """
    透過 OpenClaw 的 message tool 或 Telegram 格式輸出
    """
    now = datetime.now(TZ)
    weekday_cn = ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
    time_str = now.strftime(f"%Y-%m-%d（{weekday_cn}）%H:%M")

    lines = [
        "📡 **網路異動偵測**",
        f"⏰ 時間：{time_str}",
        "───",
        *messages,
        "───",
        "🌐 Network Watch",
    ]

    text = "\n".join(lines)

    # 用檔案輸出，讓使用者透過 cron 可以 pipe 到 telegram 或訊息系統
    log_file = LOGS_DIR / f"alerts_{now.strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{now.isoformat()}]\n{text}\n\n")

    # 同時輸出到 stdout（cron 會寄信或用來 pipe）
    print("\n" + text)


def clean_old_logs(days: int):
    """清理過期的日誌檔"""
    now = datetime.now().timestamp()
    for f in LOGS_DIR.iterdir():
        if f.is_file() and f.suffix in (".log", ".jsonl"):
            age_seconds = now - f.stat().st_mtime
            if age_seconds > days * 86400:
                f.unlink()
                logging.info(f"🧹 清理過期日誌：{f.name}")


def main():
    parser = argparse.ArgumentParser(
        description="🌐 Network Watch - 網路埠口異動自動監控"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="強制掃描（不檢查冷卻時間）",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="安靜模式（無變化不輸出）",
    )
    args = parser.parse_args()

    setup_logging()
    config = load_config()

    # 清掃舊日誌
    clean_old_logs(config.get("log_retention_days", 30))

    # 掃描
    current_scan = scan(config)

    # 載入上次結果並比對
    last_scan = load_last_scan()
    messages = diff_scan(current_scan, last_scan)

    # 儲存本次結果（無論有無變化）
    save_scan(current_scan)

    # 輸出結果
    if messages:
        send_telegram_notification(messages, config)
        logging.info(f"📢 發現 {len(messages)} 項異動，已通知")
    else:
        if not args.quiet:
            now = datetime.now(TZ)
            weekday_cn = ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
            print(
                f"✅ {now.strftime(f'%Y-%m-%d（{weekday_cn}）%H:%M')} "
                f"掃描完成，無異動（{len(current_scan)} 台主機）"
            )


if __name__ == "__main__":
    main()
