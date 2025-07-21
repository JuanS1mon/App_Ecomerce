import re
import os

# Leer el archivo navbar.html
navbar_path = os.path.join('sql_app', 'static', 'components', 'navbar.html')

try:
    with open(navbar_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer el JavaScript del archivo
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    
    if script_match:
        js_code = script_match.group(1)
        
        print('Verificando estructura del JavaScript del navbar...')
        print(f'Longitud del código: {len(js_code)} caracteres')
        print(f'Número de líneas: {len(js_code.splitlines())}')
        
        # Verificaciones básicas
        errors = []
        
        # Verificar paréntesis balanceados
        paren_count = js_code.count('(') - js_code.count(')')
        if paren_count != 0:
            errors.append(f"Paréntesis desbalanceados: {paren_count}")
        
        # Verificar llaves balanceadas
        brace_count = js_code.count('{') - js_code.count('}')
        if brace_count != 0:
            errors.append(f"Llaves desbalanceadas: {brace_count}")
        
        # Verificar corchetes balanceados
        bracket_count = js_code.count('[') - js_code.count(']')
        if bracket_count != 0:
            errors.append(f"Corchetes desbalanceados: {bracket_count}")
        
        # Buscar patrones problemáticos
        if '})();' in js_code:
            print('✅ Encontrado patrón IIFE correcto')
        else:
            errors.append("No se encontró el patrón IIFE })(); al final")
        
        if js_code.strip().startswith('(function()'):
            print('✅ Inicio de IIFE correcto')
        else:
            errors.append("No empieza con (function()")
        
        # Buscar palabras clave problemáticas
        if 'const ' in js_code or 'let ' in js_code:
            errors.append("Contiene 'const' o 'let' (debería usar 'var' para ES5)")
        
        if '=>' in js_code:
            errors.append("Contiene arrow functions (debería usar function())")
        
        if '`' in js_code:
            errors.append("Contiene template literals (debería usar concatenación)")
        
        if errors:
            print('❌ Problemas encontrados:')
            for error in errors:
                print(f'  - {error}')
        else:
            print('✅ Estructura del JavaScript parece correcta')
            
        # Mostrar las primeras y últimas líneas
        lines = js_code.splitlines()
        print(f'\nPrimeras 5 líneas:')
        for i, line in enumerate(lines[:5]):
            print(f'  {i+1}: {line.strip()}')
        
        print(f'\nÚltimas 5 líneas:')
        for i, line in enumerate(lines[-5:], len(lines)-4):
            print(f'  {i}: {line.strip()}')
            
    else:
        print('❌ No se encontró script en el archivo navbar.html')
        
except Exception as e:
    print(f'❌ Error leyendo el archivo: {e}')
