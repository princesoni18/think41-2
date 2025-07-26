import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger("think41_chatbot")
logger.setLevel(LOG_LEVEL)

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)

# Usage: from app.utils.logger import logger
