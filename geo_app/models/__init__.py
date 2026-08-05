"""
Modele SQLAlchemy - Warstwa bazy danych
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class PackageModel(Base):
    """
    Model bazy danych dla pakietu danych
    Przechowuje metadane o pobranych pakietach
    """
    __tablename__ = "packages"
    
    id = Column(String, primary_key=True, index=True, doc="Unikatowy identyfikator pakietu")
    created_at = Column(DateTime, default=datetime.utcnow, doc="Data utworzenia pakietu")
    region = Column(String, default="Polska", doc="Region, z którego pochodzą dane")
    source = Column(String, default="System API", doc="Źródło danych (API)")
    file_path = Column(String, doc="Ścieżka do pliku ZIP")
    item_count = Column(Integer, default=0, doc="Liczba elementów w pakiecie")
    bbox = Column(JSON, doc="Bounding box: {'minx', 'miny', 'maxx', 'maxy'}")
    status = Column(String, default="created", doc="Status: created/processing/ready/failed")
    
    def to_dict(self):
        """Konwertuj model na słownik"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "region": self.region,
            "source": self.source,
            "file_path": self.file_path,
            "item_count": self.item_count,
            "bbox": self.bbox,
            "status": self.status
        }
