"""
Fabryka Klientów API (SOLID: Factory Method Pattern)
Umożliwia dynamiczne tworzenie odpowiednich klientów API (GIOŚ, Overpass)
bez bezpośredniego wiązania kodu z konkretnymi klasami
"""
from typing import Dict, Type
from services.base_api_client import BaseAPIClient
# Importujemy zaktualizowanego klienta GIOŚ oraz klienta Overpass
from services.gios_client import GIOSAPIClient
from services.overpass_client import OverpassAPIClient
from utils.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class APIClientFactory:
    """
    Fabryka odpowiedzialna za inicjalizację i dostarczanie 
    odpowiednich klientów API na podstawie nazwy usługi.
    """
    
    # Rejestr dostępnych klientów API (łatwo rozszerzalny o nowe klasy)
    _CLIENTS_REGISTRY: Dict[str, Type[BaseAPIClient]] = {
        "gios": GIOSAPIClient,
        "overpass": OverpassAPIClient
    }
    
    @classmethod
    def create_client(cls, api_name: str, **kwargs) -> BaseAPIClient:
        """
        Tworzy i zwraca instancję klienta dla wybranego API.
        
        Args:
            api_name: Nazwa API ("gios" lub "overpass")
            **kwargs: Dodatkowe parametry przekazywane do konstruktora klienta
            
        Returns:
            BaseAPIClient: Instancja klienta API dziedzicząca po klasie bazowej
        """
        normalized_name = api_name.lower().strip()
        
        if normalized_name == "gbif":
            logger.info("🔄 Żądanie klienta 'gbif' przekierowane na zintegrowany 'gios'.")
            normalized_name = "gios"
            
        client_class = cls._CLIENTS_REGISTRY.get(normalized_name)
        
        if not client_class:
            available = ", ".join(cls._CLIENTS_REGISTRY.keys())
            raise ValueError(
                f"Nieobsługiwany typ API: '{api_name}'. "
                f"Dostępne klienty w systemie: [{available}]"
            )
            
        logger.info(f"⚙️ Fabryka tworzy instancję klienta dla: {client_class.__name__}")
        return client_class(**kwargs)