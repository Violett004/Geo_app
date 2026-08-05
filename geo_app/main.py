import os
import uuid
from contextlib import asynccontextmanager
from web.views import views_router


from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
from config.settings import settings

from api import router
from api.dependencies import get_db
from repositories.user_repository import UserRepository
from web.views import views_router  # Router widoków HTML
from services.data_pipeline import _trigger_scheduled_processing  # Wydzielony potok ETL
from utils.logger import LoggerFactory
from utils import FileHandler

logger = LoggerFactory.get_logger(__name__)

users_db = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

# Inicjalizacja wymaganych katalogów na serwerze
FileHandler.ensure_directory_exists(settings.data_output_dir)
FileHandler.ensure_directory_exists(settings.templates_dir)
FileHandler.ensure_directory_exists(settings.static_dir)


# --- INICJALIZACJA LIFECYCLE (LIFESPAN i SCHEDULER) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Zarządzanie cyklem życia aplikacji FastAPI.
    Twardy reset struktur bazodanowych SQL i uruchomienie harmonogramu.
    """
    logger.info("Inicjalizacja systemu monitoringu...")
    
    # Automatyczny reset tabel przy starcie
    try:
        from api.dependencies import engine
        from models import Base
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Repozytorium bazodanowe SQL zresetowane pomyślnie.")
    except Exception as e:
        logger.warning(f"Status czyszczenia tabel: {e}")
    
    # Rejestracja cyklicznego zadania w tle (ETL Co 24 godziny)
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _trigger_scheduled_processing,
        'interval',
        hours=settings.schedule_interval_hours
    )
    scheduler.start()
    logger.info(f"Scheduler uruchomiony pomyślnie (interwał: {settings.schedule_interval_hours}h)")
    
    # Pierwsze, synchroniczne wywołanie na starcie
    await _trigger_scheduled_processing()
    
    yield
    
    scheduler.shutdown()
    logger.info("Zamykanie struktur systemu przyrodniczego.")


# STRUKTURA SERWERA FASTAPI

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)
app.include_router(views_router)
# Middleware śledzenia unikalnych sesji
@app.middleware("http")
async def track_user_session(request: Request, call_next):
    user_id = request.cookies.get("user_tracker_id")
    response = await call_next(request)
    
    if not user_id:
        new_id = str(uuid.uuid4())
        response.set_cookie(key="user_tracker_id", value=new_id, max_age=31536000, httponly=True)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(settings.static_dir):
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


# Trasy bazodanowe i API pobierania
app.include_router(router, prefix="/api", tags=["data"])


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Nieprawidłowy login lub hasło")
    resp = JSONResponse(content={"user": {"username": user.username, "email": user.email}})
    resp.set_cookie(key="auth_session", value=user.username, max_age=31536000, httponly=True)
    return resp


@app.post("/api/auth/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    if repo.get_user_by_username(payload.username):
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")
    if repo.get_user_by_email(payload.email):
        raise HTTPException(status_code=400, detail="E-mail już zarejestrowany")
    user = repo.create_user(payload.username, payload.email, payload.password)
    resp = JSONResponse(content={"user": {"username": user.username, "email": user.email}})
    resp.set_cookie(key="auth_session", value=user.username, max_age=31536000, httponly=True)
    return resp

# Trasy widoków HTML oraz telemetria (views.py)
app.include_router(views_router, tags=["views"])


def main_entry():
    import uvicorn
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print("\n ARCHITEKTURA LOGICZNA URUCHOMIONA! Adres: http://127.0.0.1:8001 \n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main_entry()