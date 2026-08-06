"""
Abstrakcje dla API clients - Dependency Inversion Principle
Określa interfejs, który muszą implementować wszystkie klienty API
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class APIRequest:
    """Struktura żądania API"""
    api_name: str
    endpoint: str
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuj na słownik dla logowania"""
        return {
            "api_name": self.api_name,
            "endpoint": self.endpoint,
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "params": self.params,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class APIResponse:
    """Struktura odpowiedzi API"""
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str]
    request: APIRequest
    response_time_ms: float
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """Czy odpowiedź jest pomyślna"""
        return 200 <= self.status_code < 300


class BaseAPIClient(ABC):
    """
    Abstrakcyjna klasa bazowa dla wszystkich klientów API
    SOLID: Interface Segregation Principle
    """
    
    @abstractmethod
    def execute_request(self, api_request: APIRequest) -> APIResponse:
        """
        Wykonaj żądanie HTTP
        
        Args:
            api_request: Żądanie do wykonania
            
        Returns:
            APIResponse: Odpowiedź z API
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Sprawdź czy API jest dostępne
        
        Returns:
            bool: True jeśli API odpowiada
        """
        pass
    
    @abstractmethod
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Pobierz status limitów API
        
        Returns:
            Dict z informacją o limitach
        """
        pass
