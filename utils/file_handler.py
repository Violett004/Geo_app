"""
Obsługa plików i katalogów
"""
import os
import shutil
from pathlib import Path
from utils.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class FileHandler:
    """Obsługa operacji na plikach"""
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> bool:
        """
        Upewni się, że katalog istnieje
        
        Args:
            directory: Ścieżka do katalogu
            
        Returns:
            bool: True jeśli operacja się powiodła
        """
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Katalog gotowy: {directory}")
            return True
        except Exception as e:
            logger.error(f"Błąd przy tworzeniu katalogu {directory}: {e}")
            return False
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Sprawdź czy plik istnieje"""
        return os.path.exists(file_path)
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Usuń plik"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Plik usunięty: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Błąd przy usuwaniu pliku {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Pobierz rozmiar pliku w bajtach"""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Błąd przy pobieraniu rozmiaru pliku: {e}")
            return 0
    
    @staticmethod
    def get_files_in_directory(directory: str, extension: str = None) -> list:
        try:
            files = []
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    if extension is None or file.endswith(extension):
                        files.append(file_path)
            return files
        except Exception as e:
            logger.error(f"Błąd przy czytaniu katalogu {directory}: {e}")
            return []
