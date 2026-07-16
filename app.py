import os
import csv
import subprocess
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'dtps-inventory-secret-key'

INVENTORY_FILE = '/home/borsheng/.openclaw/workspace/dtps_inventory.csv'
HEADERS = ['IP', 'Name', 'Type', 'Location', 'MAC', 'Notes']

# --- 資料讀寫與輔助函數 ---

def ensure_file_exists():
    """確保庫存 CSV 檔案存在，若無則建立並寫入標題"""
    if not os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def read_inventory():
    """讀取庫存資料"""
    ensure_file_exists()
    with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader)  # 跳過標題列
        except StopIteration:
            pass
        
        rows = []
        for row in reader:
            if not row:
                continue
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

def ping_ip(ip):
    """執行 ping 測試，回傳 True (在線) 或 False (離線)"""
    try:
        # -c 1: 傳送一個封包
        # -W 1: 等待回應時間為 1 秒
        res = subprocess.run(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except Exception:
        return False

def scan_ports(ip):
    """掃描 IP 的常見 port，回傳 [{port, name, status}]"""
    import socket
    COMMON_PORTS = [
        (21, 'FTP'), (22, 'SSH'), (23, 'Telnet'), (25, 'SMTP'), (53, 'DNS'),
        (80, 'HTTP'), (110, 'POP3'), (111, 'RPC'), (135, 'RPC'), (137, 'NetBIOS'),
        (139, 'SMB'), (143, 'IMAP'), (389, 'LDAP'), (443, 'HTTPS'), (445, 'SMB'),
        (3389, 'RDP'), (5432, 'PostgreSQL'), (3306, 'MySQL'), (6379, 'Redis'),
        (8080, 'HTTP-Alt'), (8443, 'HTTPS-Alt'), (9090, 'HTTP-Alt2')
    ]
    results = []
    for port, name in COMMON_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        status = sock.connect_ex((ip, port))
        sock.close()
        results.append({'port': port, 'name': name, 'status': 'open' if status == 0 else 'closed'})
    return results

def is_school_ip(ip):
    """檢查是否為 192.60.1.0/24 網段"""
    try:
        parts = ip.strip().split('.')
        if len(parts) != 4:
            return False
        return parts[0] == '192' and parts[1] == '60' and parts[2] == '1'
    except:
        return False

def get_display_width(s):
    """計算字串在終端機顯示的大致寬度（全形字元算作 2 格）"""
    width = 0
    for char in s:
        if ord(char) > 127:
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

def get_cli_stats(data):
    """產生與 CLI 版本一致的文字對齊統計報表"""
    type_counts = {}
    location_counts = {}
    
    for row in data:
        device_type = row[2].strip() or "未分類"
        location = row[3].strip() or "未分類"
        
        type_counts[device_type] = type_counts.get(device_type, 0) + 1
        location_counts[location] = location_counts.get(location, 0) + 1
        
    lines = []
    lines.append("┌──────────────────────────────────────────┐")
    lines.append("│             大屯國小設備統計報表         │")
    lines.append("├──────────────────────────────────────────┤")
    lines.append("  [ 設備類型統計 ]")
    for dtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        padded_dtype = pad_to_width(dtype, 15)
        lines.append(f"  - {padded_dtype}: {count:>3} 台")
        
    lines.append("\n  [ 設備位置統計 ]")
    for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True):
        padded_loc = pad_to_width(loc, 15)
        lines.append(f"  - {padded_loc}: {count:>3} 台")
    lines.append("└──────────────────────────────────────────┘")
    return "\n".join(lines)


# --- HTML 模板定義 ---

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - 大屯國小設備管理系統</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Noto Sans TC', sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15);
        }
        .navbar-brand {
            font-weight: 700;
            letter-spacing: 0.5px;
            font-size: 1.3rem;
        }
        .nav-link {
            font-weight: 500;
            padding: 0.5rem 1rem !important;
            margin: 0 0.2rem;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.1);
            color: #fef08a !important;
        }
        .nav-link.active {
            background-color: rgba(255, 255, 255, 0.15);
            color: #fef08a !important;
            font-weight: 700;
        }
        .card {
            border: none;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            background-color: #ffffff;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .card-header {
            background-color: #ffffff;
            border-bottom: 1px solid #f1f5f9;
            border-top-left-radius: 16px !important;
            border-top-right-radius: 16px !important;
        }
        .table-responsive {
            border-radius: 16px;
            overflow: hidden;
        }
        .table {
            margin-bottom: 0;
        }
        .table th {
            font-weight: 600;
            background-color: #f1f5f9;
            color: #475569;
            border-bottom-width: 1px;
            padding: 1rem 0.75rem;
        }
        .table td {
            padding: 1rem 0.75rem;
            color: #334155;
            border-bottom: 1px solid #f1f5f9;
        }
        .table tr:last-child td {
            border-bottom: none;
        }
        .btn {
            border-radius: 10px;
            font-weight: 500;
            padding: 0.5rem 1.25rem;
            transition: all 0.2s ease;
        }
        .btn-sm {
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
        }
        .badge {
            font-weight: 500;
            padding: 0.4em 0.8em;
            border-radius: 6px;
        }
        .badge-online {
            background-color: #dcfce7;
            color: #15803d;
        }
        .badge-offline {
            background-color: #fee2e2;
            color: #b91c1c;
        }
        .footer {
            margin-top: auto;
            background-color: #ffffff;
            border-top: 1px solid #e2e8f0;
            color: #64748b;
        }
        .text-monospace {
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        }
        /* --- 行動優化 CSS --- */
        @media (max-width: 576px) {
            .card { padding: 0; }
            .card-body { padding: 1rem !important; }
            body { font-size: 0.95rem; }
            .table-responsive { overflow-x: auto; }
            .table th { white-space: nowrap; }
            .chart-wrapper { height: 180px !important; }
        }
        @media (max-width: 768px) {
            .navbar-brand { font-size: 1.1rem !important; }
            .navbar-toggler { padding: 0.5rem 0.6rem; font-size: 1.25rem; border-width: 2px; }
            .action-text { display: none !important; }
            .form-label { font-size: 0.9rem; }
            .form-control, .form-select, textarea { padding: 0.75rem; }
            .mobile-full-btn { width: 100% !important; display: block; margin-top: 0.5rem; }
            .mobile-textarea { height: 60px !important; }
            .mobile-row { display: table-row !important; }
            .desktop-row { display: none !important; }
            .desktop-thead { display: none !important; }
            #pingProgressContainer { padding: 1.5rem !important; }
            .progress { height: 16px !important; }
        }
        @media (min-width: 769px) {
            .mobile-row { display: none !important; }
        }
    </style>
