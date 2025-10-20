import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Configura logger com output para console e arquivo."""
    from src.settings.settings import settings
    
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Console Handler com UTF-8
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Forçar UTF-8 no console (Windows fix)
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, 'strict')
    
    logger.addHandler(console_handler)
    
    # File Handler (opcional)
    if log_file:
        settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            settings.LOGS_DIR / log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Retorna logger existente ou cria um novo."""
    return logging.getLogger(name)