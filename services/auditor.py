from typing import Dict

from config.connections import MySQLConnectionManager
from config.settings import ENABLE_AUDIT, AUDIT_TOLERANCE
from utils.logger import get_logger

logger = get_logger(__name__)


class VentasAuditor:
    """
    Servicio encargado de validar la consistencia de los datos
    entre la BD agregada local y la BD agregada en la VPS.
    """

    AUDIT_SQL = """
        SELECT
            COUNT(*)            AS total_filas,
            COALESCE(SUM(Unidades), 0)    AS total_unidades,
            COALESCE(SUM(VentaTotal), 0)  AS total_venta,
            COALESCE(SUM(CostoTotal), 0)  AS total_costo
        FROM VentasAgrupadas
        WHERE Fecha = CURDATE()
          AND IdSucursal = %s;
    """

    def _execute_audit(self, connection, id_sucursal: int) -> Dict:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(self.AUDIT_SQL, (id_sucursal,))
        result = cursor.fetchone()
        cursor.close()
        return result or {}

    @staticmethod
    def _diff_ok(a: float, b: float) -> bool:
        """
        Verifica si la diferencia entre dos valores
        está dentro de la tolerancia permitida.
        """
        return abs(a - b) <= AUDIT_TOLERANCE

    def audit(self, id_sucursal: int) -> bool:
        """
        Ejecuta la auditoría comparando BD local vs VPS.
        Devuelve True si la auditoría es correcta.
        """
        if not ENABLE_AUDIT:
            logger.warning("Auditoría deshabilitada por configuración")
            return True

        logger.info(f"Iniciando auditoría para sucursal {id_sucursal}")

        conn_local = None
        conn_vps = None

        try:
            conn_local = MySQLConnectionManager.connect_local()
            conn_vps = MySQLConnectionManager.connect_vps()

            local_data = self._execute_audit(conn_local, id_sucursal)
            vps_data = self._execute_audit(conn_vps, id_sucursal)

            logger.info(f"Local: {local_data}")
            logger.info(f"VPS:   {vps_data}")

            # =========================
            # Comparaciones
            # =========================
            if local_data["total_filas"] != vps_data["total_filas"]:
                logger.error("Diferencia en cantidad de filas")
                return False

            if not self._diff_ok(local_data["total_unidades"], vps_data["total_unidades"]):
                logger.error("Diferencia en total de unidades")
                return False

            if not self._diff_ok(local_data["total_venta"], vps_data["total_venta"]):
                logger.error("Diferencia en total de ventas")
                return False

            if not self._diff_ok(local_data["total_costo"], vps_data["total_costo"]):
                logger.error("Diferencia en total de costos")
                return False

            logger.info("Auditoría completada correctamente")
            return True

        except Exception as e:
            logger.error(f"Error durante auditoría: {e}")
            raise

        finally:
            if conn_local:
                conn_local.close()
            if conn_vps:
                conn_vps.close()