</head>
<body>
    <!-- 導航列 -->
    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="/">
                <i class="bi bi-cpu-fill me-2 fs-4"></i>大屯國小設備管理系統
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'dashboard' %}active{% endif %}" href="/">
                            <i class="bi bi-speedometer2 me-1"></i>儀表板
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'devices' %}active{% endif %}" href="/devices">
                            <i class="bi bi-list-task me-1"></i>設備清單
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'add' %}active{% endif %}" href="/add">
                            <i class="bi bi-plus-circle me-1"></i>新增設備
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'ping' %}active{% endif %}" href="/ping">
                            <i class="bi bi-broadcast me-1"></i>Ping 測試
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'stats' %}active{% endif %}" href="/stats">
                            <i class="bi bi-bar-chart-line me-1"></i>統計報表
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'portscan' %}active{% endif %}" href="/portscan">
                            <i class="bi bi-shield-check me-1"></i>Port掃描
                        </a>
                        <a class="nav-link {% if active_page == 'networkmap' %}active{% endif %}" href="/networkmap">
                            <i class="bi bi-diagram-3 me-1"></i>網路拓撲
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- 主要內容區 -->
    <div class="container mb-5">
        <!-- 訊息提示 -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category if category != 'error' else 'danger' }} alert-dismissible fade show shadow-sm border-0 mb-4" role="alert" style="border-radius: 12px;">
                        <div class="d-flex align-items-center">
                            {% if category == 'success' %}
                                <i class="bi bi-check-circle-fill me-2 fs-5 text-success"></i>
                            {% else %}
                                <i class="bi bi-exclamation-triangle-fill me-2 fs-5 text-danger"></i>
                            {% endif %}
                            <div>{{ message }}</div>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <!-- 頁尾 -->
    <footer class="footer py-3 text-center">
        <div class="container">
            <span>© 2026 大屯國小設備清單管理系統 · 資訊組管理端</span>
        </div>
    </footer>

    <!-- Bootstrap 5 Bundle JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 共用的 Bootstrap 表單驗證機制
        (function () {
            'use strict'
            var forms = document.querySelectorAll('.needs-validation')
            Array.prototype.slice.call(forms)
                .forEach(function (form) {
                    form.addEventListener('submit', function (event) {
                        if (!form.checkValidity()) {
                            event.preventDefault()
                            event.stopPropagation()
                        }
                        form.classList.add('was-validated')
                    }, false)
                })
        })()
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""

DASHBOARD_TEMPLATE_CONTENT = """
<div class="row g-4 mb-4">
    <!-- 總設備數 -->
    <div class="col-md-4">
        <div class="card bg-primary text-white h-100 border-0 shadow-sm" style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);">
            <div class="card-body d-flex align-items-center p-4">
                <div class="rounded-circle bg-white bg-opacity-20 p-3 me-3 d-flex align-items-center justify-content-center" style="width: 64px; height: 64px;">
                    <i class="bi bi-pc-display-horizontal fs-2"></i>
                </div>
                <div>
                    <h6 class="card-title mb-1 text-white-50">總設備數</h6>
                    <h2 class="display-6 fw-bold mb-0">{{ total_devices }} <span class="fs-6 fw-normal">台</span></h2>
                </div>
            </div>
        </div>
    </div>
    <!-- 設備類型數 -->
    <div class="col-md-4">
        <div class="card bg-success text-white h-100 border-0 shadow-sm" style="background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);">
            <div class="card-body d-flex align-items-center p-4">
                <div class="rounded-circle bg-white bg-opacity-20 p-3 me-3 d-flex align-items-center justify-content-center" style="width: 64px; height: 64px;">
                    <i class="bi bi-tags fs-2"></i>
                </div>
                <div>
                    <h6 class="card-title mb-1 text-white-50">設備類型數</h6>
                    <h2 class="display-6 fw-bold mb-0">{{ total_types }} <span class="fs-6 fw-normal">種</span></h2>
                </div>
            </div>
        </div>
    </div>
    <!-- 位置總數 -->
    <div class="col-md-4">
        <div class="card bg-info text-white h-100 border-0 shadow-sm" style="background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 100%);">
            <div class="card-body d-flex align-items-center p-4">
                <div class="rounded-circle bg-white bg-opacity-20 p-3 me-3 d-flex align-items-center justify-content-center" style="width: 64px; height: 64px;">
                    <i class="bi bi-geo-alt fs-2"></i>
                </div>
                <div>
                    <h6 class="card-title mb-1 text-white-50">涵蓋位置數</h6>
                    <h2 class="display-6 fw-bold mb-0">{{ total_locations }} <span class="fs-6 fw-normal">處</span></h2>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row g-4 mb-4">
    <!-- 類型統計圖表 -->
    <div class="col-md-6">
        <div class="card h-100 shadow-sm border-0">
            <div class="card-header d-flex justify-content-between align-items-center bg-white py-3 border-0">
                <span class="fw-bold"><i class="bi bi-bar-chart-fill me-2 text-primary"></i>設備類型分佈</span>
            </div>
            <div class="card-body">
                <div class="chart-wrapper" style="position: relative; height:240px; width:100%">
                    <canvas id="typeChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    <!-- 位置統計圖表 -->
    <div class="col-md-6">
        <div class="card h-100 shadow-sm border-0">
            <div class="card-header d-flex justify-content-between align-items-center bg-white py-3 border-0">
                <span class="fw-bold"><i class="bi bi-pie-chart-fill me-2 text-success"></i>設備位置分佈</span>
            </div>
            <div class="card-body">
                <div class="chart-wrapper" style="position: relative; height:240px; width:100%">
                    <canvas id="locationChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 最近新增設備 -->
<div class="card shadow-sm border-0">
    <div class="card-header d-flex justify-content-between align-items-center bg-white py-3 border-0">
        <span class="fs-5 fw-bold"><i class="bi bi-clock-history me-2 text-warning"></i>最近新增設備 (5筆)</span>
        <a href="/devices" class="btn btn-sm btn-outline-primary">查看所有設備</a>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
                <thead>
                    <tr>
                        <th class="ps-4">IP 位址</th>
                        <th>設備名稱</th>
                        <th>類型</th>
                        <th>位置</th>
                        <th>MAC</th>
                        <th>備註</th>
                        <th class="text-center pe-4" style="width: 130px;">操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for dev in recent_devices %}
                    <tr>
                        <td class="ps-4 fw-bold text-primary">{{ dev[0] }}</td>
                        <td>{{ dev[1] }}</td>
                        <td><span class="badge bg-secondary">{{ dev[2] }}</span></td>
                        <td><span class="badge bg-light text-dark border"><i class="bi bi-geo-alt me-1"></i>{{ dev[3] }}</span></td>
                        <td class="text-monospace text-muted">{{ dev[4] or '-' }}</td>
                        <td class="text-truncate" style="max-width: 220px;" title="{{ dev[5] }}">{{ dev[5] or '-' }}</td>
                        <td class="text-center pe-4">
                            <a href="/edit/{{ dev[0] }}" class="btn btn-sm btn-outline-secondary me-1" title="編輯">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button onclick="confirmDelete('{{ dev[0] }}', '{{ dev[1] }}')" class="btn btn-sm btn-outline-danger" title="刪除">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="7" class="text-center py-4 text-muted">無設備資料</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Modal 確認刪除 -->
<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow" style="border-radius: 16px;">
            <div class="modal-header border-0 pb-0">
                <h5 class="modal-title fw-bold" id="deleteModalLabel"><i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>確認刪除設備</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body py-3">
                確定要刪除設備 <strong id="deleteDeviceName"></strong> (<span id="deleteDeviceIP" class="text-danger fw-bold"></span>) 嗎？此動作無法復原。
            </div>
            <div class="modal-footer border-0 pt-0">
                <button type="button" class="btn btn-light" data-bs-dismiss="modal">取消</button>
                <form id="deleteForm" method="POST" action="">
                    <button type="submit" class="btn btn-danger px-4">確認刪除</button>
                </form>
            </div>
        </div>
    </div>
</div>
"""

DEVICES_TEMPLATE_CONTENT = """
<div class="card shadow-sm border-0">
    <div class="card-header bg-white py-3 border-0">
        <div class="row align-items-center g-3">
            <div class="col-md-4">
                <h4 class="mb-0 fw-bold"><i class="bi bi-list-task me-2 text-primary"></i>設備清單</h4>
            </div>
            <div class="col-md-5">
                <div class="input-group">
                    <span class="input-group-text bg-light border-end-0 text-muted"><i class="bi bi-search"></i></span>
                    <input type="text" id="searchInput" class="form-control bg-light border-start-0" placeholder="輸入關鍵字即時篩選 (IP、名稱、類型、位置、備註)..." onkeyup="filterTable()">
                </div>
            </div>
            <div class="col-md-3 text-md-end">
                <a href="/add" class="btn btn-primary w-100 w-md-auto shadow-sm">
                    <i class="bi bi-plus-circle me-1"></i>新增設備
                </a>
            </div>
        </div>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle" id="devicesTable">
                <thead class="desktop-thead">
                    <tr>
                        <th class="ps-4 sortable" onclick="sortTable(0)" style="cursor:pointer; user-select: none;">IP 位址 <i class="bi bi-arrow-down-up ms-1 text-muted fs-7"></i></th>
                        <th class="sortable" onclick="sortTable(1)" style="cursor:pointer; user-select: none;">設備名稱 <i class="bi bi-arrow-down-up ms-1 text-muted fs-7"></i></th>
                        <th class="sortable" onclick="sortTable(2)" style="cursor:pointer; user-select: none;">類型 <i class="bi bi-arrow-down-up ms-1 text-muted fs-7"></i></th>
                        <th class="sortable" onclick="sortTable(3)" style="cursor:pointer; user-select: none;">位置 <i class="bi bi-arrow-down-up ms-1 text-muted fs-7"></i></th>
                        <th>MAC</th>
                        <th>備註</th>
                        <th class="text-center pe-4" style="width: 180px;">操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for dev in devices %}
                    <tr class="desktop-row">
                        <td class="ps-4 fw-bold text-primary">{{ dev[0] }}</td>
                        <td>{{ dev[1] }}</td>
                        <td><span class="badge bg-secondary">{{ dev[2] }}</span></td>
                        <td><span class="badge bg-light text-dark border"><i class="bi bi-geo-alt me-1 text-muted"></i>{{ dev[3] }}</span></td>
                        <td class="text-monospace text-muted">{{ dev[4] or '-' }}</td>
                        <td class="text-truncate" style="max-width: 250px;" title="{{ dev[5] }}">{{ dev[5] or '-' }}</td>
                        <td class="text-center pe-4">
                            <a href="/edit/{{ dev[0] }}" class="btn btn-sm btn-outline-secondary me-1">
                                <i class="bi bi-pencil-fill me-1"></i><span class="action-text">編輯</span>
                            </a>
                            <button onclick="confirmDelete('{{ dev[0] }}', '{{ dev[1] }}')" class="btn btn-sm btn-outline-danger">
                                <i class="bi bi-trash-fill me-1"></i><span class="action-text">刪除</span>
                            </button>
                        </td>
                    </tr>
                    <tr class="mobile-row d-none">
                        <td colspan="7" class="p-3 border-0">
                            <div class="card shadow-sm border mb-0">
                                <div class="card-body p-3">
                                    <h4 class="fw-bold text-primary mb-2">{{ dev[0] }}</h4>
                                    <div class="mb-2">
                                        <span class="fw-bold">{{ dev[1] }}</span>
                                        <span class="badge bg-secondary ms-2">{{ dev[2] }}</span>
                                    </div>
                                    <div class="mb-3 text-muted">
                                        <i class="bi bi-geo-alt me-1"></i>{{ dev[3] }}
                                    </div>
                                    <div class="d-flex gap-2">
                                        <a href="/edit/{{ dev[0] }}" class="btn btn-sm btn-outline-secondary flex-fill">
                                            <i class="bi bi-pencil-fill me-1"></i>編輯
                                        </a>
                                        <button onclick="confirmDelete('{{ dev[0] }}', '{{ dev[1] }}')" class="btn btn-sm btn-outline-danger flex-fill">
                                            <i class="bi bi-trash-fill me-1"></i>刪除
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="7" class="text-center py-5 text-muted">目前無任何設備資料，請點擊右上角新增！</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Modal 確認刪除 -->
<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow" style="border-radius: 16px;">
            <div class="modal-header border-0 pb-0">
                <h5 class="modal-title fw-bold" id="deleteModalLabel"><i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>確認刪除設備</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body py-3">
                確定要刪除設備 <strong id="deleteDeviceName"></strong> (<span id="deleteDeviceIP" class="text-danger fw-bold"></span>) 嗎？此動作無法復原。
            </div>
            <div class="modal-footer border-0 pt-0">
                <button type="button" class="btn btn-light" data-bs-dismiss="modal">取消</button>
                <form id="deleteForm" method="POST" action="">
                    <button type="submit" class="btn btn-danger px-4">確認刪除</button>
                </form>
            </div>
        </div>
    </div>
</div>
"""

