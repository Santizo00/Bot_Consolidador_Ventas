#!/bin/bash

# ======================================
# Script de ejecución del Bot Consolidador
# ======================================

echo "Iniciando Bot Consolidador de Ventas..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar el bot
python3 main.py

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "El bot finalizó con errores (exit code $EXIT_CODE)"
else
    echo "El bot finalizó correctamente"
fi

exit $EXIT_CODE
