#!/usr/bin/env python3
"""
Script para ejecutar el servidor de forma controlada y capturar errores
"""
import sys
import os
import traceback

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_server_with_error_handling():
    """Ejecuta el servidor con manejo de errores detallado"""
    print("🚀 Iniciando servidor con manejo de errores detallado...")

    try:
        # Importar el módulo main
        print("📦 Importando módulo main...")
        import main
        print("✅ Módulo main importado correctamente")

        # Verificar que la app existe
        print("🔍 Verificando aplicación FastAPI...")
        app = getattr(main, 'app', None)
        if app is None:
            print("❌ No se encontró la aplicación 'app' en el módulo main")
            return
        print("✅ Aplicación FastAPI encontrada")

        # Intentar ejecutar el servidor manualmente con uvicorn
        print("🖥️  Iniciando servidor uvicorn...")
        import uvicorn

        # Configurar logging para capturar más detalles
        import logging
        logging.basicConfig(level=logging.DEBUG)

        # Ejecutar con timeout simulado (detendremos manualmente)
        print("⏰ Ejecutando servidor por 5 segundos...")

        # Usar un enfoque diferente: ejecutar en un thread separado
        import threading
        import time

        server_started = False
        server_error = None

        def run_uvicorn():
            nonlocal server_started, server_error
            try:
                server_started = True
                print("🟢 Servidor iniciado en thread separado")
                uvicorn.run(
                    app=app,
                    host="0.0.0.0",
                    port=8000,
                    reload=False,
                    log_level="debug",
                    access_log=True,
                    use_colors=True,
                )
            except Exception as e:
                server_error = e
                print(f"❌ Error en thread del servidor: {e}")
                traceback.print_exc()

        # Iniciar servidor en thread
        server_thread = threading.Thread(target=run_uvicorn, daemon=True)
        server_thread.start()

        # Esperar a que el servidor se inicie
        time.sleep(2)

        if server_started:
            print("✅ Servidor aparentemente iniciado correctamente")
            print("⏳ Esperando 3 segundos para ver si se mantiene...")
            time.sleep(3)

            if server_thread.is_alive():
                print("✅ Servidor sigue ejecutándose después de 3 segundos")
                print("🛑 Deteniendo servidor...")
                # No hay forma fácil de detener uvicorn desde otro thread
                # El servidor debería detenerse solo
            else:
                print("❌ Servidor se detuvo prematuramente")
                if server_error:
                    print(f"Error del servidor: {server_error}")
        else:
            print("❌ Servidor no se inició correctamente")

    except Exception as e:
        print(f"❌ Error general: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_server_with_error_handling()