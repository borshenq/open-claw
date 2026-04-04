import os
from typing import List
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM = os.getenv("MAIL_FROM", "repair-system@school.edu"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_report_confirmation(email: str, item_name: str, report_id: int):
    # If credentials are not set, we just log instead of failing
    if not conf.MAIL_USERNAME:
        print(f"DEBUG: 報修申請確認信將發送至 {email} (編號: #{report_id})")
        return

    html = f"""
    <p>您好，</p>
    <p>我們已收到您對 <b>{item_name}</b> 的報修申請（編號：#{report_id}）。</p>
    <p>我們將持續更新維修進度。</p>
    <br>
    <p>祝好，<br>維修團隊</p>
    """

    message = MessageSchema(
        subject=f"報修申請已受理：#{report_id}",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_status_update(email: str, item_name: str, report_id: int, status: str, note: str):
    if not conf.MAIL_USERNAME:
        # Translate status values for debug print as well
        z_status = '處理中' if status == 'Pending' else '維修中' if status == 'In Progress' else '已完成' if status == 'Completed' else status
        print(f"DEBUG: #{report_id} 狀態更新郵件 ({z_status}) 發送至 {email}")
        return
    
    z_status = '處理中' if status == 'Pending' else '維修中' if status == 'In Progress' else '已完成' if status == 'Completed' else status

    html = f"""
    <p>您好，</p>
    <p>您的 <b>{item_name}</b> 報修申請（編號：#{report_id}）狀態已更新。</p>
    <p><b>最新狀態：</b> {z_status}</p>
    <p><b>進度備註：</b> {note}</p>
    <br>
    <p>祝好，<br>維修團隊</p>
    """

    message = MessageSchema(
        subject=f"報修進度更新通知：#{report_id}",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
