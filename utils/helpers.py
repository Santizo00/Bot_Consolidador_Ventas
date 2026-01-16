from datetime import date, datetime, timedelta
from typing import List

from config.settings import (
    HISTORICAL_MODE,
    HISTORICAL_START_DATE,
    HISTORICAL_END_DATE,
)


def get_process_dates(reprocess_days: int) -> List[date]:
    """
    Devuelve la lista de fechas a procesar según el modo de ejecución.

    - Modo normal: hoy o últimos N días
    - Modo histórico: desde fecha de apertura hasta fecha fin
    """

    today = date.today()
    dates: List[date] = []

    # =========================
    # MODO HISTÓRICO
    # =========================
    if HISTORICAL_MODE:
        start_date = datetime.strptime(
            HISTORICAL_START_DATE, "%Y-%m-%d"
        ).date()

        end_date = (
            datetime.strptime(HISTORICAL_END_DATE, "%Y-%m-%d").date()
            if HISTORICAL_END_DATE
            else today
        )

        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)

        return dates

    # =========================
    # MODO NORMAL
    # =========================
    for i in range(reprocess_days):
        dates.append(today - timedelta(days=i))

    return dates
