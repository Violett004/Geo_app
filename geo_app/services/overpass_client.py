"""
Klient Overpass API - Implementacja dla OpenStreetMap
"""
import requests
import time
from typing import Dict, Any, Optional
from config.api_config import APIConfigManager
from services.base_api_client import BaseAPIClient, APIRequest, APIResponse
from utils.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class OverpassAPIClient(BaseAPIClient):
    """
    Klient do komunikacji z Overpass API
    ma pobierac dane z OpenStreetMap albo z Open-Meteo
    """
    
    def __init__(self, timeout: int = 30):
        """
        Inicjalizuj klient Overpass
        
        Args:
            timeout: Timeout dla requestów w sekundach
        """
        self.timeout = timeout
        self.config = APIConfigManager.get_api_config("overpass")
        self.request_count = 0
        self.last_request_time = None
    
    def execute_request(self, api_request: APIRequest) -> APIResponse:
        """
        Wykonaj żądanie do Overpass API
        
        Args:
            api_request: Żądanie API
            
        Returns:
            APIResponse: Odpowiedź z API
        """
        logger.info(f"Wysyłanie żądania do Overpass: {api_request.endpoint}")
        logger.debug(f"URL: {api_request.url}, Dane: {api_request.data}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                url=api_request.url,
                headers=api_request.headers or {},
                data=api_request.data or api_request.params,
                timeout=self.timeout
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Zapisuje krótki fragment odpowiedzi
            response_data = {"raw_response": response.text[:500]}  # Przechowaj część odpowiedzi
            
            api_response = APIResponse(
                status_code=response.status_code,
                data=response_data,
                headers=dict(response.headers),
                request=api_request,
                response_time_ms=response_time
            )
            
            self.request_count += 1
            self.last_request_time = time.time()
            
            if api_response.is_success:
                logger.info(f"Żądanie Overpass powiodło się: {response.status_code}, czas: {response_time:.2f}ms")
            else:
                logger.warning(f"Żądanie Overpass zwróciło błąd: {response.status_code}")
            
            return api_response
            
        except requests.Timeout:
            error_msg = f"Timeout przy żądaniu Overpass (>{self.timeout}s)"
            logger.error(error_msg)
            return APIResponse(
                status_code=408,
                data={},
                headers={},
                request=api_request,
                response_time_ms=(time.time() - start_time) * 1000,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Błąd przy żądaniu Overpass: {str(e)}"
            logger.error(error_msg)
            return APIResponse(
                status_code=500,
                data={},
                headers={},
                request=api_request,
                response_time_ms=(time.time() - start_time) * 1000,
                error=error_msg
            )
    
    def is_available(self) -> bool:
        """Sprawdź dostępność Overpass API"""
        try:
            response = requests.head(
                "https://overpass-api.de/api/interpreter",
                timeout=5
            )
            available = response.status_code < 500
            logger.info(f"Overpass dostępny: {available}")
            return available
        except Exception as e:
            logger.warning(f"Overpass niedostępny: {e}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Pobierz informację o limitach Overpass"""
        return {
            "api": "Overpass",
            "request_count": self.request_count,
            "last_request": self.last_request_time,
            "status": "available" if self.is_available() else "unavailable"
        }
    
    def search_parks(self) -> APIResponse:
        """
        Szukaj atrakcji turystycznych
        
        Returns:
            APIResponse: Odpowiedź z wynikami
        """
        endpoint_config = APIConfigManager.get_endpoint_config("overpass", "parks_search")
        
        api_request = APIRequest(
            api_name="Overpass",
            endpoint="parks_search",
            method="POST",
            url=endpoint_config.url,
            headers=endpoint_config.headers,
            data=endpoint_config.params.get("data") if endpoint_config.params else ""
        )
        
        return self.execute_request(api_request)
    
    def search_protected_areas(self) -> APIResponse:
        """
        Szukaj obszarów chronionych
        
        Returns:
            APIResponse: Odpowiedź z wynikami
        """
        endpoint_config = APIConfigManager.get_endpoint_config("overpass", "national_parks")
        
        api_request = APIRequest(
            api_name="Overpass",
            endpoint="national_parks",
            method="POST",
            url=endpoint_config.url,
            headers=endpoint_config.headers,
            data=endpoint_config.params.get("data") if endpoint_config.params else ""
        )
        
        return self.execute_request(api_request)
