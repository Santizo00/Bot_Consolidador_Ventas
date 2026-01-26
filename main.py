import sys
from datetime import date

from utils.logger import get_logger
from utils.helpers import get_process_dates
from config.settings import REPROCESS_DAYS, MAX_RETRIES

from services.extractor import VentasExtractor
from services.loader import VentasLoader
from services.auditor import VentasAuditor
from services.reprocessor import VentasReprocessor
from utils.bitacora_csv import registrar_bitacora

logger = get_logger(__name__)


def run_process_for_date(
    extractor: VentasExtractor,
    loader: VentasLoader,
    auditor: VentasAuditor,
    process_date: date
):
    """
    Ejecuta para una fecha:
    - SELECT vía SP
    - UPSERT
    - AUDITORÍA
    Maneja reintentos y registra bitácora CSV.
    """
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # =========================
            # EXTRACCIÓN
            # =========================
            ventas = extractor.extract(process_date)
            filas = len(ventas)


            # =========================
            # UPSERT
            # =========================
            if filas > 0:
                loader.load(ventas)
            else:
                logger.info(f"Sin registros para {process_date}")
                registrar_bitacora(
                    fecha=process_date,
                    estado="OK",
                    intentos=attempt,
                    filas=0
                )
                return

            # =========================
            # AUDITORÍA
            # =========================
            audit_ok = auditor.audit(process_date)

            if not audit_ok:
                logger.warning(f"Auditoría fallida para {process_date}, reprocesando")
                VentasReprocessor.delete(process_date)
                raise Exception("Auditoría fallida")

            # =========================
            # BITÁCORA OK
            # =========================
            registrar_bitacora(
                fecha=process_date,
                estado="OK",
                intentos=attempt,
                filas=filas
            )
            return

        except Exception as e:
            last_error = str(e)
            if attempt < MAX_RETRIES:
                logger.warning(f"Error en intento {attempt}/{MAX_RETRIES} para {process_date}: {last_error}")
            else:
                logger.error(f"Error definitivo para {process_date}: {last_error}")

    # =========================
    # BITÁCORA ERROR FINAL
    # =========================

    registrar_bitacora(
        fecha=process_date,
        estado="ERROR",
        intentos=MAX_RETRIES,
        filas=0,
        error=last_error
    )


def main():
    logger.info("===== INICIANDO BOT =====")

    extractor = VentasExtractor()
    loader = VentasLoader()
    auditor = VentasAuditor()

    try:
        dates_to_process = get_process_dates(REPROCESS_DAYS)
        logger.info(f"Procesando {len(dates_to_process)} fecha(s)")

        for process_date in dates_to_process:
            run_process_for_date(
                extractor,
                loader,
                auditor,
                process_date
            )

        logger.info("===== BOT FINALIZADO =====")

    except Exception as e:
        logger.critical(
            f"Error crítico inesperado en ejecución del bot: {e}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
