"""
Konfiguracja logowania dla aplikacji
"""
import logging
import os
from config.settings import settings


class LoggerFactory:
    """Fabryka do tworzenia loggerów"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Pobierz logger po nazwie
        
        Args:
            name: Nazwa modułu (zwykle __name__)
            
        Returns:
            logging.Logger: Skonfigurowany logger
        """
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            
            # Czyta poziom logowania z konfiguracji
            level = getattr(logging, settings.log_level)
            logger.setLevel(level)
            
            # Dodaje handler konsoli
            handler = logging.StreamHandler()
            handler.setLevel(level)
            
            # Definiuje format wpisów
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            # Przypisuje handler do loggera
            if not logger.handlers:
                logger.addHandler(handler)
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]
