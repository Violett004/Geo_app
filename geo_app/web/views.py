import os
import json
from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends, responses
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from api.dependencies import get_db
from repositories.user_repository import UserRepository
from repositories import PackageRepository
from config.settings import settings
from utils.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)
views_router = APIRouter()

templates = Jinja2Templates(directory=settings.templates_dir)
ANALYTICS_LOG_FILE = os.path.join(settings.data_output_dir, "analytics_logs.json")


# --- SYSTEM TELEMETRII (LOGI ODWIEDZIN) ---

def _log_user_visit(request: Request, page_name: str):
    """Natywny system telemetrii - rejestrowanie unikalnych zdarzeń"""
    user_id = request.cookies.get("user_tracker_id")
    log_entry = {
        "user_id": user_id,
        "page": page_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.client.host if request.client else "127.0.0.1"
    }
    
    logs = []
    if os.path.exists(ANALYTICS_LOG_FILE):
        try:
            with open(ANALYTICS_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            pass
            
    logs.append(log_entry)
    try:
        with open(ANALYTICS_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Błąd zapisu logów analitycznych: {e}")


def get_current_user(request: Request, db: Session):
    """Sprawdzenie, czy użytkownik jest zalogowany po ciasteczku"""
    session_username = request.cookies.get("auth_session")
    if not session_username:
        return None
    repo = UserRepository(db)
    return repo.get_user_by_username(session_username)

@views_router.get("/login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={"user": user, "error": None}
    )

# --- STRONY LOGOWANIA I REJESTRACJI ---
@views_router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    user = repo.authenticate_user(username, password)

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"user": None, "error": "Nieprawidłowa nazwa użytkownika lub hasło!", "active_tab": "login"}
        )

    response = responses.RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="auth_session", value=user.username, max_age=31536000, httponly=True)
    return response


@views_router.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    error = None
    if len(password) < 8:
        error = "Hasło musi mieć co najmniej 8 znaków!"
    elif not any(char.isupper() for char in password):
        error = "Hasło musi zawierać co najmniej jedną wielką literę!"
    elif not any(char.isdigit() or not char.isalnum() for char in password):
        error = "Hasło musi zawierać co najmniej jedną cyfrę lub znak specjalny!"

    repo = UserRepository(db)
    if not error and repo.get_user_by_username(username):
        error = "Nazwa użytkownika jest już zajęta!"
    if not error and repo.get_user_by_email(email):
        error = "Adres e-mail jest już zarejestrowany!"

    if error:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"user": None, "error": error, "active_tab": "register"}
        )

    user = repo.create_user(username, email, password)
    response = responses.RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="auth_session", value=user.username, max_age=31536000, httponly=True)
    return response


@views_router.get("/logout")
async def logout():
    response = responses.RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("auth_session")
    return response


# --- GŁÓWNE PODSTRONY APLIKACJI ---

@views_router.get("/")
async def home_page(request: Request, db: Session = Depends(get_db)):
    _log_user_visit(request, "Strona Główna")
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"user": user}
    )

# @views_router.get("/mapa")
# async def map_page(request: Request, db: Session = Depends(get_db)):
#     _log_user_visit(request, "Mapa Interaktywna")
#     user = get_current_user(request, db)
#     return templates.TemplateResponse("mapa.html", {"request": request, "user": user})
@views_router.get("/mapa")
async def map_page(request: Request, db: Session = Depends(get_db)):
    _log_user_visit(request, "Mapa Interaktywna")
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request, 
        name="mapa.html", 
        context={"user": user}
    )

@views_router.get("/repozytorium")
async def repository_page(request: Request, db: Session = Depends(get_db)):
    _log_user_visit(request, "Repozytorium Danych")
    user = get_current_user(request, db)
    repo = PackageRepository(db)
    packages = repo.get_all()
    return templates.TemplateResponse(
        request=request, 
        name="repozytorium.html", 
        context={"user": user, "packages": packages}
    )

# @views_router.get("/repozytorium")
# async def repository_page(request: Request, db: Session = Depends(get_db)):
#     _log_user_visit(request, "Repozytorium Danych")
#     user = get_current_user(request, db)
    
#     repo = PackageRepository(db)
#     packages = repo.get_all()
    
#     return templates.TemplateResponse("repozytorium.html", {
#         "request": request, 
#         "user": user,
#         "packages": packages
#     })

@views_router.get("/dokumentacja")
async def serve_documentation(request: Request, db: Session = Depends(get_db)):
    _log_user_visit(request, "Dokumentacja")
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request, 
        name="dokumentacja.html", 
        context={"user": user}
    )

@views_router.get("/autorzy")
async def serve_authors(request: Request, db: Session = Depends(get_db)):
    _log_user_visit(request, "O Autorze")
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request, 
        name="autorzy.html", 
        context={"user": user}
    )

# @views_router.get("/dokumentacja")
# async def serve_documentation(request: Request, db: Session = Depends(get_db)):
#     _log_user_visit(request, "Dokumentacja")
#     user = get_current_user(request, db)
#     return templates.TemplateResponse("dokumentacja.html", {"request": request, "user": user})


# @views_router.get("/autorzy")
# async def serve_authors(request: Request, db: Session = Depends(get_db)):
#     _log_user_visit(request, "O Autorze")
#     user = get_current_user(request, db)
#     return templates.TemplateResponse("autorzy.html", {"request": request, "user": user})


# --- TELEMETRIA DLA FRONTENDU ---

@views_router.get("/analytics-stats")
async def get_analytics_stats():
    if not os.path.exists(ANALYTICS_LOG_FILE):
        return {"total_views": 0, "unique_users": 0, "page_distribution": {}}
        
    try:
        with open(ANALYTICS_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
            
        total_views = len(logs)
        unique_users = len(set(log["user_id"] for log in logs if log["user_id"]))
        
        page_dist = {}
        for log in logs:
            page_dist[log["page"]] = page_dist.get(log["page"], 0) + 1
            
        return {
            "total_views": total_views,
            "unique_users": unique_users,
            "page_distribution": page_dist
        }
    except Exception as e:
        return {"error": str(e)}