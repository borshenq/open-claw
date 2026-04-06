import os
import shutil
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, database, auth, email_utils

# Resolve paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(docs_url="/api/docs", redoc_url="/api/redoc")

# Mount static files and templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request=request, name="login.html", 
            context={"title": "登入", "error": "使用者名稱或密碼錯誤"}
        )
    
    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
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
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("Reporter"),
    db: Session = Depends(database.get_db)
):
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
    item_name: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="請先登入")

    image_url = None
    if image and image.filename:
        try:
            file_ext = os.path.splitext(image.filename)[1]
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
    
    return RedirectResponse(url=f"/report/{new_report.id}", status_code=303)

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
    
    logs = sorted(report.logs, key=lambda x: x.updated_at, reverse=True)
    
    return templates.TemplateResponse(
        request=request, name="detail.html", context={
            "title": f"報修單 #{report.id}",
            "report": report,
            "logs": logs,
            "user": current_user
        }
    )

@app.post("/report/{report_id}/log")
async def add_log(
    background_tasks: BackgroundTasks,
    report_id: int,
    note: str = Form(...),
    status: str = Form(...),
    current_user: models.User = Depends(auth.is_technician),
    db: Session = Depends(database.get_db)
):
    report = db.query(models.RepairRequest).filter(models.RepairRequest.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="找不到該報修單")
    
    report.status = status
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
