import re

# Analizar qué caracteres mal codificados existen realmente
with open('static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar secuencias de caracteres que contienen ├ ó ┬
bad_sequences = re.findall(r'[├┬][^a-zA-Z0-9\s]*', content)

print('Secuencias mal codificadas encontradas:')
unique_sequences = list(set(bad_sequences))
for seq in unique_sequences[:20]:  # Mostrar solo las primeras 20
    print(f'  "{seq}"')

print(f'\nTotal de secuencias únicas: {len(unique_sequences)}')

# También buscar caracteres individuales no ASCII
bad_chars = []
for char in content:
    if ord(char) > 127:  # Caracteres no ASCII
        if char not in bad_chars:
            bad_chars.append(char)

print('\nCaracteres no ASCII encontrados:')
for char in bad_chars[:30]:  # Mostrar solo los primeros 30
    print(f'  "{char}" (U+{ord(char):04X})')

# Crear un mapeo más preciso
print('\nCreando mapeo de corrección...')
corrections = {}
for seq in unique_sequences:
    if len(seq) == 2:  # Solo secuencias de 2 caracteres
        # Intentar decodificar como latin1 y luego re-encodear como utf8
        try:
            # Los caracteres ├ y ┬ son indicadores de que el archivo fue mal codificado
            # Necesitamos mapear manualmente los más comunes
            pass
        except:
            pass

# Mapeo manual basado en patrones comunes
manual_map = {
    '├¡': 'á',
    '├©': 'é',
    '├*': 'í',
    '├│': 'ó',
    '├║': 'ú',
    '├ü': 'ü',
    '├ç': 'ç',
    '├Ç': 'Ç',
    '├▒': 'ñ',
    '├æ': 'Ñ',
    '┬┐': '¿',
    '├┐': '¿',
    '├┤': 'ñ',
    '├æ': 'Ñ',
    '├ü': 'ü',
    '├Ü': 'Ü',
    '├¡': 'á',
    '├É': 'Á',
    '├®': 'é',
    '├ë': 'É',
    '├*': 'í',
    '├*': 'Í',
    '├│': 'ó',
    '├ô': 'Ó',
    '├║': 'ú',
    '├£': 'Ú',
    '├▒': 'ñ',
    '├æ': 'Ñ',
    '├ç': 'ç',
    '├Ç': 'Ç'
}

print('Mapeo manual disponible:')
for wrong, correct in list(manual_map.items())[:10]:
    print(f'  "{wrong}" -> "{correct}"')