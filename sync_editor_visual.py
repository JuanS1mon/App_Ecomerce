#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar automáticamente los archivos del Editor Visual
entre las dos ubicaciones del proyecto.
"""

import os
import shutil
import sys
from pathlib import Path

def main():
    # Rutas de los archivos del Editor Visual
    source_file = Path("c:/Users/PCJuan/Desktop/sql_app/static/html/editor_visual.html")
    target_file = Path("c:/Users/PCJuan/Desktop/sql_app/sql_app/static/html/editor_visual.html")
    
    print("🔄 Sincronizando archivos del Editor Visual...")
    print(f"📁 Origen: {source_file}")
    print(f"📁 Destino: {target_file}")
    
    # Verificar que el archivo origen existe
    if not source_file.exists():
        print(f"❌ Error: Archivo origen no encontrado: {source_file}")
        sys.exit(1)
    
    # Crear directorio destino si no existe
    target_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Copiar archivo
        shutil.copy2(source_file, target_file)
        print("✅ Sincronización completada exitosamente")
        print(f"📊 Tamaño del archivo: {source_file.stat().st_size:,} bytes")
        
    except Exception as e:
        print(f"❌ Error durante la sincronización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
