#!/usr/bin/env python3
"""
Script para arreglar automáticamente las importaciones duplicadas e inconsistentes
Este script:
1. Detecta importaciones duplicadas
2. Convierte importaciones relativas inconsistentes a absolutas
3. Remueve importaciones redundantes
4. Estandariza el orden de las importaciones
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_fix.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ImportFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.sql_app_root = self.project_root / "sql_app"
        
        # Patrones de importaciones problemáticas
        self.problematic_patterns = [
            r'from\s+\.\.\.?Services\.security\.security\s+import',
            r'from\s+Services\.security\.security\s+import',
            r'from\s+\.\.\.?db\.database\s+import',
            r'from\s+db\.database\s+import',
            r'from\s+\.\.\.?db\.schemas\.config\.Usuarios\s+import',
            r'from\s+\.\.\.?db\.models\.config\.usuarios\s+import',
        ]
        
        # Mapeo de importaciones estándar
        self.import_mapping = {
            # Seguridad
            r'from\s+\.\.\.?Services\.security\.security\s+import': 'from sql_app.Services.security.security import',
            r'from\s+Services\.security\.security\s+import': 'from sql_app.Services.security.security import',
            
            # Base de datos
            r'from\s+\.\.\.?db\.database\s+import': 'from sql_app.db.database import',
            r'from\s+db\.database\s+import': 'from sql_app.db.database import',
            
            # Esquemas
            r'from\s+\.\.\.?db\.schemas\.config\.Usuarios\s+import': 'from sql_app.db.schemas.config.Usuarios import',
            
            # Modelos
            r'from\s+\.\.\.?db\.models\.config\.usuarios\s+import': 'from sql_app.db.models.config.usuarios import',
            r'from\s+\.\.\.?db\.models\.config\.activityLog\s+import': 'from sql_app.db.models.config.activityLog import',
            
            # Roles
            r'from\s+\.\.\.?db\.schemas\.config\.roles\s+import': 'from sql_app.db.schemas.config.roles import',
            
            # CRUD
            r'from\s+\.\.\.?db\.crud\.tablas\s+import': 'from sql_app.db.crud.tablas import',
        }
        
        # Importaciones comunes que se pueden consolidar
        self.consolidatable_imports = {
            'sql_app.Services.security.security': [
                'get_current_user', 'require_admin', 'encriptar_clave', 'get_password_hash'
            ],
            'fastapi': [
                'APIRouter', 'Depends', 'Form', 'HTTPException', 'Request', 'status', 'FastAPI'
            ],
            'fastapi.responses': [
                'HTMLResponse', 'RedirectResponse', 'JSONResponse'
            ],
            'typing': [
                'List', 'Optional', 'Dict', 'Any'
            ]
        }
    
    def find_python_files(self) -> List[Path]:
        """Encuentra todos los archivos Python en el proyecto"""
        python_files = []
        for root, dirs, files in os.walk(self.sql_app_root):
            # Ignorar directorios de cache y logs
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'logs', '.git']]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def analyze_file_imports(self, file_path: Path) -> Dict[str, List[str]]:
        """Analiza las importaciones de un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error leyendo {file_path}: {e}")
            return {}
        
        import_lines = []
        duplicates = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('from ') or line.startswith('import '):
                import_lines.append((i, line))
        
        # Detectar duplicados
        seen_imports = set()
        for line_num, import_line in import_lines:
            if import_line in seen_imports:
                duplicates.append((line_num, import_line))
            else:
                seen_imports.add(import_line)
        
        return {
            'imports': import_lines,
            'duplicates': duplicates,
            'content': content,
            'lines': lines
        }
    
    def fix_file_imports(self, file_path: Path) -> bool:
        """Arregla las importaciones de un archivo específico"""
        analysis = self.analyze_file_imports(file_path)
        if not analysis:
            return False
        
        content = analysis['content']
        lines = analysis['lines']
        duplicates = analysis['duplicates']
        
        # Si no hay problemas, no hacer nada
        if not duplicates and not any(re.search(pattern, content) for pattern in self.problematic_patterns):
            return False
        
        logger.info(f"Arreglando importaciones en: {file_path}")
        
        # Procesar líneas
        new_lines = []
        import_section = []
        non_import_section = []
        in_import_section = True
        processed_imports = set()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Detectar fin de sección de importaciones
            if in_import_section and stripped and not stripped.startswith(('from ', 'import ', '#', '"""', "'''")):
                in_import_section = False
            
            if in_import_section and (stripped.startswith('from ') or stripped.startswith('import ')):
                # Normalizar importación
                normalized = self.normalize_import(stripped)
                if normalized and normalized not in processed_imports:
                    import_section.append(normalized)
                    processed_imports.add(normalized)
            else:
                if in_import_section:
                    # Mantener comentarios y docstrings en la sección de importaciones
                    if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''") or not stripped:
                        import_section.append(line)
                else:
                    non_import_section.append(line)
        
        # Consolidar importaciones similares
        consolidated_imports = self.consolidate_imports(import_section)
        
        # Ordenar importaciones
        sorted_imports = self.sort_imports(consolidated_imports)
        
        # Construir nuevo contenido
        new_content_lines = []
        
        # Agregar docstring inicial si existe
        if lines and (lines[0].strip().startswith('"""') or lines[0].strip().startswith("'''")):
            # Encontrar el final del docstring
            quote_type = '"""' if lines[0].strip().startswith('"""') else "'''"
            docstring_lines = []
            i = 0
            while i < len(lines):
                docstring_lines.append(lines[i])
                if i > 0 and quote_type in lines[i]:
                    break
                i += 1
            new_content_lines.extend(docstring_lines)
            new_content_lines.append('')
        
        # Agregar importaciones ordenadas
        new_content_lines.extend(sorted_imports)
        
        # Agregar línea en blanco entre importaciones y código
        if sorted_imports and non_import_section:
            new_content_lines.append('')
        
        # Agregar resto del contenido
        new_content_lines.extend(non_import_section)
        
        # Escribir archivo
        try:
            new_content = '\n'.join(new_content_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"✓ Archivo corregido: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error escribiendo {file_path}: {e}")
            return False
    
    def normalize_import(self, import_line: str) -> str:
        """Normaliza una línea de importación"""
        import_line = import_line.strip()
        
        # Aplicar mapeos de normalización
        for pattern, replacement in self.import_mapping.items():
            if re.match(pattern, import_line):
                import_line = re.sub(pattern, replacement, import_line)
                break
        
        return import_line
    
    def consolidate_imports(self, import_lines: List[str]) -> List[str]:
        """Consolida importaciones del mismo módulo"""
        imports_by_module = {}
        other_imports = []
        
        for line in import_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                other_imports.append(line)
                continue
            
            # Extraer módulo e items importados
            if line.startswith('from '):
                match = re.match(r'from\s+([^\s]+)\s+import\s+(.+)', line)
                if match:
                    module = match.group(1)
                    items = [item.strip() for item in match.group(2).split(',')]
                    
                    if module not in imports_by_module:
                        imports_by_module[module] = set()
                    imports_by_module[module].update(items)
                else:
                    other_imports.append(line)
            else:
                other_imports.append(line)
        
        # Reconstruir importaciones consolidadas
        consolidated = []
        for module, items in imports_by_module.items():
            if len(items) == 1:
                consolidated.append(f"from {module} import {list(items)[0]}")
            else:
                items_str = ', '.join(sorted(items))
                if len(items_str) > 80:  # Línea muy larga, usar múltiples líneas
                    consolidated.append(f"from {module} import (")
                    for i, item in enumerate(sorted(items)):
                        if i == len(items) - 1:
                            consolidated.append(f"    {item}")
                        else:
                            consolidated.append(f"    {item},")
                    consolidated.append(")")
                else:
                    consolidated.append(f"from {module} import {items_str}")
        
        return other_imports + consolidated
    
    def sort_imports(self, import_lines: List[str]) -> List[str]:
        """Ordena las importaciones según las mejores prácticas"""
        stdlib_imports = []
        third_party_imports = []
        local_imports = []
        comments_and_empty = []
        
        stdlib_modules = {
            'os', 'sys', 'logging', 'datetime', 'typing', 're', 'json', 
            'pathlib', 'collections', 'functools', 'itertools'
        }
        
        for line in import_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                comments_and_empty.append(line)
                continue
            
            # Determinar tipo de importación
            if line.startswith('from ') or line.startswith('import '):
                if 'sql_app.' in line:
                    local_imports.append(line)
                elif any(stdlib in line for stdlib in stdlib_modules):
                    stdlib_imports.append(line)
                else:
                    third_party_imports.append(line)
            else:
                comments_and_empty.append(line)
        
        # Ordenar cada grupo
        stdlib_imports.sort()
        third_party_imports.sort()
        local_imports.sort()
        
        # Combinar con separadores
        result = []
        
        if comments_and_empty:
            result.extend(comments_and_empty)
        
        if stdlib_imports:
            if result and result[-1]:  # Agregar línea vacía si hay contenido previo
                result.append('')
            result.extend(stdlib_imports)
        
        if third_party_imports:
            if result and result[-1]:
                result.append('')
            result.extend(third_party_imports)
        
        if local_imports:
            if result and result[-1]:
                result.append('')
            result.extend(local_imports)
        
        return result
    
    def fix_all_files(self) -> Dict[str, int]:
        """Arregla las importaciones en todos los archivos del proyecto"""
        python_files = self.find_python_files()
        stats = {
            'total_files': len(python_files),
            'fixed_files': 0,
            'error_files': 0
        }
        
        logger.info(f"Procesando {len(python_files)} archivos Python...")
        
        for file_path in python_files:
            try:
                if self.fix_file_imports(file_path):
                    stats['fixed_files'] += 1
            except Exception as e:
                stats['error_files'] += 1
                logger.error(f"Error procesando {file_path}: {e}")
        
        return stats
    
    def generate_report(self) -> str:
        """Genera un reporte de las importaciones problemáticas"""
        python_files = self.find_python_files()
        report = []
        
        report.append("REPORTE DE IMPORTACIONES PROBLEMÁTICAS")
        report.append("=" * 50)
        
        total_issues = 0
        
        for file_path in python_files:
            analysis = self.analyze_file_imports(file_path)
            if not analysis:
                continue
            
            issues = []
            
            # Verificar duplicados
            if analysis['duplicates']:
                issues.append(f"  - {len(analysis['duplicates'])} importaciones duplicadas")
                total_issues += len(analysis['duplicates'])
            
            # Verificar patrones problemáticos
            content = analysis['content']
            for pattern in self.problematic_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    issues.append(f"  - {len(matches)} importaciones inconsistentes: {pattern}")
                    total_issues += len(matches)
            
            if issues:
                relative_path = file_path.relative_to(self.project_root)
                report.append(f"\n{relative_path}:")
                report.extend(issues)
        
        report.append(f"\nTOTAL DE PROBLEMAS ENCONTRADOS: {total_issues}")
        
        return '\n'.join(report)

