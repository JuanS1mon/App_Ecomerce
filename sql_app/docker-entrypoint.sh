#!/bin/bash
# ==========================================
# DOCKER ENTRYPOINT SCRIPT
# ==========================================

set -e

echo "🚀 Iniciando aplicación FastAPI..."

# Función para esperar a que la base de datos esté lista
wait_for_database() {
    echo "⏳ Esperando a que la base de datos esté ready..."
    
    # Extraer información de conexión desde DATABASE_URL
    HOST="database"
    PORT="1433"
    
    echo "🔗 Esperando conexión a: $HOST:$PORT"
    
    # Esperar hasta 120 segundos por la base de datos
    timeout=120
    while [ $timeout -gt 0 ]; do
        if nc -z "$HOST" "$PORT" 2>/dev/null; then
            echo "✅ Base de datos disponible!"
            sleep 5  # Esperar un poco más para que esté completamente lista
            return 0
        fi
        echo "⏳ Esperando base de datos... ($timeout segundos restantes)"
        sleep 3
        timeout=$((timeout-3))
    done
    
    echo "❌ Timeout: No se pudo conectar a la base de datos"
    exit 1
}

# Función principal
main() {
    echo "🐳 Iniciando contenedor FastAPI..."
    echo "📅 Fecha: $(date)"
    echo "🌍 Entorno: ${ENVIRONMENT:-development}"
    
    # Esperar a que la base de datos esté lista
    wait_for_database
    
    echo "🎉 Inicialización completada!"
    echo "🚀 Iniciando servidor FastAPI..."
    
    # Ejecutar el comando pasado como argumentos
    exec "$@"
}

# Verificar si se está ejecutando directamente
if [ "${1#-}" != "$1" ] || [ "$1" = "uvicorn" ] || [ "$1" = "gunicorn" ]; then
    main "$@"
else
    # Si se pasa otro comando, ejecutarlo directamente
    exec "$@"
fi
