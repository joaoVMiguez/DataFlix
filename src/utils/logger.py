import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Configura logger com output para console e arquivo.
    
    Args:
        name: Nome do logger (geralmente __name__)
        log_file: Nome do arquivo de log (opcional)
        level: Nível de logging (default: INFO)
    
    Returns:
        Logger configurado
    """
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console (UTF-8)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configurar encoding UTF-8 para console
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        # Criar diretório de logs se não existir
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Adicionar timestamp ao nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d")
        log_path = log_dir / f"{timestamp}_{log_file}"
        
        file_handler = logging.FileHandler(
            log_path,
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str, level=logging.INFO): 
    """
    Retorna logger simples sem arquivo.
    
    Args:
        name: Nome do logger
        level: Nível de logging
    
    Returns:
        Logger configurado
    """
    return setup_logger(name, log_file=None, level=level)