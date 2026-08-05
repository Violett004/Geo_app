# """
# Serwis przetwarzania danych
# """
# import json
# import csv
# import zipfile
# from datetime import datetime
# from typing import Dict, Any, List, Optional
# from services.base_api_client import BaseAPIClient
# from repositories import PackageRepository
# from utils.logger import LoggerFactory
# from utils import FileHandler
# from config.settings import settings

# logger = LoggerFactory.get_logger(__name__)


# class DataProcessingService:
#     """
#     Serwis do przetwarzania danych z API
#     Obsługuje konwersję do CSV, GeoJSON i ZIP
#     """
    
#     def __init__(self, api_client: BaseAPIClient, repository: PackageRepository):
#         """
#         Inicjalizuj serwis
        
#         Args:
#             api_client: Klient API do pobierania danych
#             repository: Repozytorium do przechowywania metadanych
#         """
#         self.api_client = api_client
#         self.repository = repository
    
#     def process_occurrences_to_csv(
#         self, 
#         occurrences: List[Dict[str, Any]], 
#         output_path: str
#     ) -> bool:
#         """
#         Konwertuj obserwacje biologiczne do CSV
        
#         Args:
#             occurrences: Lista obserwacji z API GBIF
#             output_path: Ścieżka do wyjściowego pliku CSV
            
#         Returns:
#             bool: Sukces operacji
#         """
#         try:
#             logger.info(f"Konwertuję {len(occurrences)} obserwacji do CSV")
            
#             with open(output_path, 'w', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(["nazwa_obiektu", "kategoria", "lat", "lon", "informacje_dodatkowe"])
                
#                 for occ in occurrences:
#                     species = occ.get('scientificName', 'Nieznany gatunek')
#                     kingdom = occ.get('kingdom', 'Inne')
#                     lat = occ.get('decimalLatitude')
#                     lon = occ.get('decimalLongitude')
#                     institution = occ.get('institutionCode', 'GBIF Network')
                    
#                     if lat and lon:
#                         writer.writerow([species, kingdom, lat, lon, institution])
            
#             logger.info(f"CSV zapisany: {output_path}")
#             return True
#         except Exception as e:
#             logger.error(f"Błąd przy tworzeniu CSV: {e}")
#             return False
    
#     def process_occurrences_to_geojson(
#         self, 
#         occurrences: List[Dict[str, Any]], 
#         output_path: str
#     ) -> Dict[str, float]:
#         """
#         Konwertuj obserwacje do GeoJSON i oblicz bounding box
        
#         Args:
#             occurrences: Lista obserwacji
#             output_path: Ścieżka do wyjściowego pliku GeoJSON
            
#         Returns:
#             Dict: Bounding box {minx, miny, maxx, maxy}
#         """
#         try:
#             logger.info(f"Konwertuję {len(occurrences)} obserwacji do GeoJSON")
            
#             features = []
#             lats = []
#             lons = []
#             current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
#             for occ in occurrences:
#                 lat = occ.get('decimalLatitude')
#                 lon = occ.get('decimalLongitude')
                
#                 if lat and lon:
#                     lats.append(lat)
#                     lons.append(lon)
                    
#                     species = occ.get('scientificName', 'Nieznany gatunek')
#                     kingdom = occ.get('kingdom', 'Inne')
#                     institution = occ.get('institutionCode', 'GBIF Network')
                    
#                     feature = {
#                         "type": "Feature",
#                         "geometry": {
#                             "type": "Point",
#                             "coordinates": [lon, lat]
#                         },
#                         "properties": {
#                             "name": f"{species} ({kingdom})",
#                             "author": f"Źródło: {institution}",
#                             "date": current_date
#                         }
#                     }
#                     features.append(feature)
            
#             geojson = {
#                 "type": "FeatureCollection",
#                 "features": features
#             }
            
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 json.dump(geojson, f, indent=2, ensure_ascii=False)
            
#             logger.info(f"GeoJSON zapisany: {output_path}")
            
#             # Oblicza bounding box
#             bbox = {
#                 "minx": min(lons) if lons else 14.0,
#                 "miny": min(lats) if lats else 49.0,
#                 "maxx": max(lons) if lons else 24.0,
#                 "maxy": max(lats) if lats else 55.0
#             }
            
#             return bbox
#         except Exception as e:
#             logger.error(f"Błąd przy tworzeniu GeoJSON: {e}")
#             return {}
    
