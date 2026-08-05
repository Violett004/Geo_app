"""
Moduł API
"""
from .dependencies import get_db, get_package_repository
from .routes import router

__all__ = ["get_db", "get_package_repository", "router"]
