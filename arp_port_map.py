#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""以 ARP 表為主軸：每台有 IP 的設備 → IP/MAC/名稱 + 它連在哪台交換器哪個 port"""
import subprocess, re, csv

SWITCHES = [
    ('CX8100-核心', '192.60.1.245', 'SnmpPublic@TPC'),
    ('2930F-1',     '192.60.1.246', 'SnmpPublic@TPC'),
    ('2930F-2',     '192.60.1.247', 'SnmpPublic@TPC'),
    ('2930F-3',     '192.60.1.248', 'SnmpPublic@TPC'),
    ('2930F-4',     '192.60.1.251', 'SnmpPublic@TPC'),
    ('Cisco-9K',    '192.60.1.252', 'SnmpPublic@TPC'),
    ('DGS-1510',    '192.60.1.249', 'public'),
]

def walk(host, comm, oid):
    try:
        return subprocess.run(['snmpwalk','-v2c','-c',comm,'-On',host,oid],
            capture_output=True,text=True,timeout=20).stdout.splitlines()
    except: return []

def normalize(m):
    return ':'.join(f"{int(x,16):02X}" for x in re.split(r'[:.\-]',m.strip().upper())).upper()

# 1. 各交換器: port index -> 名稱, 與 FDB: mac -> port index
sw_fdb = {}  # sw_name -> {mac: portname}
for sw_name, sw_ip, comm in SWITCHES:
    pn = {}
    for line in walk(sw_ip, comm, '1.3.6.1.2.1.2.2.1.2'):
        m = re.match(r'^.*\.(\d+)\s*=\s*STRING:\s*"?(.+)"?$', line)
        if m:
            pn[m.group(1)] = m.group(2).strip()
    fdb = {}
    for line in walk(sw_ip, comm, '1.3.6.1.2.1.17.4.3.1.2'):
        # .1.3.6.1.2.1.17.4.3.1.2.<0>.<m1>...<m6> = INTEGER: portidx
        m = re.match(r'^.*\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\s*=\s*INTEGER:\s*(\d+)$', line)
        if m:
            mac = ':'.join(f"{int(x):02X}" for x in m.groups()[:6])
            portidx = m.group(7)
            pname = pn.get(portidx, f"idx{portidx}")
            # 排除 Aruba/Cisco 內部管理 MAC (本機 OUI 前綴像 F8:60:F0 是交換器本身)
            fdb[mac] = (sw_name, pname)
    sw_fdb[sw_name] = fdb
    print(f"✅ {sw_name}: {len(fdb)} FDB")

# 2. ARP 表 (有 IP 的設備)
arp = {}
for line in subprocess.run(['ip','neigh','show'],capture_output=True,text=True).stdout.splitlines():
    m = re.match(r'(192\.60\.1\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)\s', line)
    if m:
        arp[m.group(1)] = normalize(m.group(2))

# 3. 庫存
inv = {}
with open('dtps_inventory.csv',encoding='utf-8') as f:
    for r in csv.DictReader(f):
        inv[r['IP']] = r

# 4. 每台有 IP 的設備 → 找它 MAC 出現在哪台交換器 (優先核心，否則下層)
print("\n" + "="*110)
print(f"{'設備名稱':<24}{'IP':<15}{'MAC':<20}{'交換器':<12}{'Port':<12}{'類型':<8}位置")
print("="*110)
matched = 0; unmatched = []
# 先收集每台設備 MAC 在所有交換器出現的 (sw,port)，選最上層
for ip, mac in sorted(arp.items(), key=lambda x: [int(p) for p in x[0].split('.')[-1:]]):
    name = inv.get(ip,{}).get('Name','')
    typ  = inv.get(ip,{}).get('Type','')
    loc  = inv.get(ip,{}).get('Location','')
    places = []
    for sw_name, fdb in sw_fdb.items():
        if mac in fdb:
            places.append((sw_name, fdb[mac]))
    if not places:
        unmatched.append((ip, mac, name))
        continue
    # 選擇：核心出現優先；否則取第一個
    chosen = None
    for sw,p in places:
        if sw == 'CX8100-核心':
            chosen = (sw,p); break
    if not chosen:
        chosen = places[0]
    sw_name, port = chosen
    print(f"{name:<24}{ip:<15}{mac:<20}{sw_name:<12}{port:<12}{typ:<8}{loc}")
    matched += 1

print("="*110)
print(f"比對成功 {matched} 台，無法對應 {len(unmatched)} 台（FDB 未學習到）")
if unmatched:
    print("未對應設備:")
    for ip,mac,name in unmatched:
        print(f"  {ip} {mac} {name}")
