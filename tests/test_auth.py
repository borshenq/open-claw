from fastapi.testclient import TestClient
from app import auth

def test_home_redirect_to_login(client):
    """測試首頁，未登入應重新導向到登入頁。"""
    response = client.get("/", follow_redirects=False)
    # 由於首頁有 Depends(auth.get_current_user)，未帶 Token 應會拋出錯誤或導向
    # 檢查 app/main.py 發現 auth.get_current_user 若失敗會丟 HTTP 401 或 Redirect
    assert response.status_code in [302, 303, 401]

def test_register_user(client):
    """測試使用者註冊流程。"""
    response = client.post("/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "role": "Reporter"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "登入" in response.text

def test_login_success(client):
    """測試使用者登入並獲取 Cookie。"""
    # 先註冊
    client.post("/register", data={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "correct_password",
        "role": "Reporter"
    })
    
    # 嘗試登入
    response = client.post("/login", data={
        "username": "loginuser",
        "password": "correct_password"
    }, follow_redirects=False)
    
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "access_token" in response.cookies

def test_login_failure(client):
    """測試登入失敗的情境。"""
    response = client.post("/login", data={
        "username": "nonexistent",
        "password": "wrongpassword"
    })
    assert response.status_code == 200 # 登入失敗通常會回傳同一頁並顯示錯誤
    assert "使用者名稱或密碼錯誤" in response.text
