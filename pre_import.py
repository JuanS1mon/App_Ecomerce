"""
Pre-importación de typing_extensions desde el entorno virtual correcto.
Este módulo DEBE ejecutarse ANTES de cualquier import de FastAPI/Pydantic.
"""
import sys
import os

print("[PRE-IMPORT] Verificando typing_extensions...")

# Asegurar que /agents/python NO esté en sys.path
sys.path = [p for p in sys.path if '/agents/python' not in p]

# Forzar la importación desde el entorno virtual
try:
    import typing_extensions
    print(f"[PRE-IMPORT] typing_extensions cargado desde: {typing_extensions.__file__}")
    
    # Verificar que tiene Sentinel
    if hasattr(typing_extensions, 'Sentinel'):
        print("[PRE-IMPORT] ✓ Sentinel encontrado en typing_extensions")
    else:
        print("[PRE-IMPORT] ✗ ERROR: Sentinel NO encontrado")
        # Recargar desde la ruta correcta
        if 'typing_extensions' in sys.modules:
            del sys.modules['typing_extensions']
        # Forzar import desde site-packages
        venv_path = [p for p in sys.path if 'site-packages' in p][0]
        sys.path.insert(0, venv_path)
        import typing_extensions
        print(f"[PRE-IMPORT] Recargado desde: {typing_extensions.__file__}")
        
except ImportError as e:
    print(f"[PRE-IMPORT] ERROR al importar typing_extensions: {e}")
    raise
