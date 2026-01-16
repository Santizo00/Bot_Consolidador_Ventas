import os
from decimal import Decimal
from typing import Dict

from config.connections import MySQLConnectionManager
from config.settings import ENABLE_AUDIT, AUDIT_TOLERANCE
from utils.logger import get_logger

logger = get_logger(__name__)


class VentasAuditor:
    """
    Servicio encargado de validar la consistencia de los datos
    entre la base operativa (ventasdiarias)
    y las bases agregadas (local y VPS),
    por fecha y sucursal.
    """

    def __init__(
        self,
        sql_operativa_path: str = "queries/audit_operativa.sql",
        sql_agrupadas_path: str = "queries/audit_agrupadas.sql",
    ):
        self.sql_operativa_path = sql_operativa_path
        self.sql_agrupadas_path = sql_agrupadas_path

    # =========================
    # UTILIDADES
    # =========================

    def _load_sql(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró el archivo SQL: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _execute(self, connection, sql: str, params: tuple) -> Dict:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        result = cursor.fetchone()
        cursor.close()
        return result or {}

    @staticmethod
    def _diff_ok(a, b) -> bool:
        """
        Compara dos valores numéricos usando Decimal
        para evitar errores de precisión y tipos.
        """
        da = Decimal(str(a))
        db = Decimal(str(b))
        tolerance = Decimal(str(AUDIT_TOLERANCE))

        return abs(da - db) <= tolerance

    # =========================
    # AUDITORÍA PRINCIPAL
    # =========================

    def audit(self, id_sucursal: int, process_date) -> bool:
        """
        Ejecuta auditoría por fecha y sucursal.
        Compara:
        - ventasdiarias vs ventas_agrupadas (local)
        - ventas_agrupadas local vs VPS
        """

        if not ENABLE_AUDIT:
            logger.warning("Auditoría deshabilitada por configuración")
            return True

        logger.info(
            f"Iniciando auditoría para sucursal {id_sucursal} - fecha {process_date}"
        )

        sql_operativa = self._load_sql(self.sql_operativa_path)
        sql_agrupadas = self._load_sql(self.sql_agrupadas_path)

        conn_operativa = None
        conn_local = None
        conn_vps = None

        try:
            conn_operativa = MySQLConnectionManager.connect_sucursal()
            conn_local = MySQLConnectionManager.connect_local()
            conn_vps = MySQLConnectionManager.connect_vps()

            operativa = self._execute(
                conn_operativa,
                sql_operativa,
                (process_date, id_sucursal),
            )

            local = self._execute(
                conn_local,
                sql_agrupadas,
                (process_date, id_sucursal),
            )

            vps = self._execute(
                conn_vps,
                sql_agrupadas,
                (process_date, id_sucursal),
            )

            logger.info(f"Operativa: {operativa}")
            logger.info(f"Local:     {local}")
            logger.info(f"VPS:       {vps}")

            # =========================
            # COMPARACIÓN OPERATIVA vs LOCAL
            # =========================

            if operativa["TotalFilas"] != local["TotalFilas"]:
                logger.error("Diferencia en cantidad de filas (operativa vs local)")
                return False

            if not self._diff_ok(
                operativa["TotalUnidades"], local["TotalUnidades"]
            ):
                logger.error("Diferencia en unidades (operativa vs local)")
                return False

            if not self._diff_ok(
                operativa["TotalVenta"], local["TotalVenta"]
            ):
                logger.error("Diferencia en ventas (operativa vs local)")
                return False

            if not self._diff_ok(
                operativa["TotalCosto"], local["TotalCosto"]
            ):
                logger.error("Diferencia en costos (operativa vs local)")
                return False

            # =========================
            # COMPARACIÓN LOCAL vs VPS
            # =========================

            if local["TotalFilas"] != vps["TotalFilas"]:
                logger.error("Diferencia en cantidad de filas (local vs VPS)")
                return False

            if not self._diff_ok(
                local["TotalUnidades"], vps["TotalUnidades"]
            ):
                logger.error("Diferencia en unidades (local vs VPS)")
                return False

            if not self._diff_ok(
                local["TotalVenta"], vps["TotalVenta"]
            ):
                logger.error("Diferencia en ventas (local vs VPS)")
                return False

            if not self._diff_ok(
                local["TotalCosto"], vps["TotalCosto"]
            ):
                logger.error("Diferencia en costos (local vs VPS)")
                return False

            logger.info(
                f"Auditoría OK para sucursal {id_sucursal} - fecha {process_date}"
            )
            return True

        except Exception as e:
            logger.error(f"Error durante auditoría: {e}")
            raise

        finally:
            if conn_operativa:
                conn_operativa.close()
            if conn_local:
                conn_local.close()
            if conn_vps:
                conn_vps.close()
