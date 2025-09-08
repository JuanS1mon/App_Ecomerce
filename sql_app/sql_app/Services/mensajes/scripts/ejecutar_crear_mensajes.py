#!/usr/bin/env python3
"""
Script para ejecutar crear_mensajes_db.py desde la nueva ubicación
"""

import sys
import os

# Cambiar al directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Ejecutar el script original
if __name__ == "__main__":
    # Importar y ejecutar
    from crear_mensajes_db import crear_mensajes_prueba
    crear_mensajes_prueba()
