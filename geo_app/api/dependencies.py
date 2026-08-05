"""
Zależności dla API endpoints
"""
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config.settings import settings
from repositories import PackageRepository
from fastapi import Request, HTTPException, Depends
from repositories.user_repository import UserRepository

# połączenie z bazą
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Tworzy tabele bazy
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency do injection sesji bazy danych
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_package_repository(db: Session = None) -> PackageRepository:
    """
    Dependency do injection repozytorium
    """
    if db is None:
        db = SessionLocal()
    return PackageRepository(db)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Dependency zwracająca aktualnie zalogowanego użytkownika (po ciasteczku `auth_session`).
    Jeśli brak zalogowania, podnosi HTTPException 401.
    """
    session_username = request.cookies.get("auth_session")
    # Dopuszczamy też żądania, które podają Authorization: Bearer <username> (proste, kompatybilne z istniejącym frontem)
    if not session_username:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            session_username = auth_header.split(" ", 1)[1].strip()

    if not session_username:
        raise HTTPException(status_code=401, detail="Wymagane logowanie")

    user_repo = UserRepository(db)
    user = user_repo.get_user_by_username(session_username)
    if not user:
        raise HTTPException(status_code=401, detail="Nieprawidłowa sesja użytkownika")
    return user
