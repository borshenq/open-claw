import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_notification(message: str):
    """發送 Telegram 訊息給維修英雄"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram configuration missing. Notification skipped.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def format_report_message(report_id, item_name, location, priority, reporter_name):
    """格式化報修單通知訊息"""
    emoji = "🚨" if priority == "Urgent" else "🔴" if priority == "High" else "🔵"
    return (
        f"<b>{emoji} 新報修通知 #{report_id}</b>\n\n"
        f"<b>物品：</b> {item_name}\n"
        f"<b>地點：</b> {location}\n"
        f"<b>優先度：</b> {priority}\n"
        f"<b>報修人：</b> {reporter_name}\n\n"
        f"<a href='http://192.60.1.107:8000/report/{report_id}'>👉 點我查看詳情並指派英雄</a>"
    )
