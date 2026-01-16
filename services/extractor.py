import os
from typing import List

from config.connections import MySQLConnectionManager
from models.ventas_agrupadas import VentasAgrupadas
from utils.logger import get_logger

logger = get_logger(__name__)


class VentasExtractor:
    """
    Servicio encargado de extraer y agregar ventas desde la BD de la sucursal.
    NO escribe en ninguna base de datos.
    """

    def __init__(self, sql_path: str = "queries/select_ventas.sql"):
        self.sql_path = sql_path

    def _load_sql(self) -> str:
        """
        Carga la consulta SQL desde archivo.
        """
        if not os.path.exists(self.sql_path):
            raise FileNotFoundError(f"No se encontró el archivo SQL: {self.sql_path}")

        with open(self.sql_path, "r", encoding="utf-8") as f:
            return f.read()

    def extract(self) -> List[VentasAgrupadas]:
        """
        Ejecuta la consulta de agregación en la sucursal y devuelve
        una lista de objetos VentasAgrupadas.
        """
        logger.info("Iniciando extracción de ventas agregadas")

        sql = self._load_sql()
        connection = None
        cursor = None
        ventas: List[VentasAgrupadas] = []

        try:
            connection = MySQLConnectionManager.connect_sucursal()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(sql)
            rows = cursor.fetchall()

            logger.info(f"Filas extraídas: {len(rows)}")

            for row in rows:
                venta = VentasAgrupadas.from_db_row(row)
                venta.validate()
                ventas.append(venta)

            logger.info("Extracción de ventas completada correctamente")
            return ventas

        except Exception as e:
            logger.error(f"Error durante la extracción de ventas: {e}")
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