def main():
    """Función principal"""
    project_root = r"c:\Users\PCJuan\Desktop\sql_app"
    
    if not os.path.exists(project_root):
        logger.error(f"No se encontró el directorio del proyecto: {project_root}")
        return
    
    fixer = ImportFixer(project_root)
    
    print("ANÁLISIS DE IMPORTACIONES PROBLEMÁTICAS")
    print("=" * 50)
    
    # Generar reporte antes de arreglar
    report = fixer.generate_report()
    print(report)
    
    print("\n" + "=" * 50)
    print("INICIANDO CORRECCIÓN DE IMPORTACIONES...")
    print("=" * 50)
    
    # Arreglar archivos
    stats = fixer.fix_all_files()
    
    print(f"\nRESULTADOS:")
    print(f"- Archivos procesados: {stats['total_files']}")
    print(f"- Archivos corregidos: {stats['fixed_files']}")
    print(f"- Archivos con errores: {stats['error_files']}")
    
    # Guardar reporte en archivo
    with open(os.path.join(project_root, 'import_fix_report.txt'), 'w', encoding='utf-8') as f:
        f.write(report)
        f.write(f"\n\nRESULTADOS DE CORRECCIÓN:\n")
        f.write(f"- Archivos procesados: {stats['total_files']}\n")
        f.write(f"- Archivos corregidos: {stats['fixed_files']}\n")
        f.write(f"- Archivos con errores: {stats['error_files']}\n")
    
    print(f"\nReporte guardado en: import_fix_report.txt")
    logger.info("Proceso completado")

if __name__ == "__main__":
    main()
