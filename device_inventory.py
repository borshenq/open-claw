import argparse
import csv
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

INVENTORY_FILE = 'dtps_inventory.csv'
HEADERS = ['IP', 'Name', 'Type', 'Location', 'MAC', 'Notes']

def get_display_width(s):
    """計算字串在終端機顯示的大致寬度（全形字元和特定 Emoji 算作 2 格）"""
    width = 0
    for char in s:
        if ord(char) > 127 or char in ['✅', '❌']:
            width += 2
        else:
            width += 1
    return width

def pad_to_width(s, width):
    """根據顯示寬度將字串填充空格到指定寬度"""
    w = get_display_width(s)
    if w >= width:
        return s
    return s + ' ' * (width - w)

def ensure_file_exists():
    """確保庫存 CSV 檔案存在，若無則建立並寫入標題"""
    if not os.path.exists(INVENTORY_FILE):
        # 貼心檢查：如果有舊的 inventory.csv，自動轉移並升級欄位
        if os.path.exists('inventory.csv'):
            try:
                with open('inventory.csv', mode='r', newline='', encoding='utf-8') as old_f:
                    reader = csv.reader(old_f)
                    try:
                        next(reader) # skip header
                    except StopIteration:
                        pass
                    old_rows = list(reader)
                
                with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(HEADERS)
                    for row in old_rows:
                        # 舊格式: [IP, Name, Type, Location, Notes]
                        # 轉新格式: [IP, Name, Type, Location, MAC (空), Notes]
                        if len(row) == 5:
                            row = [row[0], row[1], row[2], row[3], '', row[4]]
                        elif len(row) < len(HEADERS):
                            row = row + [''] * (len(HEADERS) - len(row))
                        writer.writerow(row)
                print(f"💡 偵測到舊的 inventory.csv，已成功遷移並升級至 {INVENTORY_FILE}")
                return
            except Exception as e:
                print(f"⚠️ 移轉舊資料失敗，建立新檔案。錯誤：{e}")
        
        with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def read_inventory():
    """讀取庫存資料"""
    ensure_file_exists()
    with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader) # skip header
        except StopIteration:
            pass
        
        rows = []
        for row in reader:
            # 相容性處理：若資料欄位不足，自動補齊
            if len(row) == 5:
                row = [row[0], row[1], row[2], row[3], '', row[4]]
            elif len(row) < len(HEADERS):
                row = row + [''] * (len(HEADERS) - len(row))
            rows.append(row)
        return rows

def write_inventory(data):
    """將資料寫回庫存 CSV"""
    with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(data)

def format_table(data, headers=None):
    """手動排版輸出表格，支援中文字元與 Emoji 對齊"""
    if not data:
        return "沒有找到任何設備。"
    
    display_headers = headers if headers is not None else HEADERS
    
    # 計算每個欄位的最大寬度
    col_widths = [get_display_width(h) for h in display_headers]
    for row in data:
        for i, item in enumerate(row):
            length = get_display_width(str(item))
            if length > col_widths[i]:
                col_widths[i] = length
                
    # 最少給予一定的寬度
    col_widths = [max(w, 8) for w in col_widths]

    # 建立格式化字串
    header_str = " | ".join([pad_to_width(h, col_widths[i]) for i, h in enumerate(display_headers)])
    separator = "-+-".join(["-" * w for w in col_widths])
    
    lines = [header_str, separator]
    for row in data:
        row_str = " | ".join([pad_to_width(str(item), col_widths[i]) for i, item in enumerate(row)])
        lines.append(row_str)
        
    return "\n".join(lines)

def list_devices(args):
    """列出所有設備"""
    data = read_inventory()
    print(format_table(data))

def add_device(args):
    """新增設備"""
    ensure_file_exists()
    mac = args.mac if hasattr(args, 'mac') and args.mac else ''
    row = [args.ip, args.name, args.type, args.location, mac, args.notes]
    
    # 檢查 IP 是否重複
    data = read_inventory()
    if any(r[0].strip() == args.ip.strip() for r in data):
        print(f"❌ 錯誤：IP '{args.ip}' 已存在於庫存中！")
        return
        
    with open(INVENTORY_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)
    print(f"✅ 成功新增設備：{args.ip} ({args.name})")

def delete_device(args):
    """根據 IP 刪除設備"""
    data = read_inventory()
    target_ip = args.ip.strip()
    
    found = False
    new_data = []
    deleted_row = None
    for row in data:
        if row[0].strip() == target_ip:
            found = True
            deleted_row = row
        else:
            new_data.append(row)
            
    if not found:
        print(f"❌ 找不到 IP 為 '{target_ip}' 的設備。")
        return
        
    write_inventory(new_data)
    print(f"✅ 成功刪除設備：{deleted_row[0]} ({deleted_row[1]})")

def ping_ip(ip):
    """執行 ping 測試，回傳 True (在線) 或 False (離線)"""
    try:
        # -c 1: 傳送一個封包
        # -W 1: 等待回應時間為 1 秒
        res = subprocess.run(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except Exception:
        return False

def ping_devices(args):
    """對所有設備做 ping 測試"""
    data = read_inventory()
    if not data:
        print("沒有找到任何設備。")
        return
        
    print("正在對所有設備進行 ping 測試，請稍候...")
    
    ips = [row[0] for row in data]
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(ping_ip, ips))
        
    ping_data = []
    for row, is_online in zip(data, results):
        status = "✅在線" if is_online else "❌離線"
        ping_data.append([status] + row)
        
    print(format_table(ping_data, headers=['Status'] + HEADERS))

