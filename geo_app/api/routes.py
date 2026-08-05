"""
API Routes - Wszystkie endpoints aplikacji
"""
import json
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from api.dependencies import get_db, get_package_repository, get_current_user
from schemas import PackageResponse, HealthCheckResponse
from repositories import PackageRepository
from models import PackageModel
from services import APIClientFactory, DataProcessingService
from utils.logger import LoggerFactory
from utils import FileHandler
from config.settings import settings

logger = LoggerFactory.get_logger(__name__)
router = APIRouter()


# Endpointy pakietów

@router.get("/packages", response_model=dict)
async def get_all_packages(
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0
):
    """
    Pobierz listę wszystkich pakietów
    
    Query Parameters:
    - limit: Limit wyników (domyślnie 100)
    - offset: Offset dla paginacji (domyślnie 0)
    """
    try:
        repo = PackageRepository(db)
        packages = repo.get_all(limit=limit, offset=offset)
        logger.info(f"Pobrano {len(packages)} pakietów")
        
        return {
            "success": True,
            "count": len(packages),
            "packages": [p.to_dict() for p in packages]
        }
    except Exception as e:
        logger.error(f"Błąd przy pobieraniu pakietów: {e}")
        raise HTTPException(status_code=500, detail="Błąd przy pobieraniu pakietów")


