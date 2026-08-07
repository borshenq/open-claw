#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核心 CX8100 直連埠對照表：MAC → port → (ARP/庫存) IP+名稱"""
import subprocess, re, csv

CORE = '192.60.1.245'
COMM = 'SnmpPublic@TPC'

def snmpwalk_all(host, community, oid, timeout=20):
    try:
        out = subprocess.run(['snmpwalk','-v2c','-c',community,'-On',host,oid],
                             capture_output=True, text=True, timeout=timeout).stdout
    except Exception:
        return []
    return [l.strip() for l in out.splitlines() if l.strip()]

def snmpwalk_core(port_idx):
    """抓核心 FDB,回傳 {mac: port_index}"""
    fdb = {}
    for line in snmpwalk_all(CORE, COMM, '1.3.6.1.2.1.17.4.3.1.2'):
        m = re.match(r'^.*\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+) =.*INTEGER:\s*(\d+)$', line)
        if m:
            mac = ':'.join(f"{int(x):02X}" for x in m.groups()[:6])
            port = m.group(7)
            fdb[mac] = port
    return fdb

# port index -> 名稱
port_name = {}
for line in snmpwalk_all(CORE, COMM, '1.3.6.1.2.1.2.2.1.2'):
    m = re.match(r'^.*\.(\d+) = STRING:\s*"?(1/1/\d+)', line)
    if m:
        port_name[m.group(1)] = m.group(2)

# FDB
fdb = snmpwalk_core(CORE)
print(f"核心CX8100 FDB: {len(fdb)} 筆, port名稱: {len(port_name)} 個")

# ARP
arp = {}
try:
    out = subprocess.run(['ip','neigh','show'],capture_output=True,text=True).stdout
    for line in out.splitlines():
        m = re.match(r'(192\.60\.1\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)', line)
        if m: arp[normalize(m.group(2))] = m.group(1)
except: pass

def normalize(m):
    return ':'.join(f"{int(x,16):02X}" for x in re.split(r'[:.\-]',m.strip().upper())).upper()

# 庫存
inv = {}
try:
    with open('dtps_inventory.csv',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            inv[r['IP']] = r
except Exception as e:
    print("庫存讀取錯誤:", e)

# 組反向: MAC -> (ip,name,type,loc)
mac_info = {}
for ip,r in inv.items():
    if r.get('MAC'):
        mac_info.setdefault(normalize(r['MAC']), (ip, r['Name'], r['Type'], r['Location']))
# 也用 arp
for mac,ip in arp.items():
    if mac not in mac_info:
        n = inv.get(ip,{})
        mac_info[mac] = (ip, n.get('Name',''), n.get('Type',''), n.get('Location',''))

# 依 port index 排序輸出
print("\n" + "="*100)
print(f"{'核心8100埠':<12}{'MAC':<20}{'IP':<16}{'設備名稱':<20}{'類型':<10}位置")
print("="*100)
lines = []
for mac, pidx in fdb.items():
    pname = port_name.get(pidx, f"idx{pidx}")
    ip,name,typ,loc = mac_info.get(mac, ('','','',''))
    disp_ip = ip or '-'
    disp_name = name or '(未辨識/下聯)'
    disp_typ = typ or ''
    disp_loc = loc or ''
    lines.append((pidx, pname, mac, disp_ip, disp_name, disp_typ, disp_loc))

lines.sort(key=lambda x: (int(x[0]) if x[0].isdigit() else 999))
for pidx,pname,mac,ip,name,typ,loc in lines:
    print(f"{pname:<12}{mac:<20}{ip:<16}{name:<20}{typ:<10}{loc}")
print("="*100)
print(f"核心8100 直連埠總計 {len(lines)} 筆")
