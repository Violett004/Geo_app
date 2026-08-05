"""
Globalne ustawienia aplikacji
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Globalne ustawienia aplikacji
    Obsługuje zmienne środowiskowe z pliku .env
    """
    
    # Informacje o aplikacji
    app_name: str = "System Monitoringu Przyrodniczego"
    app_version: str = "2.0"
    
    # Baza danych
    database_url: str = "sqlite:///./data_output/packages.db"
    
    # Ścieżki
    data_output_dir: str = "data_output"
    static_dir: str = "static"
    templates_dir: str = "templates"
    
    # Harmonogram
    schedule_interval_hours: int = 24
    
    # Logowanie
    log_level: str = "INFO"
    
    # CORS
    cors_origins: list = ["*"]
    
    # Timeout dla requestów
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Globalna instancja ustawień
settings = Settings()
