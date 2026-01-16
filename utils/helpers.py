from datetime import date, timedelta


def get_process_dates(days: int):
    """
    Devuelve una lista de fechas a procesar.
    Ejemplo: days=1 → [hoy]
             days=2 → [hoy, ayer]
    """
    today = date.today()
    return [today - timedelta(days=i) for i in range(days)]
