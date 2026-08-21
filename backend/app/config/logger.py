import logging
import os
import sys

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "studiq_system.log")

logger = logging.getLogger("studiq")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # Console Handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File Handler
    f_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

def log_event(category: str, message: str, level: str = "info"):
    formatted_msg = f"[{category.upper()}] {message}"
    if level.lower() == "warning":
        logger.warning(formatted_msg)
    elif level.lower() == "error":
        logger.error(formatted_msg)
    else:
        logger.info(formatted_msg)
    for h in logger.handlers:
        h.flush()
