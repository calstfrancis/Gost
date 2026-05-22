"""
logger.py — Logging configuration for Gost.
"""

import logging
import os
from pathlib import Path


def setup_logging() -> logging.Logger:
    log_dir = Path.home() / ".local" / "share" / "gost"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "gost.log"

    logger = logging.getLogger("gost")
    logger.setLevel(logging.DEBUG)
    
    # File handler - debug level
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler - info level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("gost")
