#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 7 台交換器 FDB → 解析 port 名稱 → 與 ARP+庫存比對，產出完整設備→交換器→port 對照表"""
import subprocess, re, sys, csv

# 交換器清單: (hostname, IP, community)
SWITCHES = [
    ('CX8100-核心', '192.60.1.245', 'SnmpPublic@TPC'),
    ('2930F-1',     '192.60.1.246', 'SnmpPublic@TPC'),
    ('2930F-2',     '192.60.1.247', 'SnmpPublic@TPC'),
    ('2930F-3',     '192.60.1.248', 'SnmpPublic@TPC'),
    ('2930F-4',     '192.60.1.251', 'SnmpPublic@TPC'),
    ('Cisco-9K',    '192.60.1.252', 'SnmpPublic@TPC'),
    ('DGS-1510',    '192.60.1.249', 'public'),
]

def snmpwalk(host, community, oid, timeout=15):
    """執行 snmpwalk 回傳 (oid_suffix, value) 列表"""
    try:
        out = subprocess.run(
            ['snmpwalk', '-v2c', '-c', community, '-On', host, oid],
            capture_output=True, text=True, timeout=timeout
        ).stdout
    except Exception as e:
        return []
    results = []
    for line in out.splitlines():
        line = line.strip()
        if not line: continue
        # 格式: .iso...OID = TYPE: VALUE
        m = re.match(r'^(.*?)\s*=\s*(\w+):\s*(.*)$', line)
        if m:
            oid_part, typ, val = m.group(1), m.group(2), m.group(3)
            # 取 OID 末段
            oid_suffix = re.sub(r'^.*\.(\d+(?:\.\d+)*)$', r'\1', oid_part)
            results.append((oid_part, typ, val.strip()))
    return results

def parse_mac_from_oid(oid_suffix):
    """FDB OID: ...1.2.<mac各段>  → MAC 字串"""
    nums = oid_suffix.split('.')
    # 最後 6 個數字是 MAC
    macparts = nums[-6:]
    return ':'.join(f"{int(x):02X}" for x in macparts)

def normalize_mac(mac):
    """統一 MAC 格式為 AA:BB:CC:DD:EE:FF 大寫"""
    return ':'.join(f"{int(x,16):02X}" for x in re.split(r'[:.\-]', mac.strip().upper())).upper() if mac else ''

def main():
    # === 1. 抓所有交換器 FDB + port 名稱 ===
    fdb_map = {}  # (switch_name) -> {mac: port_name}
    port_name_map = {}  # (switch_name) -> {index: port_name}
    
    for sw_name, sw_ip, comm in SWITCHES:
        # port index → 名稱 (ifName)
        pn = {}
        for oid, typ, val in snmpwalk(sw_ip, comm, '1.3.6.1.2.1.2.2.1.2'):
            idx = oid.split('.')[-1]
            val = val.strip('"')
            if val:  # 只要實際介面 (1/1/x)
                pn[idx] = val
        port_name_map[sw_name] = pn
        
        # FDB: MAC → port index
        fdb = {}
        for oid, typ, val in snmpwalk(sw_ip, comm, '1.3.6.1.2.1.17.4.3.1.2'):
            mac = parse_mac_from_oid(oid)
            fdb[mac] = val  # port index
        fdb_map[sw_name] = fdb
        print(f"✅ {sw_name} ({sw_ip}): FDB {len(fdb)} 筆, port名稱 {len(pn)} 個")

    # === 2. 抓 ARP (IP→MAC) ===
    arp = {}
    try:
        out = subprocess.run(['ip','neigh','show'], capture_output=True, text=True).stdout
        for line in out.splitlines():
            m = re.match(r'(\d+\.\d+\.\d+\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)\s', line)
            if m and m.group(1).startswith('192.60.1.'):
                arp[m.group(1)] = normalize_mac(m.group(2))
    except: pass
    print(f"✅ ARP: {len(arp)} 筆")

    # === 3. 讀庫存 ===
    inv = {}
    try:
        with open('dtps_inventory.csv', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                for k in r: r[k] = r[k] if r[k] else ''
                ip = r['IP']
                inv[ip] = r
    except Exception as e:
        print(f"庫存讀取錯誤: {e}")

    # === 4. 建立 MAC→設備 反向索引 (從庫存+ARP) ===
    mac_to_ip = {}
    for ip, r in inv.items():
        if r.get('MAC'):
            mac_to_ip.setdefault(normalize_mac(r['MAC']), []).append(ip)

    # === 5. 產生對照表 ===
    print("\n" + "="*110)
    print(f"{'設備名稱':<16}{'IP':<16}{'MAC':<20}{'交換器':<14}{'Port':<10}{'類型':<10}位置")
    print("="*110)
    
    rows = []
    seen_mac = set()
    for sw_name, fdb in fdb_map.items():
        port_n = port_name_map[sw_name]
        for mac, port_idx in fdb.items():
            port_name = port_n.get(port_idx, f"idx{port_idx}")
            # 找這顆 MAC 對應的 IP (用 ARP 或庫存)
            ip = None
            if mac in arp.values():
                ip = next((k for k,v in arp.items() if v==mac), None)
            if not ip and mac in mac_to_ip:
                ip = mac_to_ip[mac][0]
            # 名稱
            name = ''
            typ = ''
            loc = ''
            if ip and ip in inv:
                name = inv[ip]['Name']
                typ = inv[ip]['Type']
                loc = inv[ip]['Location']
            elif mac in mac_to_ip:
                ip = mac_to_ip[mac][0]
                name = inv[ip]['Name'] if ip in inv else ''
                typ = inv[ip]['Type'] if ip in inv else ''
                loc = inv[ip]['Location'] if ip in inv else ''
            elif not ip:
                # 查所有庫存 MAC 相符者
                pass
            rows.append((sw_name, mac, port_name, ip, name, typ, loc))
    
    # 輸出：有 IP 的優先，然後依交換器/port 排
    rows.sort(key=lambda x: (0 if x[3] else 1, x[0], x[2]))
    for sw, mac, port, ip, name, typ, loc in rows:
        disp_ip = ip or '-'
        disp_name = name or '(未辨識)'
        disp_typ = typ or ''
        disp_loc = loc or ''
        print(f"{disp_name:<16}{disp_ip:<16}{mac:<20}{sw:<14}{port:<10}{disp_typ:<10}{disp_loc}")
        seen_mac.add(mac)
    
    print("="*110)
    print(f"總共 {len(rows)} 筆 FDB 對應")

if __name__ == '__main__':
    main()
