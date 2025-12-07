"""
Logger Module
Centralized logging configuration for the RAG pipeline
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class LoggerManager:
    """Manages logging configuration for the entire application"""
    
    _logger = None
    _initialized = False
    
    @classmethod
    def configure_logger(cls, log_file: str = None, level: str = "INFO"):
        """
        Configure the logger with file and console handlers
        
        Args:
            log_file: Path to log file
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if cls._initialized:
            return cls._logger
        
        # Create logger
        logger = logging.getLogger("rag_pipeline")
        logger.setLevel(getattr(logging, level))
        
        # Create logs directory if it doesn't exist
        if log_file:
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level))
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File Handler (if log_file is provided)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level))
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        
        cls._logger = logger
        cls._initialized = True
        return logger
    
    @classmethod
    def get_logger(cls):
        """Get the configured logger instance"""
        if not cls._initialized:
            cls.configure_logger()
        return cls._logger


def get_logger(name: str = None):
    """
    Convenience function to get a logger
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = LoggerManager.get_logger()
    if name:
        return logging.getLogger(name)
    return logger
