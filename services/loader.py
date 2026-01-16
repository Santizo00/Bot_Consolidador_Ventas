import os
from typing import List

from config.connections import MySQLConnectionManager
from config.settings import UPSERT_BATCH_SIZE, DRY_RUN, RUN_LOCAL_ONLY
from models.ventas_agrupadas import VentasAgrupadas
from utils.logger import get_logger

logger = get_logger(__name__)


class VentasLoader:
    """
    Servicio encargado de persistir ventas agregadas.
    Ejecuta DELETE + UPSERT de forma idempotente.
    """

    def __init__(
        self,
        delete_sql_path: str = "queries/delete_ventas.sql",
        upsert_sql_path: str = "queries/upsert_ventas.sql"
    ):
        self.delete_sql_path = delete_sql_path
        self.upsert_sql_path = upsert_sql_path

    def _load_sql(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró el archivo SQL: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _execute_delete(self, connection, id_sucursal: int):
        sql = self._load_sql(self.delete_sql_path)
        cursor = connection.cursor()

        logger.info(f"Ejecutando DELETE para sucursal {id_sucursal}")
        cursor.execute(sql, (id_sucursal,))
        cursor.close()

    def _execute_upsert(self, connection, ventas: List[VentasAgrupadas]):
        sql = self._load_sql(self.upsert_sql_path)
        cursor = connection.cursor()

        data = [v.to_tuple_for_upsert() for v in ventas]

        logger.info(f"UPSERT de {len(data)} registros")

        for i in range(0, len(data), UPSERT_BATCH_SIZE):
            batch = data[i:i + UPSERT_BATCH_SIZE]
            cursor.executemany(sql, batch)

        cursor.close()

    def load(self, ventas: List[VentasAgrupadas], id_sucursal: int):
        """
        Persiste ventas agregadas en:
        - BD local
        - BD VPS (opcional)
        """
        if DRY_RUN:
            logger.warning("DRY_RUN activo: no se ejecutará ninguna escritura")
            return

        if not ventas:
            logger.warning("No hay ventas para procesar")
            return

        conn_local = None
        conn_vps = None

        try:
            # =========================
            # BD AGREGADA LOCAL
            # =========================
            conn_local = MySQLConnectionManager.connect_local()
            self._execute_delete(conn_local, id_sucursal)
            self._execute_upsert(conn_local, ventas)
            conn_local.commit()

            logger.info("Carga local completada")

            # =========================
            # BD AGREGADA VPS
            # =========================
            if not RUN_LOCAL_ONLY:
                conn_vps = MySQLConnectionManager.connect_vps()
                self._execute_delete(conn_vps, id_sucursal)
                self._execute_upsert(conn_vps, ventas)
                conn_vps.commit()

                logger.info("Carga en VPS completada")
            else:
                logger.info("RUN_LOCAL_ONLY activo: se omite carga en VPS")

        except Exception as e:
            logger.error(f"Error durante carga de ventas: {e}")

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