ADD_TEMPLATE_CONTENT = """
<div class="row justify-content-center">
    <div class="col-lg-8 col-md-10">
        <div class="card shadow-sm border-0">
            <div class="card-header bg-white py-3 border-0">
                <h4 class="mb-0 fw-bold text-primary"><i class="bi bi-plus-circle me-2"></i>新增設備</h4>
            </div>
            <div class="card-body p-4">
                <form method="POST" action="/add" class="needs-validation" novalidate>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="ip" class="form-label fw-bold">IP 位址 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="ip" name="ip" value="{{ form_data.get('ip', '') }}" placeholder="例如: 192.60.1.100" required pattern="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$">
                            <div class="invalid-feedback">請輸入有效的 IPv4 位址。</div>
                        </div>
                        <div class="col-md-6">
                            <label for="name" class="form-label fw-bold">設備名稱 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="name" name="name" value="{{ form_data.get('name', '') }}" placeholder="例如: 自然教室AP" required>
                            <div class="invalid-feedback">請輸入設備名稱。</div>
                        </div>
                        <div class="col-md-6">
                            <label for="type" class="form-label fw-bold">設備類型 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="type" name="type" value="{{ form_data.get('type', '') }}" placeholder="例如: AP, Switch, Printer, NAS, VM" required list="typeSuggestions">
                            <datalist id="typeSuggestions">
                                <option value="AP">
                                <option value="Switch">
                                <option value="Printer">
                                <option value="NAS">
                                <option value="VM">
                                <option value="Router">
                                <option value="Camera">
                                <option value="Server">
                                <option value="UPS">
                                <option value="NVR">
                            </datalist>
                            <div class="invalid-feedback">請輸入或選擇設備類型。</div>
                        </div>
                        <div class="col-md-6">
                            <label for="location" class="form-label fw-bold">設備位置 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="location" name="location" value="{{ form_data.get('location', '') }}" placeholder="例如: 機房, 辦公室, 一年級教室" required list="locationSuggestions">
                            <datalist id="locationSuggestions">
                                <option value="機房">
                                <option value="辦公室">
                                <option value="校園">
                                <option value="行政大樓">
                                <option value="教室區">
                            </datalist>
                            <div class="invalid-feedback">請輸入或選擇設備位置。</div>
                        </div>
                        <div class="col-md-12">
                            <label for="mac" class="form-label fw-bold">MAC 位址 (選填)</label>
                            <input type="text" class="form-control" id="mac" name="mac" value="{{ form_data.get('mac', '') }}" placeholder="例如: 00:11:22:33:44:55" pattern="^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$">
                            <div class="invalid-feedback">請輸入有效的 MAC 位址格式 (例如 AA:BB:CC:DD:EE:FF)。</div>
                        </div>
                        <div class="col-md-12">
                            <label for="notes" class="form-label fw-bold">備註</label>
                            <textarea class="form-control mobile-textarea" id="notes" name="notes" rows="3" placeholder="其他設備備註說明...">{{ form_data.get('notes', '') }}</textarea>
                        </div>
                    </div>
                    <hr class="my-4 text-muted">
                    <div class="d-flex flex-wrap justify-content-between">
                        <a href="/devices" class="btn btn-outline-secondary px-4 mobile-full-btn"><i class="bi bi-arrow-left me-1"></i>返回清單</a>
                        <button type="submit" class="btn btn-primary px-5 shadow-sm mobile-full-btn"><i class="bi bi-save me-1"></i>儲存設備</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
"""

EDIT_TEMPLATE_CONTENT = """
<div class="row justify-content-center">
    <div class="col-lg-8 col-md-10">
        <div class="card shadow-sm border-0">
            <div class="card-header bg-white py-3 border-0">
                <h4 class="mb-0 fw-bold text-primary"><i class="bi bi-pencil-square me-2"></i>編輯設備資訊</h4>
            </div>
            <div class="card-body p-4">
                <form method="POST" action="/edit/{{ device[0] }}" class="needs-validation" novalidate>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="ip" class="form-label fw-bold text-muted">IP 位址 (唯讀)</label>
                            <input type="text" class="form-control bg-light" id="ip" name="ip" value="{{ device[0] }}" readonly>
                        </div>
                        <div class="col-md-6">
                            <label for="name" class="form-label fw-bold">設備名稱 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="name" name="name" value="{{ device[1] }}" placeholder="例如: 自然教室AP" required>
                            <div class="invalid-feedback">請輸入設備名稱。</div>
                        </div>
                        <div class="col-md-6">
                            <label for="type" class="form-label fw-bold">設備類型 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="type" name="type" value="{{ device[2] }}" placeholder="例如: AP, Switch, Printer, NAS" required list="typeSuggestions">
                            <datalist id="typeSuggestions">
                                <option value="AP">
                                <option value="Switch">
                                <option value="Printer">
                                <option value="NAS">
                                <option value="VM">
                                <option value="Router">
                                <option value="Camera">
                                <option value="Server">
                                <option value="UPS">
                                <option value="NVR">
                            </datalist>
                            <div class="invalid-feedback">請輸入或選擇設備類型。</div>
                        </div>
                        <div class="col-md-6">
                            <label for="location" class="form-label fw-bold">設備位置 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="location" name="location" value="{{ device[3] }}" placeholder="例如: 機房, 辦公室, 一年級教室" required list="locationSuggestions">
                            <datalist id="locationSuggestions">
                                <option value="機房">
                                <option value="辦公室">
                                <option value="校園">
                                <option value="行政大樓">
                                <option value="教室區">
                            </datalist>
                            <div class="invalid-feedback">請輸入或選擇設備位置。</div>
                        </div>
                        <div class="col-md-12">
                            <label for="mac" class="form-label fw-bold">MAC 位址</label>
                            <input type="text" class="form-control" id="mac" name="mac" value="{{ device[4] or '' }}" placeholder="例如: 00:11:22:33:44:55" pattern="^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$">
                            <div class="invalid-feedback">請輸入有效的 MAC 位址格式 (例如 AA:BB:CC:DD:EE:FF)。</div>
                        </div>
                        <div class="col-md-12">
                            <label for="notes" class="form-label fw-bold">備註</label>
                            <textarea class="form-control mobile-textarea" id="notes" name="notes" rows="3" placeholder="其他設備備註說明...">{{ device[5] or '' }}</textarea>
                        </div>
                    </div>
                    <hr class="my-4 text-muted">
                    <div class="d-flex flex-wrap justify-content-between">
                        <a href="/devices" class="btn btn-outline-secondary px-4 mobile-full-btn"><i class="bi bi-arrow-left me-1"></i>返回清單</a>
                        <button type="submit" class="btn btn-primary px-5 shadow-sm mobile-full-btn"><i class="bi bi-save me-1"></i>儲存修改</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
"""

