import os
import chardet

def detect_encoding(file_path):
    """Detecta la codificación de un archivo"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'], result['confidence']

def fix_encoding(file_path):
    """Intenta arreglar la codificación de un archivo HTML"""
    try:
        # Leer el archivo como bytes
        with open(file_path, 'rb') as f:
            raw_content = f.read()

        # Detectar la codificación
        detected_encoding, confidence = detect_encoding(file_path)
        print(f"Archivo: {file_path}")
        print(f"Codificación detectada: {detected_encoding} (confianza: {confidence:.2f})")

        # Intentar diferentes estrategias de decodificación
        strategies = [
            ('utf-8', 'ignore'),
            ('latin1', 'ignore'),
            ('cp1252', 'ignore'),
            ('iso-8859-1', 'ignore'),
        ]

        best_result = None
        best_score = 0

        for encoding, errors in strategies:
            try:
                decoded = raw_content.decode(encoding, errors=errors)

                # Calcular una puntuación basada en caracteres válidos
                valid_chars = sum(1 for c in decoded if c.isalnum() or c in ' \n\t<>/"\'=-_.,:;()[]{}')
                score = valid_chars / len(decoded) if decoded else 0

                if score > best_score:
                    best_score = score
                    best_result = decoded
                    print(f"  Mejor resultado con {encoding}: score {score:.3f}")

            except Exception as e:
                print(f"  Error con {encoding}: {e}")
                continue

        if best_result:
            # Re-codificar como UTF-8
            fixed_content = best_result.encode('utf-8')

            # Crear backup
            backup_path = file_path + '.backup'
            with open(backup_path, 'wb') as f:
                f.write(raw_content)

            # Escribir el archivo corregido
            with open(file_path, 'wb') as f:
                f.write(fixed_content)

            print(f"Archivo corregido: {file_path}")
            return True
        else:
            print(f"No se pudo corregir: {file_path}")
            return False

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

# Archivos a corregir
files_to_fix = [
    'static/carrito.html',
    'static/index.html'
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        fix_encoding(file_path)
    else:
        print(f"Archivo no encontrado: {file_path}")