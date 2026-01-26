from decimal import Decimal
from typing import Dict

from config.connections import MySQLConnectionManager
from config.settings import ENABLE_AUDIT, AUDIT_TOLERANCE, ID_SUCURSAL
from utils.logger import get_logger

logger = get_logger(__name__)


class VentasAuditor:
    """
    Auditoría de consistencia:
    - Operativa vs Local
    - Operativa vs VPS
    """

    # =========================
    # EJECUCIÓN DE SP
    # =========================
    @staticmethod
    def _execute_sp(connection, sp_name: str, params: list) -> Dict:
        cursor = connection.cursor(dictionary=True)
        cursor.callproc(sp_name, params)

        result = {}
        for res in cursor.stored_results():
            result = res.fetchone() or {}

        cursor.close()
        return result

    # =========================
    # COMPARACIÓN NUMÉRICA
    # =========================
    @staticmethod
    def _diff_ok(a, b) -> bool:
        da = Decimal(str(a))
        db = Decimal(str(b))
        tol = Decimal(str(AUDIT_TOLERANCE))
        return abs(da - db) <= tol

    # =========================
    # AUDITORÍA PRINCIPAL
    # =========================
    def audit(self, process_date) -> bool:
        if not ENABLE_AUDIT:
            logger.warning("Auditoría deshabilitada por configuración")
            return True

        conn_op = None
        conn_local = None
        conn_vps = None

        try:
            # =========================
            # CONEXIONES
            # =========================
            conn_op = MySQLConnectionManager.connect_sucursal()
            conn_local = MySQLConnectionManager.connect_local()
            conn_vps = MySQLConnectionManager.connect_vps()

            # =========================
            # AUDITORÍA OPERATIVA
            # =========================
            operativa = self._execute_sp(
                conn_op,
                "sp_audit_operativa",
                [process_date]
            )

            # =========================
            # AUDITORÍA AGREGADAS
            # =========================
            local = self._execute_sp(
                conn_local,
                "sp_audit_ventas_agrupadas",
                [process_date, ID_SUCURSAL]
            )

            vps = self._execute_sp(
                conn_vps,
                "sp_audit_ventas_agrupadas",
                [process_date, ID_SUCURSAL]
            )

            # =========================
            # OPERATIVA vs LOCAL
            # =========================
            if not self._diff_ok(
                operativa["TotalUnidades"], local["TotalUnidades"]
            ):
                logger.error(f"Auditoría fallida: Unidades Operativa={operativa['TotalUnidades']} vs Local={local['TotalUnidades']}")
                return False

            if not self._diff_ok(
                operativa["TotalVenta"], local["TotalVenta"]
            ):
                logger.error(f"Auditoría fallida: Ventas Operativa={operativa['TotalVenta']} vs Local={local['TotalVenta']}")
                return False

            if not self._diff_ok(
                operativa["TotalCosto"], local["TotalCosto"]
            ):
                logger.error(f"Auditoría fallida: Costos Operativa={operativa['TotalCosto']} vs Local={local['TotalCosto']}")
                return False

            # =========================
            # OPERATIVA vs VPS
            # =========================
            if not self._diff_ok(
                operativa["TotalUnidades"], vps["TotalUnidades"]
            ):
                logger.error(f"Auditoría fallida: Unidades Operativa={operativa['TotalUnidades']} vs VPS={vps['TotalUnidades']}")
                return False

            if not self._diff_ok(
                operativa["TotalVenta"], vps["TotalVenta"]
            ):
                logger.error(f"Auditoría fallida: Ventas Operativa={operativa['TotalVenta']} vs VPS={vps['TotalVenta']}")
                return False

            if not self._diff_ok(
                operativa["TotalCosto"], vps["TotalCosto"]
            ):
                logger.error(f"Auditoría fallida: Costos Operativa={operativa['TotalCosto']} vs VPS={vps['TotalCosto']}")
                return False

            logger.info(
                f"[OK] {process_date} | Unidades: {operativa['TotalUnidades']} | Venta: ${operativa['TotalVenta']} | Costo: ${operativa['TotalCosto']}"
            )
            return True

        except Exception as e:
            logger.error(f"Error durante auditoría: {e}")
            raise

        finally:
            if conn_op:
                conn_op.close()
            if conn_local:
                conn_local.close()
            if conn_vps:
                conn_vps.close()
