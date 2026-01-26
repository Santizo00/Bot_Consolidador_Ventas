from typing import List
from datetime import date

from config.connections import MySQLConnectionManager
from config.settings import ID_SUCURSAL
from models.ventas_agrupadas import VentasAgrupadas
from utils.logger import get_logger

logger = get_logger(__name__)


class VentasExtractor:
    """
    Servicio encargado de extraer y agregar ventas desde la BD de la sucursal
    usando un Stored Procedure.
    NO escribe en ninguna base de datos.
    """

    def extract(self, process_date: date) -> List[VentasAgrupadas]:
      
        connection = None
        cursor = None
        ventas: List[VentasAgrupadas] = []

        try:
            connection = MySQLConnectionManager.connect_sucursal()

            # dictionary=True es clave para mapear al modelo
            cursor = connection.cursor(dictionary=True)

            # Ejecutar Stored Procedure
            cursor.callproc(
                "sp_select_ventas_diarias",
                [process_date]
            )

            # MySQL devuelve resultados a través de stored_results()
            for result in cursor.stored_results():
                rows = result.fetchall()

                for row in rows:
                    venta = VentasAgrupadas.from_db_row(
                        row,
                        id_sucursal=ID_SUCURSAL
                    )
                    venta.validate()
                    ventas.append(venta)

            return ventas

        except Exception as e:
            logger.error(
                f"Error durante la extracción de ventas vía SP: {e}"
            )
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
