from config.connections import MySQLConnectionManager
from config.settings import ID_SUCURSAL
from utils.logger import get_logger

logger = get_logger(__name__)


class VentasReprocessor:

    @staticmethod
    def delete(process_date):
        conn_local = None
        conn_vps = None

        try:
            conn_local = MySQLConnectionManager.connect_local()
            conn_vps = MySQLConnectionManager.connect_vps()

            for conn, name in [
                (conn_local, "LOCAL"),
                (conn_vps, "VPS"),
            ]:
                cursor = conn.cursor()
                cursor.callproc(
                    "sp_delete_ventas_agrupadas",
                    [process_date, ID_SUCURSAL]
                )
                
                # Consumir resultados del stored procedure
                for _ in cursor.stored_results():
                    pass
                    
                conn.commit()
                cursor.close()

        finally:
            if conn_local:
                conn_local.close()
            if conn_vps:
                conn_vps.close()
