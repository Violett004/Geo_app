# """
# Globalne ustawienia aplikacji
# """
# import os
# from typing import Optional
# from pydantic_settings import BaseSettings
# import os
# from pathlib import Path

# # Pobiera główny katalog projektu
# BASE_DIR = Path(__file__).resolve().parent.parent

# # Generuje bezwzględną ścieżkę do bazy (np. C:\semestr6\...\geo_app.db)
# DATABASE_URL = f"sqlite:///{BASE_DIR}/geo_app.db"

# class Settings(BaseSettings):
#     """
#     Globalne ustawienia aplikacji
#     Obsługuje zmienne środowiskowe z pliku .env
#     """
    
#     # Informacje o aplikacji
#     app_name: str = "System Monitoringu Przyrodniczego"
#     app_version: str = "2.0"
    
#     # Baza danych
#     database_url: str = "sqlite:///./data_output/packages.db"
    
#     # Ścieżki
#     data_output_dir: str = "data_output"
#     static_dir: str = "static"
#     templates_dir: str = "templates"
    
#     # Harmonogram
#     schedule_interval_hours: int = 24
    
#     # Logowanie
#     log_level: str = "INFO"
    
#     # CORS
#     cors_origins: list = ["*"]
    
#     # Timeout dla requestów
#     request_timeout: int = 30
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False


# # Globalna instancja ustawień
# settings = Settings()

"""
Globalne ustawienia aplikacji
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Pobiera główny katalog projektu (katalog nadrzędny wobec 'config')
BASE_DIR = Path(__file__).resolve().parent.parent

# Ścieżka bezwzględna do bazy danych SQLite
DB_PATH = BASE_DIR / "geo_app.db"

class Settings(BaseSettings):
    """
    Globalne ustawienia aplikacji
    Obsługuje zmienne środowiskowe z pliku .env
    """
    
    # Informacje o aplikacji
    app_name: str = "System Monitoringu Przyrodniczego"
    app_version: str = "2.0"
    
    # Baza danych - używa wygenerowanej ścieżki bezwzględnej
    database_url: str = f"sqlite:///{DB_PATH}"
    
    # Ścieżki do katalogów w projekcie
    data_output_dir: str = str(BASE_DIR / "data_output")
    static_dir: str = str(BASE_DIR / "static")
    templates_dir: str = str(BASE_DIR / "templates")
    
    # Harmonogram (ETL co 24h)
    schedule_interval_hours: int = 24
    
    # Logowanie
    log_level: str = "INFO"
    
    # CORS - Zezwolenie dla aplikacji Angular na porcie 4200
    cors_origins: list = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:8001"
    ]
    
    # Timeout dla requestów API
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Globalna instancja ustawień
settings = Settings()