import sys

from config.settings import REPROCESS_DAYS
from utils.logger import get_logger
from utils.retry import retry
from utils.helpers import get_process_dates

from services.partition_manager import PartitionManager
from services.extractor import VentasExtractor
from services.loader import VentasLoader
from services.auditor import VentasAuditor

logger = get_logger(__name__)


def run_for_date(process_date):
    """
    Ejecuta el flujo completo del bot para una fecha específica.
    """
    logger.info(f"Iniciando proceso para fecha {process_date}")

    extractor = VentasExtractor()
    loader = VentasLoader()
    auditor = VentasAuditor()

    # =========================
    # EXTRACCIÓN
    # =========================
    ventas = retry(
        lambda: extractor.extract(),
        description="extracción de ventas"
    )

    if not ventas:
        logger.warning("No se encontraron ventas para procesar")
        return

    # Todas las ventas corresponden a la misma sucursal
    id_sucursal = ventas[0].id_sucursal

    # =========================
    # CARGA
    # =========================
    retry(
        lambda: loader.load(ventas, id_sucursal),
        description="carga de ventas"
    )

    # =========================
    # AUDITORÍA
    # =========================
    audit_ok = retry(
        lambda: auditor.audit(id_sucursal),
        description="auditoría de ventas"
    )

    if not audit_ok:
        raise Exception("Auditoría fallida, se requiere reproceso")

    logger.info(f"Proceso completado correctamente para fecha {process_date}")


def main():
    logger.info("===== INICIANDO BOT CONSOLIDADOR DE VENTAS =====")

    try:
        # =========================
        # PARTICIONES
        # =========================
        pm = PartitionManager()
        retry(
            lambda: pm.ensure_current_and_next_year(),
            description="gestión de particiones"
        )

        # =========================
        # PROCESAMIENTO POR FECHA
        # =========================
        dates_to_process = get_process_dates(REPROCESS_DAYS)

        for process_date in dates_to_process:
            run_for_date(process_date)

        logger.info("===== BOT FINALIZADO SIN ERRORES =====")

    except Exception as e:
        logger.critical(f"Error crítico en ejecución del bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
