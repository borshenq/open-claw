import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, database
from dotenv import load_dotenv

load_dotenv()

# Configuration - 安全性強化：強制從環境變數讀取金鑰
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    # 拋出明顯錯誤，防止開發者忘記設定密鑰
    raise RuntimeError("SECRET_KEY is NOT set. Please set it in your .env file.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # 使用 Python 3.12+ 推薦的時區感應 UTC
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    # 使用 Cookie 認證時，需防範 CSRF (建議在 main.py 加入 CSRF 中間件)
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # 支援 Bearer 字首處理
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登入逾時或憑證無效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def is_technician(user: models.User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="請先登入")
    if user.role != "Technician":
        raise HTTPException(status_code=403, detail="權限不足。僅限技術員存取。")
    return user
