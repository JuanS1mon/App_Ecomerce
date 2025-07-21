import re
import os

def check_js_syntax(file_path):
    """Verificar sintaxis básica de JavaScript"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer solo el JavaScript
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        print("No se encontró script en el archivo")
        return
    
    js_code = script_match.group(1)
    lines = js_code.split('\n')
    
    print(f"Analizando {len(lines)} líneas de JavaScript...")
    
    # Contadores para verificar balance
    paren_stack = []
    brace_stack = []
    bracket_stack = []
    
    errors = []
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith('//'):
            continue
            
        # Revisar cada carácter
        for j, char in enumerate(line):
            if char == '(':
                paren_stack.append((i, j, char))
            elif char == ')':
                if not paren_stack:
                    errors.append(f"Línea {i}, Col {j}: ')' sin '(' correspondiente")
                else:
                    paren_stack.pop()
            elif char == '{':
                brace_stack.append((i, j, char))
            elif char == '}':
                if not brace_stack:
                    errors.append(f"Línea {i}, Col {j}: '}}' sin '{{' correspondiente")
                else:
                    brace_stack.pop()
            elif char == '[':
                bracket_stack.append((i, j, char))
            elif char == ']':
                if not bracket_stack:
                    errors.append(f"Línea {i}, Col {j}: ']' sin '[' correspondiente")
                else:
                    bracket_stack.pop()
    
    # Verificar que todo esté balanceado
    if paren_stack:
        for line_num, col, char in paren_stack:
            errors.append(f"Línea {line_num}, Col {col}: '(' sin cerrar")
    
    if brace_stack:
        for line_num, col, char in brace_stack:
            errors.append(f"Línea {line_num}, Col {col}: '{{' sin cerrar")
    
    if bracket_stack:
        for line_num, col, char in bracket_stack:
            errors.append(f"Línea {line_num}, Col {col}: '[' sin cerrar")
    
    # Buscar patrones problemáticos comunes
    for i, line in enumerate(lines, 1):
        # Función seguida directamente por paréntesis
        if re.search(r'function\s*\w*\s*\(\s*\)\s*\)\s*{', line):
            errors.append(f"Línea {i}: Posible paréntesis extra después de declaración de función")
        
        # Paréntesis dobles inesperados
        if ')(' in line and 'function(' not in line:
            errors.append(f"Línea {i}: Posible ')(' problemático")
        
        # Comas seguidas de paréntesis de cierre
        if ',)' in line:
            errors.append(f"Línea {i}: Coma seguida de paréntesis de cierre ',)'")
    
    if errors:
        print("❌ Errores encontrados:")
        for error in errors[:10]:  # Mostrar solo los primeros 10
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... y {len(errors) - 10} errores más")
    else:
        print("✅ No se encontraron errores de sintaxis obvios")
    
    # Mostrar información de balance
    print(f"\nBalance final:")
    print(f"  Paréntesis abiertos: {len(paren_stack)}")
    print(f"  Llaves abiertas: {len(brace_stack)}")
    print(f"  Corchetes abiertos: {len(bracket_stack)}")

if __name__ == "__main__":
    navbar_path = os.path.join('sql_app', 'static', 'components', 'navbar.html')
    check_js_syntax(navbar_path)