@router.get("/packages/{package_id}", response_model=dict)
async def get_package_details(package_id: str, db: Session = Depends(get_db)):
    """
    Pobierz szczegóły konkretnego pakietu
    """
    try:
        repo = PackageRepository(db)
        package = repo.get_by_id(package_id)
        
        if not package:
            logger.warning(f"Pakiet nie znaleziony: {package_id}")
            raise HTTPException(status_code=404, detail="Pakiet nie znaleziony")
        
        logger.info(f"Pobrano pakiet: {package_id}")
        return {
            "success": True,
            "package": package.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd przy pobieraniu pakietu: {e}")
        raise HTTPException(status_code=500, detail="Błąd wewnętrzny serwera")


def _require_authenticated(request: Request) -> None:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Wymagane logowanie")


@router.get("/packages/{package_id}/download")
async def download_package(package_id: str, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Pobierz plik ZIP pakietu
    """
    try:
        # Zależność `get_current_user` zapewnia, że użytkownik jest zalogowany
        repo = PackageRepository(db)
        package = repo.get_by_id(package_id)
        
        if not package:
            raise HTTPException(status_code=404, detail="Pakiet nie znaleziony")
        
        if package.status != "ready":
            raise HTTPException(
                status_code=400,
                detail=f"Pakiet nie jest gotowy. Status: {package.status}"
            )
        
        if not FileHandler.file_exists(package.file_path):
            logger.error(f"Plik pakietu nie znaleziony na dysku: {package.file_path}")
            raise HTTPException(status_code=404, detail="Plik pakietu nie istnieje")
        
        logger.info(f"Pobieranie pakietu: {package_id}")
        
        return FileResponse(
            path=package.file_path,
            media_type="application/zip",
            filename=f"package_{package_id}.zip"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd przy pobieraniu pakietu: {e}")
        raise HTTPException(status_code=500, detail="Błąd przy pobieraniu pliku")


# Endpointy uruchamiania przetwarzania

@router.post("/trigger-processing")
async def trigger_data_processing(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api: str = "gbif"
):
    """
    Ręcznie wyzwól przetwarzanie danych
    
    Query Parameters:
    - api: Które API użyć (gbif, overpass)
    """
    try:
        repo = PackageRepository(db)
        package_id = str(uuid.uuid4())
        
        # rekord pakietu
        package = repo.create(
            package_id=package_id,
            region="Polska",
            source=f"{api.upper()} API"
        )
        
        # Dodaje zadanie do kolejki
        background_tasks.add_task(
            _process_data_background,
            package_id=package_id,
            api_name=api,
            db_url=settings.database_url
        )
        
        logger.info(f"Wyzwolono przetwarzanie: {package_id} (API: {api})")
        
        return {
            "success": True,
            "message": "Przetwarzanie wyzwolone",
            "package_id": package_id,
            "status": "processing",
            "api": api
        }
    except Exception as e:
        logger.error(f"Błąd przy wyzwalaniu przetwarzania: {e}")
        raise HTTPException(status_code=500, detail="Błąd przy wyzwalaniu przetwarzania")


# Endpointy informacyjne

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Sprawdzenie zdrowotności systemu
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version
    )


@router.get("/api-status")
async def get_api_status():
    """
    Sprawdź status wszystkich dostępnych API
    """
    try:
        factory = APIClientFactory()
        status = {}
        
        for api_name in factory.list_available_clients():
            try:
                client = factory.create_client(api_name)
                status[api_name] = {
                    "available": client.is_available(),
                    "rate_limit": client.get_rate_limit_status()
                }
            except Exception as e:
                logger.error(f"Błąd przy sprawdzaniu API {api_name}: {e}")
                status[api_name] = {"available": False, "error": str(e)}
        
        logger.info(f"Status API: {status}")
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "apis": status
        }
    except Exception as e:
        logger.error(f"Błąd przy pobieraniu statusu API: {e}")
        raise HTTPException(status_code=500, detail="Błąd przy pobieraniu statusu")


@router.get("/latest-geojson")
async def get_latest_geojson(db: Session = Depends(get_db)):
    """
    Pobierz najnowszy plik GeoJSON
    """
    try:
        repo = PackageRepository(db)
        latest = repo.get_latest_ready()
        
        if not latest or not latest.file_path:
            return {"type": "FeatureCollection", "features": []}
        
        geojson_path = latest.file_path.replace(".zip", ".geojson")
        
        if FileHandler.file_exists(geojson_path):
            return FileResponse(
                path=geojson_path,
                media_type="application/json"
            )
        
        return {"type": "FeatureCollection", "features": []}
    except Exception as e:
        logger.error(f"Błąd przy pobieraniu GeoJSON: {e}")
        return {"type": "FeatureCollection", "features": []}


@router.get("/packages-by-date")
async def get_packages_by_date(
    db: Session = Depends(get_db),
    from_date: str = None,
    to_date: str = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Pobierz pakiety z zakresu dat.
    
    Query Parameters:
    - from_date: Data początkowa (YYYY-MM-DD format)
    - to_date: Data końcowa (YYYY-MM-DD format)
    - limit: Limit wyników (domyślnie 100)
    - offset: Offset dla paginacji (domyślnie 0)
    
    przykład: /api/packages-by-date?from_date=2024-01-01&to_date=2024-12-31
    """
    try:
        from datetime import datetime as dt
        from sqlalchemy import and_
        
        repo = PackageRepository(db)
        query = repo.db.query(PackageModel).order_by(
            desc(PackageModel.created_at)
        )
        
        # Filtruj po dacie
        if from_date:
            try:
                from_dt = dt.strptime(from_date, "%Y-%m-%d")
                query = query.filter(PackageModel.created_at >= from_dt)
                logger.info(f"Filtrowanie od: {from_date}")
            except ValueError:
                raise HTTPException(status_code=400, detail="Zły format daty (użyj YYYY-MM-DD)")
        
        if to_date:
            try:
                to_dt = dt.strptime(to_date, "%Y-%m-%d")
                to_dt = to_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(PackageModel.created_at <= to_dt)
                logger.info(f"Filtrowanie do: {to_date}")
            except ValueError:
                raise HTTPException(status_code=400, detail="Zły format daty (użyj YYYY-MM-DD)")
        
        # Pobiera pakiety
        total = query.count()
        packages = query.limit(limit).offset(offset).all()
        
        logger.info(f"Pobrano {len(packages)} pakietów dla zakresu dat")
        
        return {
            "success": True,
            "count": len(packages),
            "total": total,
            "from_date": from_date,
            "to_date": to_date,
            "packages": [p.to_dict() for p in packages],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd przy filtrowaniu pakietów: {e}")
        raise HTTPException(status_code=500, detail="Błąd przy filtrowaniu pakietów")


@router.get("/packages-latest-n")
async def get_latest_n_packages(
    db: Session = Depends(get_db),
    count: int = 10
):
    """
    Pobierz N ostatnich pakietów.
    
    Query Parameters:
    - count: Liczba ostatnich pakietów (domyślnie 10, max 100)
    
    Przykład: /api/packages-latest-n?count=5
    """
    try:
        if count > 100:
            count = 100
        if count < 1:
            count = 1
        
        repo = PackageRepository(db)
        packages = repo.get_all(limit=count, offset=0)
        
        logger.info(f"Pobrano {len(packages)} ostatnich pakietów")
        
        return {
            "success": True,
            "count": len(packages),
            "packages": [p.to_dict() for p in packages]
        }
    except Exception as e:
        logger.error(f"Błąd przy pobieraniu ostatnich pakietów: {e}")
        raise HTTPException(status_code=500, detail="Błąd przy pobieraniu pakietów")


# Funkcje pomocnicze

async def _process_data_background(package_id: str, api_name: str, db_url: str):
    """
    Funkcja do przetwarzania danych w tle
    """
    from api.dependencies import SessionLocal
    
    db = SessionLocal()
    try:
        repo = PackageRepository(db)
        
        # Ustawia status na przetwarzanie
        repo.update_status(package_id, "processing")
        
        # Pobiera dane z API
        factory = APIClientFactory()
        client = factory.create_client(api_name)
        
        logger.info(f"Pobieranie danych z {api_name} dla {package_id}")
        
        if api_name.lower() == "gbif":
            response = client.search_occurrences()
            occurrences = response.data.get("results", [])
        else:
            logger.warning(f"API {api_name} nie jest w pełni obsługiwane")
            occurrences = []
        
        if not response.is_success:
            logger.error(f"Błąd API: {response.error}")
            repo.update_status(package_id, "failed")
            return
        
        # Przetwarza dane
        processor = DataProcessingService(client, repo)
        result = processor.process_full_pipeline(package_id, occurrences)
        
        if not result:
            repo.update_status(package_id, "failed")
            logger.error(f"Błąd w pipeline dla {package_id}")
            return
        
        # Zapisuje wyniki w pakiecie
        repo.update_full(
            package_id,
            status="ready",
            file_path=result["zip_path"],
            item_count=result["item_count"],
            bbox=result["bbox"]
        )
        
        logger.info(f"Przetwarzanie zakończone: {package_id}")
        
    except Exception as e:
        logger.error(f"Błąd w przetwarzaniu {package_id}: {e}")
        repo.update_status(package_id, "failed")
    finally:
        db.close()

@router.get("/analytics/stats", tags=["analytics"])
async def get_analytics_stats():
    """
    Endpoint zwracający statystyki natywnej telemetrii
    """
    # ścieżka do logów w oparciu o globalne settings
    analytics_file = os.path.join(settings.data_output_dir, "analytics_logs.json")
    
    if not os.path.exists(analytics_file):
        return {"total_views": 0, "unique_users": 0, "page_distribution": {}}
        
    try:
        with open(analytics_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
            
        total_views = len(logs)
        unique_users = len(set(log["user_id"] for log in logs if log["user_id"]))
        
        page_dist = {}
        for log in logs:
            page_dist[log["page"]] = page_dist.get(log["page"], 0) + 1
            
        return {
            "total_views": total_views,
            "unique_users": unique_users,
            "page_distribution": page_dist
        }
    except Exception as e:
        return {"error": str(e)}