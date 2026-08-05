"""
Klient GIOŚ API - Implementacja dla Głównego Inspektoratu Ochrony Środowiska
"""
import requests
import time
from typing import Dict, Any, Optional
from config.api_config import APIConfigManager
from services.base_api_client import BaseAPIClient, APIRequest, APIResponse
from utils.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class GIOSAPIClient(BaseAPIClient):
    """
    Klient do komunikacji z API GIOŚ (Jakość Powietrza w Polsce)
    Pobiera dane o stacjach monitoringu środowiskowego oraz indeksach zanieczyszczeń
    """
    
    def __init__(self, timeout: int = 20):
        """
        Inicjalizuj klient GIOŚ
        
        Args:
            timeout: Timeout dla requestów w sekundach
        """
        self.timeout = timeout
        self.config = APIConfigManager.get_api_config("gios")
        self.request_count = 0
        self.last_request_time = None
    
    def execute_request(self, api_request: APIRequest) -> APIResponse:
        """
        Wykonuje żądanie HTTP GET do API GIOŚ
        
        Args:
            api_request: Obiekt żądania API
            
        Returns:
            APIResponse: Standaryzowana odpowiedź systemu
        """
        logger.info(f"Wysyłanie żądania do GIOŚ: {api_request.endpoint}")
        
        start_time = time.time()
        
        try:
            response = requests.get(
                url=api_request.url,
                headers=api_request.headers or {},
                params=api_request.params,
                timeout=self.timeout
            )
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # GIOŚ zwraca format JSON-LD, robimy go jako standardowy słownik
            response_data = response.json() if response.status_code == 200 else {}
            
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
                logger.info(f"Żądanie GIOŚ powiodło się: {response.status_code}, czas: {response_time:.2f}ms")
            else:
                logger.warning(f"Żądanie GIOŚ zwróciło błąd statusu: {response.status_code}")
            
            return api_response
            
        except requests.Timeout:
            error_msg = f"Przekroczono limit czasu (Timeout) żądania GIOŚ (>{self.timeout}s)"
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
            error_msg = f"Krytyczny błąd transportu API GIOŚ: {str(e)}"
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
        """Sprawdź dostępność serwera głównego GIOŚ"""
        try:
            response = requests.head(
                "https://api.gios.gov.pl/pjp-api/v1/rest/station/findAll",
                timeout=5
            )
            return response.status_code < 500
        except Exception:
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Statystyki odpytywania rejestru na potrzeby panelu analitycznego"""
        return {
            "api": "GIOŚ",
            "request_count": self.request_count,
            "last_request": self.last_request_time,
            "status": "active" if self.is_available() else "offline"
        }
    
    def fetch_all_stations(self) -> APIResponse:
        """
        ma pobierac pełną listę aktywnych stacji pomiarowych GIOŚ w Polsce
        """
        endpoint_config = APIConfigManager.get_endpoint_config("gios", "all_stations")
        url = endpoint_config.url if endpoint_config else "https://api.gios.gov.pl/pjp-api/v1/rest/station/findAll"
        headers = endpoint_config.headers if endpoint_config else {}
        
        api_request = APIRequest(
            api_name="GIOŚ",
            endpoint="all_stations",
            method="GET",
            url=url,
            headers=headers,
            params={}
        )
        return self.execute_request(api_request)

    def fetch_air_index(self, station_id: int) -> APIResponse:
        """
        Pobiera zbiorczy indeks jakości powietrza dla wybranej stacji (Krok 3 - Agregacja)
        """
        base_url = "https://api.gios.gov.pl/pjp-api/v1/rest/aqindex/getIndex"
        
        api_request = APIRequest(
            api_name="GIOŚ",
            endpoint=f"air_index_{station_id}",
            method="GET",
            url=f"{base_url}/{station_id}",
            headers={},
            params={}
        )
        return self.execute_request(api_request)
    