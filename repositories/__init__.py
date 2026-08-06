"""
Repozytoria - Warstwa dostępu do danych (Repository Pattern)
Oddziela logikę dostępu do danych od logiki biznesowej
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import PackageModel
from utils.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class PackageRepository:
    """
    Repozytorium dla pakietów danych
    Obsługuje wszystkie operacje CRUD na pakietach
    """
    
    def __init__(self, db: Session):
        """
        Inicjalizuj repozytorium
        
        Args:
            db: SQLAlchemy Session
        """
        self.db = db
    
    def create(self, package_id: str, region: str = "Polska", source: str = "System API") -> PackageModel:
        """
        Stwórz nowy pakiet
        
        Args:
            package_id: ID pakietu
            region: Region
            source: Źródło danych
            
        Returns:
            PackageModel: Utworzony pakiet
        """
        try:
            package = PackageModel(
                id=package_id,
                region=region,
                source=source,
                status="created"
            )
            self.db.add(package)
            self.db.commit()
            self.db.refresh(package)
            logger.info(f"Utworzono pakiet: {package_id}")
            return package
        except Exception as e:
            logger.error(f"Błąd przy tworzeniu pakietu: {e}")
            self.db.rollback()
            raise
    
    def get_by_id(self, package_id: str) -> Optional[PackageModel]:
        """Pobierz pakiet po ID"""
        return self.db.query(PackageModel).filter(PackageModel.id == package_id).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[PackageModel]:
        """Pobierz wszystkie pakiety z paginacją"""
        return self.db.query(PackageModel).order_by(
            desc(PackageModel.created_at)
        ).limit(limit).offset(offset).all()
    
    def get_ready_packages(self) -> List[PackageModel]:
        """Pobierz gotowe pakiety"""
        return self.db.query(PackageModel).filter(
            PackageModel.status == "ready"
        ).order_by(desc(PackageModel.created_at)).all()
    
    def get_latest_ready(self) -> Optional[PackageModel]:
        """Pobierz najnowszy gotowy pakiet"""
        return self.db.query(PackageModel).filter(
            PackageModel.status == "ready"
        ).order_by(desc(PackageModel.created_at)).first()

    def get_by_region_and_source(self, region: str, source: str) -> Optional[PackageModel]:
        """Pobierz pakiet po regionie i źródle."""
        return self.db.query(PackageModel).filter(
            PackageModel.region == region,
            PackageModel.source == source
        ).first()
    
    def update_status(self, package_id: str, status: str) -> bool:
        """Zaktualizuj status pakietu"""
        try:
            self.db.query(PackageModel).filter(
                PackageModel.id == package_id
            ).update({"status": status})
            self.db.commit()
            logger.info(f"Zaktualizowano status pakietu {package_id}: {status}")
            return True
        except Exception as e:
            logger.error(f"Błąd przy aktualizacji statusu: {e}")
            self.db.rollback()
            return False
    
    def update_full(self, package_id: str, **kwargs) -> bool:
        """Zaktualizuj całe dane pakietu"""
        try:
            self.db.query(PackageModel).filter(
                PackageModel.id == package_id
            ).update(kwargs)
            self.db.commit()
            logger.info(f"Zaktualizowano pakiet: {package_id}")
            return True
        except Exception as e:
            logger.error(f"Błąd przy aktualizacji pakietu: {e}")
            self.db.rollback()
            return False
    
    def delete(self, package_id: str) -> bool:
        """Usuń pakiet"""
        try:
            self.db.query(PackageModel).filter(
                PackageModel.id == package_id
            ).delete()
            self.db.commit()
            logger.info(f"Usunięto pakiet: {package_id}")
            return True
        except Exception as e:
            logger.error(f"Błąd przy usuwaniu pakietu: {e}")
            self.db.rollback()
            return False
