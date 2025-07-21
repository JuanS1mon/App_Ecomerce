import re
import os

def find_line_431(file_path):
    """Encontrar exactamente qué hay en la línea 431 del JavaScript"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer solo el JavaScript
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        print("No se encontró script")
        return
    
    js_code = script_match.group(1)
    lines = js_code.split('\n')
    
    print(f"Total de líneas en JavaScript: {len(lines)}")
    
    if len(lines) >= 431:
        print(f"Línea 431: '{lines[430]}'")  # 430 porque es índice 0
        
        # Mostrar contexto alrededor
        print("\nContexto:")
        for i in range(max(0, 428), min(len(lines), 435)):
            marker = ">>> " if i == 430 else "    "
            print(f"{marker}{i+1}: {lines[i]}")
    else:
        print(f"El archivo solo tiene {len(lines)} líneas de JavaScript")

if __name__ == "__main__":
    navbar_path = os.path.join('sql_app', 'static', 'components', 'navbar.html')
    find_line_431(navbar_path)
