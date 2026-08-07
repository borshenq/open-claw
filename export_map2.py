#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新產出乾淨的 port_mapping.csv: 簡化埠名 + 正確欄位"""
import subprocess, re, csv

def short_port(sw, p):
    """簡化埠名顯示"""
    p = p.strip().strip('"')
    if 'D-Link' in p:
        m = re.search(r'Port\s*(\d+)', p)
        return f"Port {m.group(1)}" if m else 'DGS-port'
    if p.startswith('1/1/'):
        return p
    if p in ('idx0','0'):
        return '(本體)'
    return p

# 沿用 topo 邏輯重新跑一次乾淨版
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

swdata={}
for name,ip,comm in SW:
    pn={}
    for l in walk(ip,comm,'1.3.6.1.2.1.2.2.1.2'):
        m=re.match(r'^.*\.(\d+)\s*=\s*STRING:\s*"?(.+)"?$',l)
        if m: pn[m.group(1)]=m.group(2).strip()
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

arp={}
for l in subprocess.run(['ip','neigh','show'],capture_output=True,text=True).stdout.splitlines():
    m=re.match(r'(192\.60\.1\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)\s',l)
    if m: arp[m.group(1)]=norm(m.group(2))

inv={}
with open('dtps_inventory.csv',encoding='utf-8') as f:
    for r in csv.DictReader(f): inv[r['IP']]=r

rows=[]
for ip,mac in sorted(arp.items(),key=lambda x:[int(p) for p in x[0].split('.')[-1:]]):
    name=inv.get(ip,{}).get('Name','') or ip
    typ=inv.get(ip,{}).get('Type','')
    loc=inv.get(ip,{}).get('Location','')
    best=None
    for sname,s in swdata.items():
        if mac in s['fdb']:
            for pid in s['fdb'][mac]:
                pc=s['portcount'].get(pid,0)
                if pc<=2:
                    cand=(sname, s['pn'].get(pid,f'idx{pid}'))
                    prio={'DGS-1510':1,'Cisco-9K':2,'2930F-4':3,'2930F-3':4,'2930F-2':5,'2930F-1':6,'CX8100-核心':7}
                    if best is None or prio.get(cand[0],9)<prio.get(best[0],9):
                        best=cand
    if best:
        rows.append([name,ip,mac,best[0],short_port(best[0],best[1]),typ,loc])
    else:
        rows.append([name,ip,mac,'(僅見於上聯)','-',typ,loc])

with open('port_mapping.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f)
    w.writerow(['設備名稱','IP','MAC','交換器','實體埠','類型','位置'])
    w.writerows(rows)
print(f"✅ 已重新產出 port_mapping.csv：{len(rows)} 筆")
print("預覽:")
for r in rows[:8]:
    print("  ", r)
