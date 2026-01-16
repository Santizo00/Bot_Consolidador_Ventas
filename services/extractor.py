from typing import List, Dict, Any
from utils.helpers import read_query


def extract_ventas(conn, fecha) -> List[Dict[str, Any]]:
    sql = read_query("select_ventas.sql")
    with conn.cursor() as cur:
        cur.execute(sql, (fecha,))
        return list(cur.fetchall())
