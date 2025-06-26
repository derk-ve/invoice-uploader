import logging
import os
from pathlib import Path
from datetime import datetime


def setup_logger(logs_dir="./logs"):
    """Setup basic logging with file and console handlers."""
    
    # Create logs directory if it doesn't exist
    Path(logs_dir).mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("snelstart_automation")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    log_filename = f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = Path(logs_dir) / log_filename
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger