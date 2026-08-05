"""
Konfiguracje dla różnych API
Łatwo rozszerzalna struktura dla dodawania nowych API
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class APIEndpointConfig:
    """Konfiguracja pojedynczego endpointa API"""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    timeout: int = 30


class APIConfigManager:
    """
    Zarządca konfiguracji API
    Centralne miejsce do przechowywania i zarządzania konfiguracjami wszystkich API
    """
    # GIOŚ (Główny Inspektorat Ochrony Środowiska)
    GIOS_CONFIG = {
        "base_url": "https://api.gios.gov.pl/pjp-api",
        "endpoints": {
            "all_stations": APIEndpointConfig(
                url="https://api.gios.gov.pl/pjp-api/v1/rest/station/findAll",
                method="GET",
                headers={
                    "User-Agent": "SystemMonitoringuPrzyrodniczego/2.0 (GIOŚ Client)"
                },
                timeout=20
            ),
            "air_index": APIEndpointConfig(
                url="https://api.gios.gov.pl/pjp-api/v1/rest/aqindex/getIndex",
                method="GET",
                timeout=10
            )
        },
        "name": "GIOŚ - Główny Inspektorat Ochrony Środowiska",
        "description": "Dane dotyczące jakości powietrza w Polsce wytwarzane w ramach Państwowego Monitoringu Środowiska"
    }
    
    # # Konfiguracja GBIF
    # GBIF_CONFIG = {
    #     "base_url": "https://api.gbif.org/v1",
    #     "endpoints": {
    #         "occurrence_search": APIEndpointConfig(
    #             url="https://api.gbif.org/v1/occurrence/search",
    #             method="GET",
    #             headers={
    #                 "User-Agent": "SystemInformacjiPrzyrodniczej/2.0 (GBIF Leaflet Client)"
    #             },
    #             params={
    #                 "country": "PL",
    #                 "hasCoordinate": True,
    #                 "limit": 100
    #             },
    #             timeout=30
    #         )
    #     },
    #     "name": "GBIF - Global Biodiversity Information Facility",
    #     "description": "Baza danych obserwacji biologicznych z całego świata"
    # }
    
    # Konfiguracja Overpass
    OVERPASS_CONFIG = {
        "base_url": "https://overpass-api.de/api/interpreter",
        "endpoints": {
            "parks_search": APIEndpointConfig(
                url="https://overpass-api.de/api/interpreter",
                method="POST",
                params={
                    "data": "[bbox:49,14,55,24];(node['tourism'='attraction'];way['tourism'='attraction'];);out geom;"
                },
                timeout=30
            ),
            "national_parks": APIEndpointConfig(
                url="https://overpass-api.de/api/interpreter",
                method="POST",
                params={
                    "data": "[bbox:49,14,55,24];(node['protect_class'];way['protect_class'];);out geom;"
                },
                timeout=30
            )
        },
        "name": "Overpass API - OpenStreetMap",
        "description": "Zaawansowane zapytania na danych OpenStreetMap"
    }
    
    
    @classmethod
    def get_api_config(cls, api_name: str) -> Optional[Dict[str, Any]]:
        """Pobierz konfigurację API po nazwie"""
        api_configs = {
            "gbif": cls.GBIF_CONFIG,
            "overpass": cls.OVERPASS_CONFIG,
        }
        return api_configs.get(api_name.lower())
    
    @classmethod
    def get_endpoint_config(cls, api_name: str, endpoint_name: str) -> Optional[APIEndpointConfig]:
        """Pobierz konfigurację konkretnego endpointa"""
        api_config = cls.get_api_config(api_name)
        if api_config and "endpoints" in api_config:
            return api_config["endpoints"].get(endpoint_name)
        return None
    
    @classmethod
    def list_available_apis(cls) -> Dict[str, str]:
        """Lista dostępnych API"""
        return {
            "gbif": "GBIF - Biodiversity Information Facility",
            "overpass": "Overpass API - OpenStreetMap"
        }

class Settings:
    """Główna konfiguracja aplikacji (wymagana przez main.py)"""
    app_name: str = "System Monitoringu Przyrodniczego"
    app_version: str = "1.0.0"
    database_url: str = "sqlite:///./sql_app.db" 
    
    # Katalogi aplikacji
    data_output_dir: str = "data_output"
    templates_dir: str = "templates"
    static_dir: str = "static"
    
    # Harmonogram i limity
    schedule_interval_hours: int = 24
    gbif_result_limit: int = 100
    
    # CORS
    cors_origins: list = ["*"]

# Inicjalizacja instancji settings, którą importuje main.py
settings = Settings()