import time
from typing import Callable

from config.settings import MAX_RETRIES, RETRY_DELAY_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)


def retry(operation: Callable, description: str = "operación"):
    """
    Ejecuta una función con reintentos controlados.
    """
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            return operation()
        except Exception as e:
            attempt += 1
            logger.warning(
                f"Fallo en {description} (intento {attempt}/{MAX_RETRIES}): {e}"
            )

            if attempt >= MAX_RETRIES:
                logger.error(f"{description} falló definitivamente")
                raise

            time.sleep(RETRY_DELAY_SECONDS)
