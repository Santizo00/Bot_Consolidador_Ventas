import csv
import os
from datetime import datetime


BITACORA_PATH = "logs/bitacora_extraccion.csv"


def registrar_bitacora(
    fecha,
    estado,
    intentos,
    filas=0,
    error=None
):
    """
    Registra una fila en la bitácora CSV.
    """
    file_exists = os.path.exists(BITACORA_PATH)

    with open(BITACORA_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Escribir encabezado si el archivo no existe
        if not file_exists:
            writer.writerow([
                "fecha",
                "estado",
                "intentos",
                "filas",
                "error",
                "fecha_registro"
            ])

        writer.writerow([
            fecha,
            estado,
            intentos,
            filas,
            error,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
