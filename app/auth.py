from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.config import settings

router = APIRouter()

def get_login_form(error: str = "") -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Вход в админку</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .form-container {{ max-width: 400px; margin: 0 auto; }}
            input[type="password"] {{ 
                width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; 
            }}
            button {{ 
                width: 100%; padding: 10px; background: #007bff; color: white; border: none; 
                border-radius: 4px; cursor: pointer; 
            }}
            .error {{ color: red; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>🔐 Вход в админку</h2>
            <form method="post">
                <input type="password" name="password" placeholder="Введите секретный ключ" required>
                <button type="submit">Войти</button>
            </form>
            <div class="error">{error}</div>
        </div>
    </body>
    </html>
    """

@router.get("/login", response_class=HTMLResponse)
def show_login():
    return get_login_form()

@router.post("/login")
def login(password: str = Form(...)):
    print(f"Пытаемся залогиниться с паролем: {password}")
    print(f"А надо {settings.ADMIN_API_KEY}")
    if password == settings.ADMIN_API_KEY:
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="auth",
            value="authenticated",
            httponly=True,
            max_age=3600,
            samesite="lax"
        )
        return response
    else:
        return HTMLResponse(get_login_form("❌ Неверный ключ. Попробуйте снова."), status_code=401)

def require_auth(request: Request):
    """Проверяет аутентификацию"""
    if request.cookies.get("auth") != "authenticated":
        return RedirectResponse("/login")
    return None