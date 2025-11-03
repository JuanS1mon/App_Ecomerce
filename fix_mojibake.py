import os

def fix_mojibake(file_path):
    """Corrige archivos con codificación mojibake (doble codificación)"""
    try:
        # Leer como bytes
        with open(file_path, 'rb') as f:
            raw_bytes = f.read()

        # Crear backup
        backup_path = file_path + '.original'
        with open(backup_path, 'wb') as f:
            f.write(raw_bytes)

        # El problema parece ser que el archivo fue codificado como latin1/cp1252
        # pero interpretado como UTF-8, creando "mojibake"

        # Intentar decodificar como UTF-8 primero (ignorando errores)
        try:
            step1 = raw_bytes.decode('utf-8', errors='ignore')
        except:
            print(f"No se pudo decodificar como UTF-8: {file_path}")
            return False

        # Ahora re-codificar como latin1 (que es similar a cp1252)
        try:
            step2_bytes = step1.encode('latin1', errors='ignore')
        except:
            print(f"No se pudo re-codificar como latin1: {file_path}")
            return False

        # Finalmente, decodificar como UTF-8
        try:
            final_content = step2_bytes.decode('utf-8', errors='ignore')
        except:
            print(f"No se pudo decodificar final como UTF-8: {file_path}")
            return False

        # Verificar que el resultado tenga sentido
        # Debería contener etiquetas HTML normales
        if '<!DOCTYPE html>' in final_content or '<html' in final_content:
            # Escribir el archivo corregido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"Archivo corregido exitosamente: {file_path}")
            return True
        else:
            print(f"El resultado no parece HTML válido: {file_path}")
            return False

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

# Función alternativa: intentar diferentes combinaciones
def fix_mojibake_alternative(file_path):
    """Método alternativo para corregir mojibake"""
    try:
        with open(file_path, 'rb') as f:
            raw_bytes = f.read()

        # Crear backup
        backup_path = file_path + '.alt_backup'
        with open(backup_path, 'wb') as f:
            f.write(raw_bytes)

        # Método alternativo: asumir que fue cp1252 → UTF-8 mal interpretado
        # Decodificar como cp1252 directamente
        try:
            content = raw_bytes.decode('cp1252', errors='ignore')
            # Verificar si tiene sentido
            if 'html' in content.lower() and ('<' in content and '>' in content):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Archivo corregido con método alternativo: {file_path}")
                return True
        except:
            pass

        # Otro método: UTF-8 → latin1 → UTF-8
        try:
            step1 = raw_bytes.decode('utf-8', errors='replace')
            step2 = step1.encode('latin1', errors='replace')
            final = step2.decode('utf-8', errors='replace')

            if '<!DOCTYPE' in final or '<html' in final:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final)
                print(f"Archivo corregido con método UTF-8→latin1→UTF-8: {file_path}")
                return True
        except:
            pass

        print(f"No se pudo corregir con métodos alternativos: {file_path}")
        return False

    except Exception as e:
        print(f"Error en método alternativo para {file_path}: {e}")
        return False

# Archivos a corregir
files_to_fix = [
    'static/carrito.html',
    'static/index.html'
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        print(f"Procesando: {file_path}")
        # Intentar método principal
        if not fix_mojibake(file_path):
            # Si falla, intentar método alternativo
            fix_mojibake_alternative(file_path)
    else:
        print(f"Archivo no encontrado: {file_path}")