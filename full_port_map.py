#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整對照表: 每台主機 IP/MAC/名稱 + 位於哪台交換器實體埠"""
import subprocess, re, csv

SWITCHES = [
    ('CX8100-核心', '192.60.1.245', 'SnmpPublic@TPC', r'1/1/\d+'),
    ('2930F-1',     '192.60.1.246', 'SnmpPublic@TPC', r'\d+'),
    ('2930F-2',     '192.60.1.247', 'SnmpPublic@TPC', r'\d+'),
    ('2930F-3',     '192.60.1.248', 'SnmpPublic@TPC', r'\d+'),
    ('2930F-4',     '192.60.1.251', 'SnmpPublic@TPC', r'\d+'),
    ('Cisco-9K',    '192.60.1.252', 'SnmpPublic@TPC', r'GigabitEthernet'),
    ('DGS-1510',    '192.60.1.249', 'public',          r'\d+'),
]

def walk(host, comm, oid):
    try:
        return subprocess.run(['snmpwalk','-v2c','-c',comm,'-On',host,oid],
            capture_output=True,text=True,timeout=20).stdout.splitlines()
    except: return []

def mac_from_oid(oid):
    # OID 尾段格式: <0>.<m1>.<m2>.<m3>.<m4>.<m5>.<m6> (7段)
    # MAC = m1:m2:m3:m4:m5:m6 (每段十進位轉 hex)
    nums = oid.strip('.').split('.')
    tail = [int(x) for x in nums[-7:]]
    return ':'.join(f"{x:02X}" for x in tail[1:])

def normalize(m):
    return ':'.join(f"{int(x,16):02X}" for x in re.split(r'[:.\-]',m.strip().upper())).upper()

# ARP
arp = {}
try:
    for line in subprocess.run(['ip','neigh','show'],capture_output=True,text=True).stdout.splitlines():
        m = re.match(r'(192\.60\.1\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)', line)
        if m and not m.group(2).startswith('02:'):
            arp[normalize(m.group(2))] = m.group(1)
except: pass

# 庫存
inv = {}
try:
    with open('dtps_inventory.csv',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            inv[r['IP']] = r
except Exception as e:
    print("庫存:", e)

mac_info = {}
for ip,r in inv.items():
    if r.get('MAC'):
        mac_info.setdefault(normalize(r['MAC']), (ip,r['Name'],r['Type'],r['Location']))
for mac,ip in arp.items():
    if mac not in mac_info:
        n = inv.get(ip,{})
        mac_info[mac] = (ip,n.get('Name',''),n.get('Type',''),n.get('Location',''))

# 掃每台交換器: 實體埠 -> 學習到的 MAC (只取埠名符合 + MAC 非內部02:/交換器本體)
print("="*115)
print(f"{'設備名稱':<22}{'IP':<15}{'MAC':<20}{'交換器':<12}{'埠':<14}{'類型':<8}位置")
print("="*115)
seen_dev = set()
for sw_name, sw_ip, comm, port_pat in SWITCHES:
    # port index -> 名稱
    pn = {}
    for line in walk(sw_ip, comm, '1.3.6.1.2.1.2.2.1.2'):
        m = re.match(r'^.*\.(\d+) = STRING:\s*"?([^"]+)"?', line)
        if m and re.match(port_pat, m.group(2)):
            pn[m.group(1)] = m.group(2)
    # FDB: MAC -> port index
    fdb = {}
    for line in walk(sw_ip, comm, '1.3.6.1.2.1.17.4.3.1.2'):
        # 格式: .1.3.6.1.2.1.17.4.3.1.2.<0>.<m1>...<m6> = INTEGER: portidx
        mm = re.match(r'^(.*\.(?:\d+){7}) = INTEGER:\s*(\d+)$', line)
        if mm:
            oid = mm.group(1); portidx = mm.group(2)
            mac = mac_from_oid(oid)
            # 排除 Aruba 內部/虛擬 MAC (02: = locally administered / 交換器管理)
            if mac.startswith('02:'):
                continue
            fdb.setdefault(mac, portidx)
    # 輸出
    for mac, pidx in fdb.items():
        pname = pn.get(pidx, f"idx{pidx}")
        ip,name,typ,loc = mac_info.get(mac, ('','','',''))
        if not ip and not name: continue  # 只顯示能識別的
        if mac.startswith('02:'): continue
        disp_ip = ip or '-'
        disp_name = name or '(未辨識)'
        disp_typ = typ or ''
        disp_loc = loc or ''
        key=(mac)
        if key in seen_dev: 
            continue  # 每設備只顯示第一個(最上層)交換器
        seen_dev.add(key)
        print(f"{disp_name:<22}{disp_ip:<15}{mac:<20}{sw_name:<12}{pname:<14}{disp_typ:<8}{disp_loc}")
print("="*115)
print(f"已辨識終端設備總數: {len(seen_dev)}")
