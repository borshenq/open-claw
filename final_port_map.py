#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""終極對照表: 每台設備 → 最靠近它的交換器實體埠
策略: 從 ARP 表出發,對每台有 IP 設備,去 7 台交換器 FDB 找它 MAC,
選「埠名非聚合/上聯」且直接學習到的交換器;若只出現在某交換器多埠,取實體埠。
"""
import subprocess, re, csv

SW = [
    ('CX8100-核心','192.60.1.245','SnmpPublic@TPC'),
    ('2930F-1','192.60.1.246','SnmpPublic@TPC'),
    ('2930F-2','192.60.1.247','SnmpPublic@TPC'),
    ('2930F-3','192.60.1.248','SnmpPublic@TPC'),
    ('2930F-4','192.60.1.251','SnmpPublic@TPC'),
    ('Cisco-9K','192.60.1.252','SnmpPublic@TPC'),
    ('DGS-1510','192.60.1.249','public'),
]

def walk(host,comm,oid):
    try:
        return subprocess.run(['snmpwalk','-v2c','-c',comm,'-On',host,oid],
            capture_output=True,text=True,timeout=20).stdout.splitlines()
    except: return []

def norm(m):
    return ':'.join(f"{int(x,16):02X}" for x in re.split(r'[:.\-]',m.strip().upper())).upper()

# 各交換器 port名 + FDB
sw = {}
for name,ip,comm in SW:
    pn={}
    for l in walk(ip,comm,'1.3.6.1.2.1.2.2.1.2'):
        m=re.match(r'^.*\.(\d+)\s*=\s*STRING:\s*"?(.+)"?$',l)
        if m: pn[m.group(1)]=m.group(2).strip()
    fdb={}
    for l in walk(ip,comm,'1.3.6.1.2.1.17.4.3.1.2'):
        m=re.match(r'^.*\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\s*=\s*INTEGER:\s*(\d+)$',l.strip())
        if m:
            mac=':'.join(f'{int(x):02X}' for x in m.groups()[:6])
            if mac.startswith('02:'): continue
            fdb.setdefault(mac,set()).add(pn.get(m.group(7),f"idx{m.group(7)}"))
    sw[name]={'pn':pn,'fdb':fdb}
    print(f"✅ {name}: {len(fdb)} MAC")

# 聚合/上聯埠判定
AGG_PAT = re.compile(r'^(trk|lag|po|port-channel|1/1/(?:21|23|25|27|29|31|47|48)|GigabitEthernet1/0/(?:24|25|26|27|28|47|48))', re.I)

# ARP
arp={}
for l in subprocess.run(['ip','neigh','show'],capture_output=True,text=True).stdout.splitlines():
    m=re.match(r'(192\.60\.1\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)\s',l)
    if m: arp[m.group(1)]=norm(m.group(2))

# 庫存
inv={}
with open('dtps_inventory.csv',encoding='utf-8') as f:
    for r in csv.DictReader(f): inv[r['IP']]=r

print("\n"+"="*115)
print(f"{'設備名稱':<26}{'IP':<15}{'MAC':<20}{'交換器':<12}{'實體埠':<12}{'類型':<8}位置")
print("="*115)
rows=[]; nofdb=[]
for ip,mac in sorted(arp.items(),key=lambda x:[int(p) for p in x[0].split('.')[-1:]]):
    name=inv.get(ip,{}).get('Name','') or ip
    typ=inv.get(ip,{}).get('Type','')
    loc=inv.get(ip,{}).get('Location','')
    # 找出所有出現的交換器+埠
    places=[]
    for sname,s in sw.items():
        if mac in s['fdb']:
            for p in s['fdb'][mac]:
                places.append((sname,p))
    if not places:
        nofdb.append((ip,mac,name))
        continue
    # 選「非聚合且最接近終端」: 優先 DGS/Cisco/2930F 的實體埠,避免核心上聯
    # 過濾掉明確聚合埠
    real=[pl for pl in places if not AGG_PAT.search(pl[1])]
    if not real: real=places
    # 選交換器優先序: DGS > Cisco > 2930F-4 > 2930F-3 > 2930F-2 > 2930F-1 > 核心
    prio={'DGS-1510':1,'Cisco-9K':2,'2930F-4':3,'2930F-3':4,'2930F-2':5,'2930F-1':6,'CX8100-核心':7}
    real.sort(key=lambda x:(prio.get(x[0],9), x[1]))
    sname,port=real[0]
    rows.append((name,ip,mac,sname,port,typ,loc))

rows.sort(key=lambda x:[int(p) for p in x[1].split('.')[-1:]])
for name,ip,mac,sname,port,typ,loc in rows:
    print(f"{name:<26}{ip:<15}{mac:<20}{sname:<12}{port:<12}{typ:<8}{loc}")
print("="*115)
print(f"對照成功 {len(rows)} 台, FDB 未學習到 {len(nofdb)} 台")
if nofdb:
    print("未對應:")
    for ip,mac,name in nofdb: print(f"  {ip} {mac} {name}")
