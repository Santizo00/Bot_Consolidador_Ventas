# config/settings.py

import os
from datetime import date

# ================================
# IDENTIDAD DE LA SUCURSAL
# ================================

ID_SUCURSAL = int(os.getenv("ID_SUCURSAL", "99"))

# ================================
# MODO DE EJECUCIÓN
# ================================

# False = modo normal (procesa hoy o últimos N días)
# True  = modo histórico (procesa un rango de fechas)
HISTORICAL_MODE = True

# Fecha inicial del histórico (YYYY-MM-DD)
# Obligatoria si HISTORICAL_MODE = True
HISTORICAL_START_DATE = "2009-08-14"

# Fecha final del histórico
# None = hasta hoy
# Usar fecha específica para reprocesos controlados
HISTORICAL_END_DATE = "2009-09-01"
# Ejemplo: "2015-12-31"


# ================================
# COMPORTAMIENTO GENERAL DEL BOT
# ================================

# En modo normal: cuántos días hacia atrás reprocesar
REPROCESS_DAYS = 1

# Tamaño del batch para UPSERT
UPSERT_BATCH_SIZE = 500


# ================================
# CONTROL DE ERRORES / REINTENTOS
# ================================

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


# ================================
# AUDITORÍA
# ================================

ENABLE_AUDIT = True

# Tolerancia para comparación de montos
AUDIT_TOLERANCE = 0.01


# ================================
# LOGGING
# ================================

LOG_LEVEL = "INFO"
LOG_FILE = "logs/bot.log"


# ================================
# FLAGS OPERATIVOS
# ================================

DRY_RUN = False
RUN_LOCAL_ONLY = False
