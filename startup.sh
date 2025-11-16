#!/bin/bash
# ============================================================================
# Script de inicio para Azure App Service
# Limpia PYTHONPATH ANTES de que Gunicorn inicie
# ============================================================================

echo "[STARTUP.SH] Iniciando aplicación..."
echo "[STARTUP.SH] PYTHONPATH original: $PYTHONPATH"

# Remover /agents/python del PYTHONPATH
export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v '/agents/python' | tr '\n' ':' | sed 's/:$//')

echo "[STARTUP.SH] PYTHONPATH limpio: $PYTHONPATH"

# Verificar que el entorno virtual existe
if [ -d "$ANTENV" ] || [ -d "antenv" ]; then
    echo "[STARTUP.SH] Entorno virtual encontrado"
else
    echo "[STARTUP.SH] WARNING: No se encontró entorno virtual"
fi

# Ejecutar Gunicorn con la configuración personalizada
echo "[STARTUP.SH] Iniciando Gunicorn..."
python3 -m gunicorn main:app -c gunicorn.conf.py
