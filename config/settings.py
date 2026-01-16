# config/settings.py

from datetime import date

# ================================
# MODO DE EJECUCIÓN
# ================================

# False = modo normal (procesa hoy o últimos N días)
# True  = modo histórico (bootstrap desde fecha de apertura)
HISTORICAL_MODE = True

# Fecha de apertura de la sucursal (YYYY-MM-DD)
HISTORICAL_START_DATE = "2026-01-13"

# Fecha final del histórico
# None = hasta hoy
HISTORICAL_END_DATE = None


# ================================
# COMPORTAMIENTO GENERAL DEL BOT
# ================================

# En modo normal: cuántos días hacia atrás reprocesar
REPROCESS_DAYS = 1

# Tamaño del batch para UPSERT (executemany)
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

# Tolerancia para comparación de montos (redondeos)
AUDIT_TOLERANCE = 0.01


# ================================
# LOGGING
# ================================

LOG_LEVEL = "INFO"
LOG_FILE = "logs/bot.log"


# ================================
# FLAGS OPERATIVOS
# ================================

# True  = no ejecuta INSERT/DELETE (solo prueba)
# False = ejecución real
DRY_RUN = False

# True  = solo BD local
# False = BD local + VPS
RUN_LOCAL_ONLY = False
