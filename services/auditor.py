def auditar_consistencia(conn_local, conn_vps, fecha, sucursal_id) -> bool:
    with conn_local.cursor() as cl, conn_vps.cursor() as cv:
        cl.execute(
            "SELECT COUNT(*), COALESCE(SUM(total),0) FROM ventas_agregadas WHERE fecha=%s AND sucursal_id=%s",
            (fecha, sucursal_id),
        )
        cv.execute(
            "SELECT COUNT(*), COALESCE(SUM(total),0) FROM ventas_agregadas WHERE fecha=%s AND sucursal_id=%s",
            (fecha, sucursal_id),
        )
        c_local, s_local = cl.fetchone()
        c_vps, s_vps = cv.fetchone()
    return (c_local == c_vps) and (s_local == s_vps)
