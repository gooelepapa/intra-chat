import logging
import os
import warnings
from logging.handlers import RotatingFileHandler
from typing import Literal, Optional

from coloredlogs import ColoredFormatter

TO_FILE = os.environ.get("TO_FILE", False)
if TO_FILE:
    TO_FILE = TO_FILE.lower() in ("true", "1")


def get_logger(
    name: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    to_file: bool = TO_FILE,
    log_dir: str = "./logs",
    file_name: Optional[str] = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        # If the logger already has handlers, return it
        return logger

    log_lv = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_lv)
    fmt = ColoredFormatter(format)
    std_out = logging.StreamHandler()
    std_out.setFormatter(fmt)
    logger.addHandler(std_out)
    if to_file:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if file_name is None:
            warnings.warn("File name is not provided. Using default: 'log.txt'")
            file = f"log_{name.replace('.', '-')}.log"
        else:
            file = file_name + ".log"
        file_path = os.path.join(log_dir, file)
        file_handler = RotatingFileHandler(file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
        file_handler.setFormatter(logging.Formatter(format))
        logger.addHandler(file_handler)
    logger.propagate = False
    return logger


if __name__ == "__main__":
    # Example usage
    logger = get_logger("logger_test")
    logger.setLevel(logging.DEBUG)
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