def show_stats(args):
    """顯示設備統計報表"""
    data = read_inventory()
    if not data:
        print("沒有找到任何設備，無法進行統計。")
        return
        
    type_counts = {}
    location_counts = {}
    
    for row in data:
        device_type = row[2].strip() or "未分類"
        location = row[3].strip() or "未分類"
        
        type_counts[device_type] = type_counts.get(device_type, 0) + 1
        location_counts[location] = location_counts.get(location, 0) + 1
        
    print("┌──────────────────────────────────────────┐")
    print("│             大屯國小設備統計報表         │")
    print("├──────────────────────────────────────────┤")
    print("  [ 設備類型統計 ]")
    for dtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {dtype:<15}: {count:>3} 台")
        
    print("\n  [ 設備位置統計 ]")
    for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {loc:<15}: {count:>3} 台")
    print("└──────────────────────────────────────────┘")

def edit_device(args):
    """根據 IP 修改設備資訊"""
    data = read_inventory()
    target_ip = args.ip.strip()
    
    target_index = -1
    for i, row in enumerate(data):
        if row[0].strip() == target_ip:
            target_index = i
            break
            
    if target_index == -1:
        print(f"❌ 找不到 IP 為 '{target_ip}' 的設備。")
        return
        
    if not any([args.name, args.type, args.location, args.mac, args.notes]):
        print("⚠️  請指定至少一個要修改的欄位 (例如 --name, --type, --location, --mac, --notes)")
        return
        
    old_row = list(data[target_index])
    new_row = list(old_row)
    
    if args.name is not None:
        new_row[1] = args.name
    if args.type is not None:
        new_row[2] = args.type
    if args.location is not None:
        new_row[3] = args.location
    if args.mac is not None:
        new_row[4] = args.mac
    if args.notes is not None:
        new_row[5] = args.notes
        
    data[target_index] = new_row
    write_inventory(data)
    
    print(f"✅ 成功修改設備 '{target_ip}' 的資訊：")
    changes = []
    for h, old_val, new_val in zip(HEADERS, old_row, new_row):
        if old_val != new_val:
            changes.append(f"  - {h}: '{old_val}' ➡️  '{new_val}'")
            
    print("\n".join(changes))

def search_devices(args):
    """搜尋設備"""
    data = read_inventory()
    keyword = args.keyword.lower()
    results = [row for row in data if any(keyword in str(item).lower() for item in row)]
    if results:
        print(format_table(results))
    else:
        print(f"找不到包含關鍵字 '{args.keyword}' 的設備。")

def export_devices(args):
    """匯出設備清單"""
    ensure_file_exists()
    output_file = args.output
    try:
        shutil.copyfile(INVENTORY_FILE, output_file)
        print(f"已成功匯出清單至：{output_file}")
    except Exception as e:
        print(f"匯出失敗: {e}")

def main():
    parser = argparse.ArgumentParser(description="設備清單管理系統 (Device Inventory)")
    subparsers = parser.add_subparsers(dest='command', help='可用指令')
    subparsers.required = True

    # list
    parser_list = subparsers.add_parser('list', help='列出所有設備')
    parser_list.set_defaults(func=list_devices)

    # add
    parser_add = subparsers.add_parser('add', help='新增設備')
    parser_add.add_argument('ip', help='IP 位址')
    parser_add.add_argument('name', help='設備名稱')
    parser_add.add_argument('type', help='設備類型')
    parser_add.add_argument('location', help='設備位置')
    parser_add.add_argument('notes', help='備註')
    parser_add.add_argument('--mac', default='', help='MAC 位址 (選填)')
    parser_add.set_defaults(func=add_device)

    # delete
    parser_delete = subparsers.add_parser('delete', help='根據 IP 刪除設備')
    parser_delete.add_argument('ip', help='要刪除的設備 IP 位址')
    parser_delete.set_defaults(func=delete_device)

    # ping
    parser_ping = subparsers.add_parser('ping', help='對所有設備做 ping 測試')
    parser_ping.set_defaults(func=ping_devices)

    # stats
    parser_stats = subparsers.add_parser('stats', help='顯示設備統計報表')
    parser_stats.set_defaults(func=show_stats)

    # edit
    parser_edit = subparsers.add_parser('edit', help='根據 IP 修改設備資訊')
    parser_edit.add_argument('ip', help='要修改的設備 IP 位址')
    parser_edit.add_argument('--name', help='修改設備名稱')
    parser_edit.add_argument('--type', help='修改設備類型')
    parser_edit.add_argument('--location', help='修改設備位置')
    parser_edit.add_argument('--mac', help='修改 MAC 位址')
    parser_edit.add_argument('--notes', help='修改備註')
    parser_edit.set_defaults(func=edit_device)

    # search
    parser_search = subparsers.add_parser('search', help='搜尋設備')
    parser_search.add_argument('keyword', help='搜尋關鍵字')
    parser_search.set_defaults(func=search_devices)

    # export
    parser_export = subparsers.add_parser('export', help='匯出設備清單為新的 CSV 檔案')
    parser_export.add_argument('--output', '-o', default='exported_inventory.csv', help='匯出的檔案名稱 (預設: exported_inventory.csv)')
    parser_export.set_defaults(func=export_devices)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
