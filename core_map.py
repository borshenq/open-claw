#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核心 CX8100 直連埠對照表：MAC→port→設備(IP/名稱)"""
import subprocess, re, csv

def normalize(m):
    return ':'.join(f"{int(x,16):02X}" for x in re.split(r'[:.\-]',m.strip().upper())).upper()

# 核心 8100 FDB (MAC -> port index)
fdb = {}
out = subprocess.run(['snmpwalk','-v2c','-c','SnmpPublic@TPC','-On','192.60.1.245','1.3.6.1.2.1.17.4.3.1.2'],
    capture_output=True,text=True,timeout=25).stdout.splitlines()
for line in out:
    m = re.match(r'^.*\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\s*=\s*INTEGER:\s*(\d+)$', line.strip())
    if m:
        mac=':'.join(f'{int(x):02X}' for x in m.groups()[:6])
        if mac.startswith('02:'): continue
        fdb.setdefault(mac, m.group(7))

# port index -> 名稱
pn = {}
out = subprocess.run(['snmpwalk','-v2c','-c','SnmpPublic@TPC','-On','192.60.1.245','1.3.6.1.2.1.2.2.1.2'],
    capture_output=True,text=True,timeout=25).stdout.splitlines()
for line in out:
    m = re.match(r'^.*\.(\d+)\s*=\s*STRING:\s*"?(1/1/\d+)"?$', line.strip())
    if m: pn[m.group(1)] = m.group(2)

# ARP (IP->MAC)
arp = {}
for line in subprocess.run(['ip','neigh','show'],capture_output=True,text=True).stdout.splitlines():
    m = re.match(r'(192\.60\.1\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)\s', line)
    if m: arp[normalize(m.group(2))] = m.group(1)

# 庫存
inv = {}
with open('dtps_inventory.csv',encoding='utf-8') as f:
    for r in csv.DictReader(f): inv[r['IP']] = r

# MAC -> 設備(ip,name,type,loc)
mac_info = {}
for ip,r in inv.items():
    if r.get('MAC'): mac_info.setdefault(normalize(r['MAC']),(ip,r['Name'],r['Type'],r['Location']))
for mac,ip in arp.items():
    if mac not in mac_info:
        n=inv.get(ip,{})
        mac_info[mac]=(ip,n.get('Name',''),n.get('Type',''),n.get('Location',''))

print("\n"+"="*110)
print(f"{'設備名稱':<26}{'IP':<15}{'MAC':<20}{'核心8100埠':<10}{'類型':<10}位置")
print("="*110)
rows=[]
for mac,pidx in fdb.items():
    ip,name,typ,loc = mac_info.get(mac,('','','',''))
    pname = pn.get(pidx, f"idx{pidx}")
    disp_ip=ip or '-'; disp_name=name or '(未辨識)'
    rows.append((pidx,pname,mac,disp_ip,disp_name,typ,loc))
rows.sort(key=lambda x:(int(x[0]) if x[0].isdigit() else 999))
for pidx,pname,mac,ip,name,typ,loc in rows:
    print(f"{name:<26}{ip:<15}{mac:<20}{pname:<10}{typ:<10}{loc}")
print("="*110)
print(f"核心8100 直連埠設備：{len(rows)} 筆")
