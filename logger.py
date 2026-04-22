import os
import logging
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)

logger = logging.getLogger("gym_control")


def log_error(ex: Exception, context: str = ""):
    import traceback
    msg = f"{context}: {str(ex)}" if context else str(ex)
    logger.error(msg)
    logger.error(traceback.format_exc())
