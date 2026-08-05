"""
Walidacja danych
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class BoundingBox(BaseModel):
    """Bounding Box dla obszaru"""
    minx: float = Field(..., description="Minimalna długość geograficzna")
    miny: float = Field(..., description="Minimalna szerokość geograficzna")
    maxx: float = Field(..., description="Maksymalna długość geograficzna")
    maxy: float = Field(..., description="Maksymalna szerokość geograficzna")


class PackageResponse(BaseModel):
    """Schemat odpowiedzi dla pakietu"""
    id: str = Field(..., description="ID pakietu")
    created_at: datetime = Field(..., description="Data utworzenia")
    region: str = Field(..., description="Region")
    source: str = Field(..., description="Źródło danych")
    file_path: Optional[str] = Field(None, description="Ścieżka do pliku")
    item_count: int = Field(default=0, description="Liczba elementów")
    bbox: Optional[Dict[str, float]] = Field(None, description="Bounding box")
    status: str = Field(..., description="Status pakietu")
    
    class Config:
        from_attributes = True


class APIRequestLog(BaseModel):
    """Schemat logu requestu API"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    api_name: str = Field(..., description="Nazwa API")
    endpoint: str = Field(..., description="Endpoint")
    method: str = Field(..., description="Metoda HTTP")
    url: str = Field(..., description="Pełny URL")
    status_code: Optional[int] = Field(None, description="Kod statusu HTTP")
    response_time_ms: float = Field(..., description="Czas odpowiedzi w ms")
    error: Optional[str] = Field(None, description="Błąd jeśli wystąpił")


class HealthCheckResponse(BaseModel):
    """Schemat odpowiedzi dla healthchecka"""
    status: str = Field(..., description="Status systemu")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Wersja aplikacji")
