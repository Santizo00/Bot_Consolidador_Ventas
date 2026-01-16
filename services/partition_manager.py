from datetime import date

from config.connections import MySQLConnectionManager
from utils.logger import get_logger

logger = get_logger(__name__)


class PartitionManager:
    """
    Servicio encargado de verificar y crear particiones
    anuales en la tabla VentasAgrupadas.
    """

    TABLE_NAME = "VentasAgrupadas"
    MAX_PARTITION_NAME = "pMax"

    CHECK_PARTITION_SQL = """
        SELECT COUNT(*) AS total
        FROM information_schema.PARTITIONS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND PARTITION_NAME = %s;
    """

    REORGANIZE_PARTITION_SQL = """
        ALTER TABLE VentasAgrupadas
        REORGANIZE PARTITION pMax INTO (
            PARTITION {partition_name} VALUES LESS THAN ({less_than}),
            PARTITION pMax VALUES LESS THAN MAXVALUE
        );
    """

    def _partition_exists(self, connection, schema: str, partition_name: str) -> bool:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            self.CHECK_PARTITION_SQL,
            (schema, self.TABLE_NAME, partition_name)
        )
        result = cursor.fetchone()
        cursor.close()
        return result["total"] > 0

    def ensure_year_partition(self, year: int):
        partition_name = f"p{year}"
        less_than = year + 1

        conn = None

        try:
            conn = MySQLConnectionManager.connect_local()
            schema = conn.database

            if self._partition_exists(conn, schema, partition_name):
                logger.info(f"La partición {partition_name} ya existe")
                return

            logger.warning(f"La partición {partition_name} no existe, reorganizando pMax")

            sql = self.REORGANIZE_PARTITION_SQL.format(
                partition_name=partition_name,
                less_than=less_than
            )

            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()

            logger.info(f"Partición {partition_name} creada correctamente")

        except Exception as e:
            logger.error(f"Error al gestionar particiones: {e}")
            raise

        finally:
            if conn:
                conn.close()

    def ensure_current_and_next_year(self):
        current_year = date.today().year
        self.ensure_year_partition(current_year)
        self.ensure_year_partition(current_year + 1)
