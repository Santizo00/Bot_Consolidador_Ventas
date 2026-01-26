from typing import List

from config.connections import MySQLConnectionManager
from config.settings import UPSERT_BATCH_SIZE, DRY_RUN, RUN_LOCAL_ONLY, ID_SUCURSAL
from models.ventas_agrupadas import VentasAgrupadas
from utils.logger import get_logger

logger = get_logger(__name__)


class VentasLoader:
    """
    Servicio encargado de persistir ventas agregadas
    usando UPSERT idempotente.
    NO ejecuta DELETE.
    """

    def __init__(self, upsert_sql_path: str = "queries/upsert_ventas.sql"):
        self.upsert_sql_path = upsert_sql_path

    def _load_sql(self) -> str:
        with open(self.upsert_sql_path, "r", encoding="utf-8") as f:
            return f.read()

    def _execute_upsert(self, connection, ventas: List[VentasAgrupadas]):
        sql = self._load_sql()
        cursor = connection.cursor()

        data = [v.to_tuple_for_upsert() for v in ventas]

        for i in range(0, len(data), UPSERT_BATCH_SIZE):
            batch = data[i:i + UPSERT_BATCH_SIZE]
            cursor.executemany(sql, batch)

        cursor.close()

    def load(self, ventas: List[VentasAgrupadas]):
        """
        Persiste ventas agregadas en:
        - BD local
        - BD VPS (opcional)
        """
        if DRY_RUN:
            logger.warning("DRY_RUN activo: no se ejecutará ninguna escritura")
            return

        if not ventas:
            return

        conn_local = None
        conn_vps = None

        try:
            # =========================
            # BD AGREGADA LOCAL
            # =========================
            conn_local = MySQLConnectionManager.connect_local()
            self._execute_upsert(conn_local, ventas)
            conn_local.commit()

            # =========================
            # BD AGREGADA VPS
            # =========================
            if not RUN_LOCAL_ONLY:
                conn_vps = MySQLConnectionManager.connect_vps()
                self._execute_upsert(conn_vps, ventas)
                conn_vps.commit()

            else:
                logger.info("RUN_LOCAL_ONLY activo: se omite UPSERT en VPS")

        except Exception as e:
            logger.error(f"Error durante UPSERT de ventas: {e}")

            if conn_local:
                conn_local.rollback()
            if conn_vps:
                conn_vps.rollback()

            raise

        finally:
            if conn_local:
                conn_local.close()
            if conn_vps:
                conn_vps.close()
