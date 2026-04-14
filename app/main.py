import os
import shutil
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import io
import csv
from . import models, database, auth, email_utils, telegram_utils

# Resolve paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

# --- 基礎速率限制器 (Simple Rate Limiter) ---
# 儲存每個 IP 的請求紀錄： { ip: [timestamp1, timestamp2, ...] }
rate_limit_records = defaultdict(list)

def check_rate_limit(ip: str, limit: int = 5, window: int = 60):
    """檢查該 IP 在指定秒數 (window) 內是否超過請求限制 (limit)"""
    now = time.time()
    # 移除超過視窗期的紀錄
    rate_limit_records[ip] = [t for t in rate_limit_records[ip] if now - t < window]
    if len(rate_limit_records[ip]) >= limit:
        return False
    rate_limit_records[ip].append(now)
    return True

# --- 安全標頭中間件 ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
        # 移除或覆蓋伺服器資訊
        response.headers["Server"] = "Hidden"
        return response

app = FastAPI(docs_url="/api/docs", redoc_url="/api/redoc")

# 加入中間件
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"]) # 正式環境應限制為具體域名

# Mount static files and templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

import re

def is_valid_email(email: str):
    """檢查 Email 格式是否正確"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def is_strong_password(password: str):
    """檢查密碼強度：至少 8 字元，包含字母與數字"""
    if len(password) < 8:
        return False
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        return False
    return True

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"title": "首頁", "user": current_user}
    )

@app.get("/docs", response_class=HTMLResponse)
async def docs(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    return templates.TemplateResponse(
        request=request, name="docs.html", context={"title": "說明文件", "user": current_user}
    )

@app.get("/architecture", response_class=HTMLResponse)
async def architecture(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    return templates.TemplateResponse(
        request=request, name="architecture.html", context={"title": "系統架構", "user": current_user}
    )

@app.get("/database", response_class=HTMLResponse)
async def database_docs(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    return templates.TemplateResponse(
        request=request, name="database_docs.html", context={"title": "資料庫說明", "user": current_user}
    )

@app.get("/maintenance", response_class=HTMLResponse)
async def maintenance(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    return templates.TemplateResponse(
        request=request, name="maintenance.html", context={"title": "系統維護", "user": current_user}
    )

# --- Auth Routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"title": "登入"})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(..., max_length=50),
    password: str = Form(..., max_length=100),
    db: Session = Depends(database.get_db)
):
    # 安全性強化：速率限制 (每分鐘 5 次)
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
         return templates.TemplateResponse(
            request=request, name="login.html", 
            context={"title": "登入", "error": "嘗試次數過多，請稍後再試。"}
        )

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request=request, name="login.html", 
            context={"title": "登入", "error": "使用者名稱或密碼錯誤"}
        )
    
    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    # 強化安全性：加入 samesite="lax"，防止 CSRF 攻擊
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        samesite="lax",
        secure=False  # 若在正式環境使用 HTTPS，請改為 True
    )
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={"title": "註冊"})

@app.post("/register")
async def register(
    request: Request,
    username: str = Form(..., max_length=50),
    email: str = Form(..., max_length=100),
    password: str = Form(..., max_length=100),
    role: str = Form("Reporter", max_length=20),
    db: Session = Depends(database.get_db)
):
    # 安全性強化：速率限制 (每分鐘 5 次)
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
         return templates.TemplateResponse(
            request=request, name="register.html", 
            context={"title": "註冊", "error": "操作過於頻繁，請稍後再試。"}
        )

    # 安全性強化：格式驗證
    if not is_valid_email(email):
        return templates.TemplateResponse(
            request=request, name="register.html", 
            context={"title": "註冊", "error": "電子郵件格式不正確。"}
        )
    
    if not is_strong_password(password):
        return templates.TemplateResponse(
            request=request, name="register.html", 
            context={"title": "註冊", "error": "密碼太弱。請至少設定 8 個字元，並包含英文與數字。"}
        )

    if db.query(models.User).filter(models.User.username == username).first():
        return templates.TemplateResponse(
            request=request, name="register.html", 
            context={"title": "註冊", "error": "使用者名稱已存在"}
        )
    
    new_user = models.User(
        username=username,
        email=email,
        hashed_password=auth.get_password_hash(password),
        role=role
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# --- Repair Routes ---

@app.get("/report", response_class=HTMLResponse)
async def report_form(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request, name="report.html", context={"title": "新報修單", "user": current_user}
    )

@app.post("/report")
async def submit_report(
    background_tasks: BackgroundTasks,
    request: Request,
    item_name: str = Form(..., max_length=100),
    location: str = Form(..., max_length=200),
    description: str = Form(..., max_length=2000),
    priority: str = Form("Normal", max_length=20),
    category: str = Form("General", max_length=30),
    image: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="請先登入")

    image_url = None
    if image and image.filename:
        # 安全性強化：限制副檔名，防止惡意腳本上傳
        ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
        file_ext = os.path.splitext(image.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
             raise HTTPException(status_code=400, detail="不支援的檔案格式。只允許圖片檔 (.jpg, .png, .gif)")

        # 安全性強化：檢查檔案真實屬性 (MIME Type)
        if not image.content_type.startswith("image/"):
             raise HTTPException(status_code=400, detail="不支援的檔案格式。這看起來不像是圖片檔。")

        try:
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Use async read to avoid blocking
            content = await image.read()
            if content:
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
                image_url = f"/static/uploads/{filename}"
        except Exception as e:
            print(f"Error saving image: {e}")
            # Optionally fallback or ignore image error to allow report submission

    new_report = models.RepairRequest(
        item_name=item_name,
        location=location,
        description=description,
        priority=priority,
        category=category,
        image_url=image_url,
        reporter_id=current_user.id
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # Send email notification
    background_tasks.add_task(
        email_utils.send_report_confirmation, current_user.email, item_name, new_report.id
    )
    
    # 發送 Telegram 通知
    tg_message = telegram_utils.format_report_message(
        new_report.id, item_name, location, priority, current_user.username
    )
    background_tasks.add_task(telegram_utils.send_telegram_notification, tg_message)
    
    return RedirectResponse(url=f"/report/{new_report.id}", status_code=303)

@app.get("/api/stats")
async def get_stats(current_user: models.User = Depends(auth.is_technician), db: Session = Depends(database.get_db)):
    """獲取報修統計數據 (僅限技術員)"""
    from sqlalchemy import func
    
    # 1. 狀態統計
    status_stats = db.query(models.RepairRequest.status, func.count(models.RepairRequest.id)).group_by(models.RepairRequest.status).all()
    
    # 2. 類別統計
    category_stats = db.query(models.RepairRequest.category, func.count(models.RepairRequest.id)).group_by(models.RepairRequest.category).all()
    
    return {
        "status": dict(status_stats),
        "category": dict(category_stats)
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # If technician, see everything. If reporter, see only own.
    if current_user.role == "Technician":
        reports = db.query(models.RepairRequest).order_by(models.RepairRequest.created_at.desc()).all()
    else:
        reports = db.query(models.RepairRequest).filter(models.RepairRequest.reporter_id == current_user.id).order_by(models.RepairRequest.created_at.desc()).all()
        
    return templates.TemplateResponse(
        request=request, name="dashboard.html", 
        context={"title": "儀表板", "reports": reports, "user": current_user}
    )

@app.get("/report/{report_id}", response_class=HTMLResponse)
async def report_detail(request: Request, report_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    report = db.query(models.RepairRequest).filter(models.RepairRequest.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="找不到該報修單")
    
    # Check permission
    if current_user.role != "Technician" and report.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="權限不足")
    
    technicians = db.query(models.User).filter(models.User.role == "Technician").all()
    logs = sorted(report.logs, key=lambda x: x.updated_at, reverse=True)
    
    return templates.TemplateResponse(
        request=request, name="detail.html", context={
            "title": f"報修單 #{report.id}",
            "report": report,
            "logs": logs,
            "user": current_user,
            "technicians": technicians
        }
    )

@app.post("/report/{report_id}/log")
async def add_log(
    background_tasks: BackgroundTasks,
    report_id: int,
    note: str = Form(...),
    status: str = Form(...),
    estimated_completion_at: Optional[str] = Form(None),
    current_user: models.User = Depends(auth.is_technician),
    db: Session = Depends(database.get_db)
):
    report = db.query(models.RepairRequest).filter(models.RepairRequest.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="找不到該報修單")
    
    report.status = status
    if estimated_completion_at:
        try:
            # HTML datetime-local uses 'T' separator
            report.estimated_completion_at = datetime.fromisoformat(estimated_completion_at.replace("Z", ""))
        except ValueError:
            pass

    new_log = models.RepairLog(request_id=report_id, note=note)
    db.add(new_log)
    db.commit()
    
    # Send status update email to reporter
    if report.reporter and report.reporter.email:
        background_tasks.add_task(
            email_utils.send_status_update, 
            report.reporter.email, report.item_name, report.id, status, note
        )
    
    return RedirectResponse(url=f"/report/{report_id}", status_code=303)

@app.post("/report/{report_id}/assign")
async def assign_technician(
    report_id: int,
    assigned_to_id: int = Form(...),
    current_user: models.User = Depends(auth.is_technician),
    db: Session = Depends(database.get_db)
):
    report = db.query(models.RepairRequest).filter(models.RepairRequest.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="找不到該報修單")
    
    report.assigned_to_id = assigned_to_id
    db.commit()
    return RedirectResponse(url=f"/report/{report_id}", status_code=303)

@app.post("/report/{report_id}/feedback")
async def submit_feedback(
    report_id: int,
    rating: int = Form(...),
    feedback: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    report = db.query(models.RepairRequest).filter(models.RepairRequest.id == report_id).first()
    if not report or report.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="權限不足或找不到報修單")
    
    report.rating = rating
    report.feedback = feedback
    db.commit()
    return RedirectResponse(url=f"/report/{report_id}", status_code=303)

@app.get("/export/excel")
async def export_excel(current_user: models.User = Depends(auth.is_technician), db: Session = Depends(database.get_db)):
    import pandas as pd
    from io import BytesIO
    
    reports = db.query(models.RepairRequest).all()
    
    data = []
    for r in reports:
        data.append({
            "編號": r.id,
            "物品名稱": r.item_name,
            "地點": r.location,
            "狀態": r.status,
            "優先度": r.priority,
            "類別": r.category,
            "報修人": r.reporter.username if r.reporter else "未知",
            "負責英雄": r.assigned_to.username if r.assigned_to else "未指派",
            "建立時間": r.created_at.replace(tzinfo=None), # 移除時區資訊以便 Excel 讀取
            "預計完成": r.estimated_completion_at.replace(tzinfo=None) if r.estimated_completion_at else None,
            "評分": r.rating,
            "意見回饋": r.feedback
        })
    
    df = pd.DataFrame(data)
    
    # 建立記憶體中的 Excel 檔案
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='報修紀錄')
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=repair_reports.xlsx"}
    )