#     def create_zip_package(
#         self, 
#         csv_path: str, 
#         geojson_path: str, 
#         zip_path: str
#     ) -> bool:
#         """
#         Pakuj CSV i GeoJSON do ZIP
        
#         Args:
#             csv_path: Ścieżka do pliku CSV
#             geojson_path: Ścieżka do pliku GeoJSON
#             zip_path: Ścieżka do wyjściowego pliku ZIP
            
#         Returns:
#             bool: Sukces operacji
#         """
#         try:
#             logger.info(f"Tworzę pakiet ZIP: {zip_path}")
            
#             with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
#                 zipf.write(csv_path, arcname="data.csv")
#                 zipf.write(geojson_path, arcname="data.geojson")
            
#             logger.info(f"ZIP pakiet utworzony: {zip_path}")
#             return True
#         except Exception as e:
#             logger.error(f"Błąd przy tworzeniu ZIP: {e}")
#             return False
    
#     def process_full_pipeline(
#         self, 
#         package_id: str, 
#         occurrences: List[Dict[str, Any]],
#         package_name: str = "data"
#     ) -> Optional[Dict[str, Any]]:
#         """
#         Pełny pipeline: pobierz dane -> konwertuj CSV -> konwertuj GeoJSON -> stwórz ZIP
        
#         Args:
#             package_id: ID pakietu
#             occurrences: Lista obserwacji z API
#             package_name: Nazwa pakietu dla plików
            
#         Returns:
#             Dict: Metadane pakietu lub None jeśli błąd
#         """
#         try:
#             # Tworzy katalog wyjściowy
#             FileHandler.ensure_directory_exists(settings.data_output_dir)
            
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             base_filename = f"package_{timestamp}_{package_id[:8]}"
            
#             csv_path = f"{settings.data_output_dir}/{base_filename}.csv"
#             geojson_path = f"{settings.data_output_dir}/{base_filename}.geojson"
#             zip_path = f"{settings.data_output_dir}/{base_filename}.zip"
            
#             logger.info(f"Rozpoczynam pipeline dla pakietu: {package_id}")
            
#             # Zapisuje dane w formacie CSV
#             if not self.process_occurrences_to_csv(occurrences, csv_path):
#                 return None
            
#             # Zapisuje dane w formacie GeoJSON
#             bbox = self.process_occurrences_to_geojson(occurrences, geojson_path)
            
#             # Pakuje pliki do archiwum
#             if not self.create_zip_package(csv_path, geojson_path, zip_path):
#                 return None
            
#             logger.info(f"Pipeline zakończony sukces: {package_id}")
            
#             return {
#                 "csv_path": csv_path,
#                 "geojson_path": geojson_path,
#                 "zip_path": zip_path,
#                 "bbox": bbox,
#                 "item_count": len(occurrences)
#             }
            
#         except Exception as e:
#             logger.error(f"Błąd w pipeline: {e}")
#             return None

"""
Serwis przetwarzania danych
"""
import json
import csv
import zipfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from services.base_api_client import BaseAPIClient
from repositories import PackageRepository
from utils.logger import LoggerFactory
from utils import FileHandler
from config.settings import settings

logger = LoggerFactory.get_logger(__name__)


