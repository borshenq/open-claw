#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拓撲感知對照表: 每台設備 → 最下游交換器 + 實體埠
上聯埠判定: 該埠學習到大量 MAC(>5) = 上聯/聚合埠,跳過
其餘埠若只學到少數 MAC = 直連終端
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

# 抓每台交換器: 埠名, FDB(mac->set(port)), 每埠MAC計數
swdata={}
for name,ip,comm in SW:
    pn={}
    for l in walk(ip,comm,'1.3.6.1.2.1.2.2.1.2'):
        m=re.match(r'^.*\.(\d+)\s*=\s*STRING:\s*"?(.+)"?$',l)
        if m:
            # 短化 DGS 埠名: 抓 Port N
            pn[m.group(1)]=m.group(2).strip()
    fdb={}; portcount={}
    for l in walk(ip,comm,'1.3.6.1.2.1.17.4.3.1.2'):
        m=re.match(r'^.*\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\s*=\s*INTEGER:\s*(\d+)$',l.strip())
        if m:
            mac=':'.join(f'{int(x):02X}' for x in m.groups()[:6])
            if mac.startswith('02:'):continue
            pid=m.group(7)
            fdb.setdefault(mac,set()).add(pid)
            portcount[pid]=portcount.get(pid,0)+1
    swdata[name]={'pn':pn,'fdb':fdb,'portcount':portcount}
    # 顯示各埠MAC數(>2視為上聯)
    plist=sorted(portcount.items(),key=lambda x:int(x[0]))
    heavy=[f"{pn.get(p,f'idx{p}')}={c}" for p,c in plist if c>2]
    light=[f"{pn.get(p,f'idx{p}')}={c}" for p,c in plist if c<=2]
    print(f"✅ {name} | 直連埠: {', '.join(light) if light else '無'} | 上聯埠(MAC>2): {', '.join(heavy) if heavy else '無'}")

# ARP
arp={}
for l in subprocess.run(['ip','neigh','show'],capture_output=True,text=True).stdout.splitlines():
    m=re.match(r'(192\.60\.1\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)\s',l)
    if m: arp[m.group(1)]=norm(m.group(2))

# 庫存
inv={}
with open('dtps_inventory.csv',encoding='utf-8') as f:
    for r in csv.DictReader(f): inv[r['IP']]=r

print("\n"+"="*100)
print(f"{'設備名稱':<26}{'IP':<15}{'MAC':<20}{'交換器':<12}{'實體埠':<8}{'類型':<8}位置")
print("="*100)
rows=[]; 
for ip,mac in sorted(arp.items(),key=lambda x:[int(p) for p in x[0].split('.')[-1:]]):
    name=inv.get(ip,{}).get('Name','') or ip
    typ=inv.get(ip,{}).get('Type','')
    loc=inv.get(ip,{}).get('Location','')
    # 對每台交換器, 找此 MAC 出現的非上聯埠
    best=None
    for sname,s in swdata.items():
        if mac in s['fdb']:
            for pid in s['fdb'][mac]:
                pc=s['portcount'].get(pid,0)
                if pc<=2:  # 直連埠
                    candidate=(sname, s['pn'].get(pid,f'idx{pid}'))
                    # 選交換器優先序: DGS>Cisco>2930F-4>-3>-2>-1>核心
                    prio={'DGS-1510':1,'Cisco-9K':2,'2930F-4':3,'2930F-3':4,'2930F-2':5,'2930F-1':6,'CX8100-核心':7}
                    if best is None or prio.get(candidate[0],9)<prio.get(best[0],9):
                        best=candidate
    if best:
        rows.append((name,ip,mac,best[0],best[1],typ,loc))
    else:
        rows.append((name,ip,mac,'(僅見於上聯)','-',typ,loc))

rows.sort(key=lambda x:[int(p) for p in x[1].split('.')[-1:]])
for name,ip,mac,sname,port,typ,loc in rows:
    print(f"{name:<26}{ip:<15}{mac:<20}{sname:<12}{port:<8}{typ:<8}{loc}")
print("="*100)