PING_TEMPLATE_CONTENT = """
<div class="card shadow-sm border-0">
    <div class="card-header bg-white py-3 border-0 d-flex justify-content-between align-items-center">
        <h4 class="mb-0 fw-bold"><i class="bi bi-broadcast me-2 text-primary"></i>設備 Ping 測試</h4>
        <button id="startPingBtn" class="btn btn-primary shadow-sm" onclick="startPingTest()">
            <i class="bi bi-play-fill me-1"></i>開始批次測試
        </button>
    </div>
    <div class="card-body">
        <!-- 進度條區塊 -->
        <div id="pingProgressContainer" class="d-none mb-4 p-3 bg-light" style="border-radius: 12px;">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="fw-bold text-primary" id="progressStatus">正在準備測試...</span>
                <span class="fw-bold text-dark" id="progressPercent">0%</span>
            </div>
            <div class="progress" style="height: 10px; border-radius: 5px;">
                <div id="pingProgressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-success" role="progressbar" style="width: 0%"></div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
                <thead class="desktop-thead">
                    <tr>
                        <th class="ps-4" style="width: 150px;">連線狀態</th>
                        <th>IP 位址</th>
                        <th>設備名稱</th>
                        <th>類型</th>
                        <th>位置</th>
                        <th>備註</th>
                    </tr>
                </thead>
                <tbody id="pingTableBody">
                    {% for dev in devices %}
                    <tr id="row-{{ dev[0] | replace('.', '_') }}" class="desktop-row">
                        <td class="ps-4">
                            <span class="badge bg-secondary status-badge"><i class="bi bi-question-circle me-1"></i>未測試</span>
                        </td>
                        <td class="fw-bold text-primary">{{ dev[0] }}</td>
                        <td>{{ dev[1] }}</td>
                        <td><span class="badge bg-secondary">{{ dev[2] }}</span></td>
                        <td><span class="badge bg-light text-dark border">{{ dev[3] }}</span></td>
                        <td class="text-muted text-truncate" style="max-width: 250px;">{{ dev[5] or '-' }}</td>
                    </tr>
                    <tr id="mobile-row-{{ dev[0] | replace('.', '_') }}" class="mobile-row d-none">
                        <td colspan="6" class="p-3 border-0">
                            <div class="card shadow-sm border mb-0">
                                <div class="card-body p-3">
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <h4 class="fw-bold text-primary mb-0">{{ dev[0] }}</h4>
                                        <span class="badge bg-secondary status-badge-mobile"><i class="bi bi-question-circle me-1"></i>未測試</span>
                                    </div>
                                    <div class="mb-2">
                                        <span class="fw-bold">{{ dev[1] }}</span>
                                        <span class="badge bg-secondary ms-2">{{ dev[2] }}</span>
                                    </div>
                                    <div class="text-muted">
                                        <i class="bi bi-geo-alt me-1"></i>{{ dev[3] }}
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

STATS_TEMPLATE_CONTENT = """
<div class="row g-4 mb-4">
    <!-- 類型統計圖表與清單 -->
    <div class="col-md-6">
        <div class="card h-100 shadow-sm border-0">
            <div class="card-header bg-white py-3 border-0 d-flex align-items-center">
                <i class="bi bi-tag-fill me-2 text-primary fs-5"></i>
                <h5 class="mb-0 fw-bold">設備類型統計</h5>
            </div>
            <div class="card-body">
                <div class="chart-wrapper mb-4" style="position: relative; height:240px; width:100%">
                    <canvas id="typeStatsChart"></canvas>
                </div>
                <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
                    <table class="table table-hover table-striped mb-0">
                        <thead>
                            <tr class="sticky-top bg-light">
                                <th>設備類型</th>
                                <th class="text-end">數量 (台)</th>
                                <th class="text-end">比例</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for dtype, count in type_counts %}
                            <tr>
                                <td><span class="badge bg-secondary">{{ dtype }}</span></td>
                                <td class="text-end fw-bold">{{ count }}</td>
                                <td class="text-end text-muted">{{ "%.1f" | format(count / total_devices * 100) }}%</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 位置統計圖表與清單 -->
    <div class="col-md-6">
        <div class="card h-100 shadow-sm border-0">
            <div class="card-header bg-white py-3 border-0 d-flex align-items-center">
                <i class="bi bi-geo-alt-fill me-2 text-success fs-5"></i>
                <h5 class="mb-0 fw-bold">設備位置統計</h5>
            </div>
            <div class="card-body">
                <div class="chart-wrapper mb-4" style="position: relative; height:240px; width:100%">
                    <canvas id="locStatsChart"></canvas>
                </div>
                <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
                    <table class="table table-hover table-striped mb-0">
                        <thead>
                            <tr class="sticky-top bg-light">
                                <th>位置</th>
                                <th class="text-end">數量 (台)</th>
                                <th class="text-end">比例</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for loc, count in location_counts %}
                            <tr>
                                <td><span class="badge bg-light text-dark border">{{ loc }}</span></td>
                                <td class="text-end fw-bold">{{ count }}</td>
                                <td class="text-end text-muted">{{ "%.1f" | format(count / total_devices * 100) }}%</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- CLI 格式輸出 -->
<div class="card shadow-sm border-0">
    <div class="card-header bg-white py-3 border-0 d-flex align-items-center">
        <h5 class="mb-0 fw-bold text-muted"><i class="bi bi-terminal me-2"></i>CLI 模式輸出預覽 (stats)</h5>
    </div>
    <div class="card-body bg-dark text-light p-3 rounded-bottom" style="border-radius: 0 0 16px 16px;">
        <pre class="mb-0 text-monospace text-success" style="font-size: 0.95rem; line-height: 1.4;">{{ cli_output }}</pre>
    </div>
