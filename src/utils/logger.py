import sys
from loguru import logger
from typing import Optional

def setup_logger(level: str = "INFO", log_file: Optional[str] = None):
    """Configure loguru logger for the application."""
    logger.remove()  # Remove default handler
    
    # Add stdout handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # Optional file handler
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation="10 MB"
        )
    
    return logger

# Create a default configured logger instance
log = setup_logger()