class DataProcessingService:
    """
    Serwis do przetwarzania danych z API
    Obsługuje konwersję do CSV, GeoJSON i ZIP
    """
    
    def __init__(self, api_client: BaseAPIClient, repository: PackageRepository):
        """
        Inicjalizuj serwis
        
        Args:
            api_client: Klient API do pobierania danych
            repository: Repozytorium do przechowywania metadanych
        """
        self.api_client = api_client
        self.repository = repository
    
    def process_occurrences_to_csv(
        self, 
        occurrences: List[Dict[str, Any]], 
        output_path: str
    ) -> bool:
        """
        Konwertuj obserwacje do CSV z polskimi nagłówkami i kodowaniem Excela (BOM)
        """
        try:
            logger.info(f"Konwertuję {len(occurrences)} obserwacji do CSV")
            
            # Wymuszamy kodowanie utf-8-sig, aby Excel od razu poprawnie czytał polskie znaki
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Nowy, w 100% dopasowany nagłówek dla Twojej pracy
                writer.writerow(["nazwa_obiektu", "kategoria", "lat", "lon", "informacje_dodatkowe"])
                
                for occ in occurrences:
                    # Mapujemy klucze z data_pipeline na nowe, profesjonalne nazwy
                    name = occ.get('scientificName', 'Nieznany obiekt')
                    category = occ.get('kingdom', 'Inne')
                    lat = occ.get('decimalLatitude')
                    lon = occ.get('decimalLongitude')
                    meta = occ.get('publishingOrgKey', 'Brak danych szczegolowych')
                    
                    if lat and lon:
                        writer.writerow([name, category, lat, lon, meta])
            
            logger.info(f"CSV zapisany pomyślnie: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Błąd przy tworzeniu CSV: {e}")
            return False
    
    def process_occurrences_to_geojson(
        self, 
        occurrences: List[Dict[str, Any]], 
        output_path: str
    ) -> Dict[str, float]:
        """
        Konwertuj obserwacje do GeoJSON i oblicz bounding box
        """
        try:
            logger.info(f"Konwertuję {len(occurrences)} obserwacji do GeoJSON")
            
            features = []
            lats = []
            lons = []
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for occ in occurrences:
                lat = occ.get('decimalLatitude')
                lon = occ.get('decimalLongitude')
                
                if lat and lon:
                    lats.append(lat)
                    lons.append(lon)
                    
                    name = occ.get('scientificName', 'Nieznany obiekt')
                    category = occ.get('kingdom', 'Inne')
                    meta = occ.get('publishingOrgKey', 'Brak danych szczegolowych')
                    
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "properties": {
                            "name": f"{name} ({category})",
                            "author": f"{meta}",
                            "date": current_date
                        }
                    }
                    features.append(feature)
            
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, indent=2, ensure_ascii=False)
            
            logger.info(f"GeoJSON zapisany: {output_path}")
            
            # Oblicza bounding box dla Polski
            bbox = {
                "minx": min(lons) if lons else 14.0,
                "miny": min(lats) if lats else 49.0,
                "maxx": max(lons) if lons else 24.0,
                "maxy": max(lats) if lats else 55.0
            }
            
            return bbox
        except Exception as e:
            logger.error(f"Błąd przy tworzeniu GeoJSON: {e}")
            return {}
    
    def create_zip_package(
        self, 
        csv_path: str, 
        geojson_path: str, 
        zip_path: str
    ) -> bool:
        """
        Pakuj CSV i GeoJSON do ZIP
        """
        try:
            logger.info(f"Tworzę pakiet ZIP: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(csv_path, arcname="data.csv")
                zipf.write(geojson_path, arcname="data.geojson")
            
            logger.info(f"ZIP pakiet utworzony: {zip_path}")
            return True
        except Exception as e:
            logger.error(f"Błąd przy tworzeniu ZIP: {e}")
            return False
    
    def process_full_pipeline(
        self, 
        package_id: str, 
        occurrences: List[Dict[str, Any]],
        package_name: str = "data"
    ) -> Optional[Dict[str, Any]]:
        """
        Pełny pipeline: pobierz dane -> konwertuj CSV -> konwertuj GeoJSON -> stwórz ZIP
        """
        try:
            # Tworzy katalog wyjściowy
            FileHandler.ensure_directory_exists(settings.data_output_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"package_{timestamp}_{package_id[:8]}"
            
            csv_path = f"{settings.data_output_dir}/{base_filename}.csv"
            geojson_path = f"{settings.data_output_dir}/{base_filename}.geojson"
            zip_path = f"{settings.data_output_dir}/{base_filename}.zip"
            
            logger.info(f"Rozpoczynam pipeline dla pakietu: {package_id}")
            
            # Zapisuje dane w formacie CSV
            if not self.process_occurrences_to_csv(occurrences, csv_path):
                return None
            
            # Zapisuje dane w formacie GeoJSON
            bbox = self.process_occurrences_to_geojson(occurrences, geojson_path)
            
            # Pakuje pliki do archiwum
            if not self.create_zip_package(csv_path, geojson_path, zip_path):
                return None
            
            logger.info(f"Pipeline zakończony sukcesem dla: {package_id}")
            
            return {
                "csv_path": csv_path,
                "geojson_path": geojson_path,
                "zip_path": zip_path,
                "bbox": bbox,
                "item_count": len(occurrences)
            }
            
        except Exception as e:
            logger.error(f"Błąd w pipeline: {e}")
            return None