#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""將 topo_map 結果輸出成 CSV + 整理直連埠清單"""
import subprocess, re, csv

# 抓 topo_map 輸出
out = subprocess.run(['python3','topo_map.py'],capture_output=True,text=True,cwd='/home/borsheng/.openclaw/workspace').stdout
rows=[]
for line in out.splitlines():
    m=re.match(r'^(.{26})(.{15})(.{20})(.{12})(.{8})(.{8})(.*)$', line)
    if m and not line.startswith('=') and not line.startswith('✅'):
        name=m.group(1).strip(); ip=m.group(2).strip(); mac=m.group(3).strip()
        sw=m.group(4).strip(); port=m.group(5).strip(); typ=m.group(6).strip(); loc=m.group(7).strip()
        if re.match(r'^\d+\.\d+\.\d+\.\d+$',ip):
            rows.append([name,ip,mac,sw,port,typ,loc])

with open('port_mapping.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f)
    w.writerow(['設備名稱','IP','MAC','交換器','實體埠','類型','位置'])
    w.writerows(rows)
print(f"已寫入 port_mapping.csv：{len(rows)} 筆")
