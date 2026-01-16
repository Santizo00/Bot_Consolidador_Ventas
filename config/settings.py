# config/settings.py

# ================================
# COMPORTAMIENTO GENERAL DEL BOT
# ================================

REPROCESS_DAYS = 1

UPSERT_BATCH_SIZE = 500

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

ENABLE_AUDIT = True
AUDIT_TOLERANCE = 0.01

LOG_LEVEL = "INFO"
LOG_FILE = "logs/bot.log"

DRY_RUN = False
RUN_LOCAL_ONLY = False