</div>
"""


def render_page(active_page, child_content, **context):
    """自訂渲染頁面函式，將 child content 插補至 BASE_TEMPLATE 中"""
    full_template = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', child_content)
    
    # 抽取與插入 scripts block
    scripts_content = context.pop('scripts', '')
    full_template = full_template.replace('{% block scripts %}{% endblock %}', scripts_content)
    
    return render_template_string(full_template, active_page=active_page, **context)


# --- Flask 路由與控制器 ---

@app.route('/')
def dashboard_route():
    devices = read_inventory()
    total_devices = len(devices)
    
    type_counts = {}
    location_counts = {}
    
    for row in devices:
        t = row[2].strip() or '未分類'
        l = row[3].strip() or '未分類'
        type_counts[t] = type_counts.get(t, 0) + 1
        location_counts[l] = location_counts.get(l, 0) + 1
        
    type_labels = list(type_counts.keys())
    type_values = list(type_counts.values())
    loc_labels = list(location_counts.keys())
    loc_values = list(location_counts.values())
    
    # 取出最近新增的 5 筆（最後面寫入的 rows）
    recent_devices = devices[-5:][::-1] if total_devices > 0 else []
    
    scripts = f"""
    <script>
        const typeCtx = document.getElementById('typeChart').getContext('2d');
        const locationCtx = document.getElementById('locationChart').getContext('2d');

        const typeLabels = {type_labels};
        const typeData = {type_values};
        const locLabels = {loc_labels};
        const locData = {loc_values};

        const chartColors = [
            '#3b82f6', '#10b981', '#06b6d4', '#f59e0b', '#ef4444',
            '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6', '#64748b'
        ];

        new Chart(typeCtx, {{
            type: 'bar',
            data: {{
                labels: typeLabels,
                datasets: [{{
                    label: '數量 (台)',
                    data: typeData,
                    backgroundColor: chartColors.slice(0, typeLabels.length),
                    borderWidth: 0,
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ stepSize: 1, color: '#64748b' }},
                        grid: {{ color: '#f1f5f9' }}
                    }},
                    x: {{
                        ticks: {{ color: '#64748b' }},
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});

        new Chart(locationCtx, {{
            type: 'doughnut',
            data: {{
                labels: locLabels,
                datasets: [{{
                    data: locData,
                    backgroundColor: chartColors.slice().reverse().slice(0, locLabels.length),
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{ boxWidth: 12, font: {{ family: 'Noto Sans TC' }}, color: '#475569' }}
                    }}
                }}
            }}
        }});

        function confirmDelete(ip, name) {{
            document.getElementById('deleteDeviceName').innerText = name;
            document.getElementById('deleteDeviceIP').innerText = ip;
            document.getElementById('deleteForm').action = '/delete/' + ip;
            var myModal = new bootstrap.Modal(document.getElementById('deleteModal'));
            myModal.show();
        }}
    </script>
    """
    
    return render_page(
        'dashboard', 
        DASHBOARD_TEMPLATE_CONTENT, 
        title='儀表板',
        total_devices=total_devices,
        total_types=len(type_labels),
        total_locations=len(loc_labels),
        recent_devices=recent_devices,
        type_labels=type_labels,
        type_values=type_values,
        loc_labels=loc_labels,
        loc_values=loc_values,
        scripts=scripts
    )

@app.route('/devices')
def devices_route():
    devices = read_inventory()
    
    scripts = """
    <script>
        function filterTable() {
            const input = document.getElementById("searchInput");
            const filter = input.value.toLowerCase();
            const table = document.getElementById("devicesTable");
            const tr = table.getElementsByTagName("tr");

            for (let i = 1; i < tr.length; i++) {
                let match = false;
                const tds = tr[i].getElementsByTagName("td");
                for (let j = 0; j < tds.length - 1; j++) {
                    if (tds[j]) {
                        const textValue = tds[j].textContent || tds[j].innerText;
                        if (textValue.toLowerCase().indexOf(filter) > -1) {
                            match = true;
                            break;
                        }
                    }
                }
                tr[i].style.display = match ? "" : "none";
            }
        }

        let sortDirections = [true, true, true, true];
        function sortTable(colIndex) {
            const table = document.getElementById("devicesTable");
            let switching = true;
            let shouldSwitch = false;
            let i = 0;
            const dir = sortDirections[colIndex] ? "asc" : "desc";
            
            const headers = table.getElementsByTagName("th");
            for (let h = 0; h < headers.length; h++) {
                const icon = headers[h].querySelector("i");
                if (icon) {
                    icon.className = "bi bi-arrow-down-up ms-1 text-muted fs-7";
                }
            }
            
            const currentIcon = headers[colIndex].querySelector("i");
            if (currentIcon) {
                currentIcon.className = dir === "asc" ? "bi bi-arrow-up ms-1 text-primary" : "bi bi-arrow-down ms-1 text-primary";
            }

            while (switching) {
                switching = false;
                const rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {
                    shouldSwitch = false;
                    const x = rows[i].getElementsByTagName("TD")[colIndex];
                    const y = rows[i + 1].getElementsByTagName("TD")[colIndex];
                    
                    let valX = x.textContent || x.innerText;
                    let valY = y.textContent || y.innerText;
                    
                    if (colIndex === 0) { // IP 排序特殊處理
                        const ipToNum = (ip) => ip.split('.').map(num => parseInt(num, 10).toString().padStart(3, '0')).join('');
                        try {
                            valX = ipToNum(valX.trim());
                            valY = ipToNum(valY.trim());
                        } catch(e) {}
                    }

                    if (dir === "asc") {
                        if (valX > valY) {
                            shouldSwitch = true;
                            break;
                        }
                    } else if (dir === "desc") {
                        if (valX < valY) {
                            shouldSwitch = true;
                            break;
                        }
                    }
                }
                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                }
            }
            sortDirections[colIndex] = !sortDirections[colIndex];
        }

        function confirmDelete(ip, name) {
            document.getElementById('deleteDeviceName').innerText = name;
            document.getElementById('deleteDeviceIP').innerText = ip;
            document.getElementById('deleteForm').action = '/delete/' + ip;
            var myModal = new bootstrap.Modal(document.getElementById('deleteModal'));
            myModal.show();
        }
    </script>
    """
    
    return render_page(
        'devices', 
        DEVICES_TEMPLATE_CONTENT, 
        title='設備清單', 
        devices=devices, 
        scripts=scripts
    )

@app.route('/add', methods=['GET', 'POST'])
def add_device_route():
    if request.method == 'POST':
        ip = request.form.get('ip', '').strip()
        name = request.form.get('name', '').strip()
        device_type = request.form.get('type', '').strip()
        location = request.form.get('location', '').strip()
        mac = request.form.get('mac', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not ip or not name or not device_type or not location:
            flash('請填寫所有必填欄位！', 'danger')
            return redirect(url_for('add_device_route'))
            
        data = read_inventory()
        if any(row[0].strip() == ip for row in data):
            flash(f'錯誤：IP「{ip}」已存在於庫存中！', 'danger')
            return render_page(
                'add', 
                ADD_TEMPLATE_CONTENT, 
                title='新增設備', 
                form_data={'ip': ip, 'name': name, 'type': device_type, 'location': location, 'mac': mac, 'notes': notes}
            )
            
        # 新增至列表並儲存
        data.append([ip, name, device_type, location, mac, notes])
        write_inventory(data)
        flash(f'成功新增設備：{ip} ({name})', 'success')
        return redirect(url_for('devices_route'))
        
    return render_page('add', ADD_TEMPLATE_CONTENT, title='新增設備', form_data={})

@app.route('/edit/<ip>', methods=['GET', 'POST'])
def edit_device_route(ip):
    data = read_inventory()
    target_idx = -1
    for idx, row in enumerate(data):
        if row[0].strip() == ip.strip():
            target_idx = idx
            break
            
    if target_idx == -1:
        flash(f'找不到 IP 為「{ip}」的設備。', 'danger')
        return redirect(url_for('devices_route'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        device_type = request.form.get('type', '').strip()
        location = request.form.get('location', '').strip()
        mac = request.form.get('mac', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not name or not device_type or not location:
            flash('請填寫所有必填欄位！', 'danger')
            return redirect(url_for('edit_device_route', ip=ip))
            
        # 更新該項目
        data[target_idx] = [ip, name, device_type, location, mac, notes]
        write_inventory(data)
        flash(f'已成功更新設備資訊：{ip} ({name})', 'success')
        return redirect(url_for('devices_route'))
        
    return render_page(
        'devices', 
        EDIT_TEMPLATE_CONTENT, 
        title='編輯設備', 
        device=data[target_idx]
    )

@app.route('/delete/<ip>', methods=['POST'])
def delete_device_route(ip):
    data = read_inventory()
    new_data = [row for row in data if row[0].strip() != ip.strip()]
    if len(new_data) == len(data):
        flash(f'找不到 IP 為「{ip}」的設備，無法刪除。', 'danger')
    else:
        write_inventory(new_data)
        flash(f'已成功刪除設備：{ip}', 'success')
    return redirect(url_for('devices_route'))

@app.route('/ping')
def ping_route():
    devices = read_inventory()
    
    scripts = """
    <script>
        async function pingSingleDevice(ip) {
            const rowId = 'row-' + ip.replaceAll('.', '_');
            const mRowId = 'mobile-row-' + ip.replaceAll('.', '_');
            const row = document.getElementById(rowId);
            const mRow = document.getElementById(mRowId);
            
            if (!row && !mRow) return;
            
            const badges = [];
            if(row) badges.push(row.querySelector('.status-badge'));
            if(mRow) badges.push(mRow.querySelector('.status-badge-mobile'));
            
            badges.forEach(badge => {
                if(!badge) return;
                badge.className = 'badge bg-warning text-dark ' + (badge.classList.contains('status-badge-mobile') ? 'status-badge-mobile' : 'status-badge');
                badge.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>測試中';
            });
            
            try {
                const response = await fetch('/api/ping?ip=' + encodeURIComponent(ip));
                const data = await response.json();
                
                badges.forEach(badge => {
                    if(!badge) return;
                    const baseClass = badge.classList.contains('status-badge-mobile') ? 'status-badge-mobile' : 'status-badge';
                    if (data.online) {
                        badge.className = 'badge badge-online ' + baseClass;
                        badge.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>在線';
                    } else {
                        badge.className = 'badge badge-offline ' + baseClass;
                        badge.innerHTML = '<i class="bi bi-x-circle-fill me-1"></i>離線';
                    }
                });
                return data.online;
            } catch (e) {
                badges.forEach(badge => {
                    if(!badge) return;
                    const baseClass = badge.classList.contains('status-badge-mobile') ? 'status-badge-mobile' : 'status-badge';
                    badge.className = 'badge badge-offline ' + baseClass;
                    badge.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-1"></i>錯誤';
                });
                return false;
            }
        }

        async function startPingTest() {
            const btn = document.getElementById('startPingBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>測試進行中';
            
            const progressContainer = document.getElementById('pingProgressContainer');
            const progressBar = document.getElementById('pingProgressBar');
            const progressPercent = document.getElementById('progressPercent');
            const progressStatus = document.getElementById('progressStatus');
            
            progressContainer.classList.remove('d-none');
            progressBar.style.width = '0%';
            progressPercent.innerText = '0%';
            progressStatus.innerText = '正在進行連線檢測...';
            
            const rows = document.querySelectorAll('#pingTableBody tr');
            const ips = [];
            rows.forEach(row => {
                const ip = row.id.replace('row-', '').replaceAll('_', '.');
                ips.push(ip);
            });
            
            if (ips.length === 0) {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-play-fill me-1"></i>開始 Ping 測試';
                return;
            }
            
            let completed = 0;
            let onlineCount = 0;
            const limit = 8; // 限制前端發起併發請求數
            const queue = [...ips];
            const activePromises = [];
            
            const runNext = async () => {
                if (queue.length === 0) return;
                const ip = queue.shift();
                const p = pingSingleDevice(ip).then(isOnline => {
                    completed++;
                    if (isOnline) onlineCount++;
                    const pct = Math.round((completed / ips.length) * 100);
                    progressBar.style.width = pct + '%';
                    progressPercent.innerText = pct + '%';
                    progressStatus.innerText = `檢測中: ${completed} / ${ips.length} (在線: ${onlineCount}, 離線: ${completed - onlineCount})`;
                });
                
                activePromises.push(p);
                await p;
                activePromises.splice(activePromises.indexOf(p), 1);
                
                if (queue.length > 0) {
                    await runNext();
                }
            };
            
            const workers = [];
            for (let i = 0; i < Math.min(limit, queue.length); i++) {
                workers.push(runNext());
            }
            
            await Promise.all(workers);
            
            progressStatus.innerText = `測試完成！共 ${ips.length} 台設備 (在線: ${onlineCount}, 離線: ${ips.length - onlineCount})`;
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-arrow-clockwise me-1"></i>重新測試';
        }
    </script>
    """
    
    return render_page(
        'ping', 
        PING_TEMPLATE_CONTENT, 
        title='Ping 測試', 
        devices=devices, 
        scripts=scripts
    )

@app.route('/api/ping')
def api_ping():
    ip = request.args.get('ip', '').strip()
    if not ip:
        return jsonify({'error': 'No IP provided'}), 400
    is_online = ping_ip(ip)
    return jsonify({'ip': ip, 'online': is_online})

@app.route('/stats')
def stats_route():
    devices = read_inventory()
    total_devices = len(devices)
    
    type_counts = {}
    location_counts = {}
    
    for row in devices:
        t = row[2].strip() or '未分類'
        l = row[3].strip() or '未分類'
        type_counts[t] = type_counts.get(t, 0) + 1
        location_counts[l] = location_counts.get(l, 0) + 1
        
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_locs = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
    
    type_labels = [item[0] for item in sorted_types]
    type_values = [item[1] for item in sorted_types]
    loc_labels = [item[0] for item in sorted_locs]
    loc_values = [item[1] for item in sorted_locs]
    
    cli_output = get_cli_stats(devices)
    
    scripts = f"""
    <script>
        const typeCtx = document.getElementById('typeStatsChart').getContext('2d');
        const locCtx = document.getElementById('locStatsChart').getContext('2d');

        const typeLabels = {type_labels};
        const typeData = {type_values};
        const locLabels = {loc_labels};
        const locData = {loc_values};

        const chartColors = [
            '#3b82f6', '#10b981', '#06b6d4', '#f59e0b', '#ef4444',
            '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6', '#64748b'
        ];

        new Chart(typeCtx, {{
            type: 'bar',
            data: {{
                labels: typeLabels,
                datasets: [{{
                    label: '數量 (台)',
                    data: typeData,
                    backgroundColor: chartColors.slice(0, typeLabels.length),
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ stepSize: 1, color: '#64748b' }},
                        grid: {{ color: '#f1f5f9' }}
                    }},
                    x: {{
                        ticks: {{ color: '#64748b' }},
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});

        new Chart(locCtx, {{
            type: 'doughnut',
            data: {{
                labels: locLabels,
                datasets: [{{
                    data: locData,
                    backgroundColor: chartColors.slice().reverse().slice(0, locLabels.length),
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{ boxWidth: 12, font: {{ family: 'Noto Sans TC' }}, color: '#475569' }}
                    }}
                }}
            }}
        }});
    </script>
    """
    
    return render_page(
        'stats',
        STATS_TEMPLATE_CONTENT,
        title='統計報表',
        total_devices=total_devices,
        type_counts=sorted_types,
        location_counts=sorted_locs,
        type_labels=type_labels,
        type_values=type_values,
        loc_labels=loc_labels,
        loc_values=loc_values,
        cli_output=cli_output,
        scripts=scripts
    )




PORTPAGE_TEMPLATE_CONTENT = """
<div class="row justify-content-center">
    <div class="col-lg-8 col-md-10">
        <div class="card shadow-sm border-0">
            <div class="card-header bg-white py-3 border-0">
                <h4 class="mb-0 fw-bold text-primary"><i class="bi bi-shield-check me-2"></i>IP Port 掃描</h4>
            </div>
            <div class="card-body p-4">
                <p class="text-muted">輸入學校網段 (192.60.1.x) 的 IP 位址，掃描常見服務埠狀態。</p>
                <form method="POST" action="/portscan" class="needs-validation" novalidate>
                    <div class="input-group input-group-lg mb-3">
                        <span class="input-group-text bg-light"><i class="bi bi-hdd-network"></i></span>
                        <input type="text" class="form-control" id="target_ip" name="target_ip"
                               value="{{ target_ip or '' }}" placeholder="例如: 192.60.1.127" required
                               pattern="^192\.60\.1\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$">
                        <button class="btn btn-primary px-4" type="submit" id="scanBtn">
                            <i class="bi bi-search me-1"></i>開始掃描
                        </button>
                    </div>
                    <div class="invalid-feedback">請輸入 192.60.1.x 格式的 IP 位址</div>
                </form>

                {% if scan_results is defined and scan_results %}
                <hr>
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0">
                        <i class="bi bi-check-circle-fill text-success me-1"></i>
                        {{ target_ip }} 掃描結果
                    </h5>
                    {% if device_mac %}
                    <span class="badge bg-dark fs-6"><i class="bi bi-ethernet me-1"></i>{{ device_mac }}</span>
                    {% endif %}
                    <span class="badge bg-success fs-6">{{ open_count }} 個埠開啟</span>
                </div>

                <!-- 桌機版表格 -->
                <div class="table-responsive d-none d-md-block">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Port</th>
                                <th>服務名稱</th>
                                <th class="text-center">狀態</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for r in scan_results %}
                            <tr>
                                <td class="fw-bold text-monospace">{{ r.port }}</td>
                                <td>{{ r.name }}</td>
                                <td class="text-center">
                                    {% if r.status == 'open' %}
                                    <span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>開啟</span>
                                    {% else %}
                                    <span class="badge bg-light text-muted border">關閉</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <!-- 手機版卡片 -->
                <div class="d-md-none">
                    {% for r in scan_results %}
                    <div class="card shadow-sm border mb-2">
                        <div class="card-body p-3 d-flex justify-content-between align-items-center">
                            <div>
                                <span class="fw-bold text-monospace fs-5">{{ r.port }}</span>
                                <span class="text-muted ms-2">{{ r.name }}</span>
                            </div>
                            <div>
                                {% if r.status == 'open' %}
                                <span class="badge bg-success fs-6">✅ 開啟</span>
                                {% else %}
                                <span class="badge bg-light text-muted border">❌ 關閉</span>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                    <div class="text-center mt-3">
                        <span class="badge bg-success fs-6">{{ open_count }} 個埠開啟</span>
                    </div>
                </div>
                {% elif scanning %}
                <div class="text-center py-4">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">掃描中...</span>
                    </div>
                    <p class="text-muted">正在掃描 {{ target_ip }} 的 22 個常見埠，請稍候...</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
"""

import os

@app.route('/networkmap')
def networkmap_route():
    map_path = os.path.join(os.path.dirname(__file__), 'network_map.html')
    try:
        with open(map_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return '<h1>404 — 網路拓撲圖尚未建立</h1>', 404


@app.route('/portscan', methods=['GET', 'POST'])
def portscan_route():
    # 讀取設備清單，找出 IP 對應的 MAC
    devices = read_inventory()
    device_macs = {row[0]: row[4] for row in devices if len(row) > 4}
    
    if request.method == 'POST':
        target_ip = request.form.get('target_ip', '').strip()
        
        if not is_school_ip(target_ip):
            flash('只允許掃描學校內部網段 (192.60.1.0/24) 的 IP 位址', 'error')
            return render_page('portscan', PORTPAGE_TEMPLATE_CONTENT, title='Port 掃描', target_ip=target_ip, scan_results=None, open_count=0, device_mac='')
        
        scan_results = scan_ports(target_ip)
        open_count = sum(1 for r in scan_results if r['status'] == 'open')
        device_mac = device_macs.get(target_ip, '')
        
        return render_page('portscan', PORTPAGE_TEMPLATE_CONTENT, title=f'{target_ip} Port 掃描',
                           target_ip=target_ip, scan_results=scan_results, open_count=open_count, device_mac=device_mac)
    
    return render_page('portscan', PORTPAGE_TEMPLATE_CONTENT, title='Port 掃描', target_ip='', scan_results=None, open_count=0, device_mac='')


# --- 應用程式入口 ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
