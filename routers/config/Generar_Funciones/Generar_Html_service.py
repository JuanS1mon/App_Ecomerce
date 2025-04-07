def generate_html_for_service(module_name, field_names, field_types):
    """
    Genera un archivo HTML para un servicio, con una interfaz mejorada y un archivo JS separado.
    
    Args:
        module_name: Nombre del módulo
        field_names: Lista de nombres de campos
        field_types: Lista de tipos de campos
    
    Returns:
        tuple: (html_content, js_content) - Contenido HTML y JavaScript generados
    """
    from yattag import Doc
    from bs4 import BeautifulSoup

    doc, tag, text, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')

    # Construimos el HTML con diseño mejorado
    with tag('html', lang='es'):
        with tag('head'):
            doc.stag('meta', charset='UTF-8')
            doc.stag('meta', name='viewport', content='width=device-width, initial-scale=1.0')
            line('title', f'Gestión de {module_name.capitalize()}')
            doc.stag('script', src='https://cdn.tailwindcss.com')
            doc.stag('link', rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css')
            # Añadimos estilos personalizados
            doc.asis("""
<style>
    .fade-in {
        animation: fadeIn 0.3s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        z-index: 9999;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .toast-success {
        background-color: #10B981;
        color: white;
    }
    .toast-error {
        background-color: #EF4444;
        color: white;
    }
    .input-field:focus {
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
        outline: none;
    }
    .hover-raise {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .hover-raise:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .table-container {
        overflow-x: auto;
        max-height: 600px;
        overflow-y: auto;
    }
    /* Estilizando scrollbar */
    .table-container::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    .table-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    .table-container::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 10px;
    }
    .table-container::-webkit-scrollbar-thumb:hover {
        background: #a1a1a1;
    }
</style>
            """)
            
            # Referencia al archivo JS externo
            doc.stag('script', src=f'/static/js/{module_name}_service.js', defer=True)

        with tag('body', klass='bg-gray-50 min-h-screen'):
            # Barra de navegación mejorada
            doc.asis(f"""
<nav class="bg-gradient-to-r from-gray-800 to-gray-900 p-4 sticky top-0 z-30 shadow-md">
  <div class="container mx-auto flex justify-between items-center">
      <div class="flex items-center space-x-4">
          <a href="/" class="flex items-center space-x-2">
              <img src="/static/img/logo_mapache.gif" alt="Logo" class="h-8 w-auto">
              <span class="text-white font-bold text-lg hidden md:block">Sistema de Stock</span>
          </a>
          <div class="flex items-center space-x-2">
              <a href="/" class="text-white hover:text-blue-200 transition-colors">
                  <i class="fas fa-home"></i>
                  <span class="ml-1 hidden md:inline">Inicio</span>
              </a>
              <span class="text-gray-400">/</span>
              <span class="text-blue-200 font-medium">
                  <i class="fas fa-boxes"></i>
                  <span class="ml-1">{module_name.capitalize()}</span>
              </span>
          </div>
      </div>
      <div class="flex items-center space-x-4 relative">
          <a href="/docs" class="text-white hover:bg-gray-700 px-3 py-1 rounded-md text-sm transition-colors">
              <i class="fas fa-book mr-1"></i> API
          </a>
          <a href="/usuarios_admin/" class="text-white hover:bg-gray-700 px-3 py-1 rounded-md text-sm transition-colors">
              <i class="fas fa-users mr-1"></i> Usuarios
          </a>
          <a href="/servicios/" class="text-white hover:bg-gray-700 px-3 py-1 rounded-md text-sm transition-colors">
              <i class="fas fa-cogs mr-1"></i> Servicios
          </a>
      </div>
  </div>
</nav>

<!-- Notificaciones Toast -->
<div id="toast-container"></div>
""")

            # Header con título y descripción
            with tag('header', klass='bg-white shadow-sm mb-6'):
                with tag('div', klass='container mx-auto px-4 py-6'):
                    with tag('div', klass='flex flex-col md:flex-row justify-between items-start md:items-center'):
                        with tag('div'):
                            with tag('h1', klass='text-2xl font-bold text-gray-800 flex items-center'):
                                doc.asis('<i class="fas fa-cubes text-blue-600 mr-3"></i>')
                                text(f'Gestión de {module_name.capitalize()}')
                            line('p', 'Administra, añade y edita registros en el sistema', klass='text-gray-600 mt-1')
                        with tag('div', klass='mt-4 md:mt-0'):
                            with tag('button', id='help-btn', klass='bg-blue-50 text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-100 transition-colors flex items-center', onclick='toggleDescription()'):
                                doc.asis('<i class="fas fa-info-circle mr-2"></i>')
                                text('Ayuda')

            # Panel de ayuda/descripción
            with tag('div', id='description', klass='hidden container mx-auto px-4 mb-6'):
                with tag('div', klass='bg-blue-50 border-l-4 border-blue-500 p-5 rounded-lg shadow-sm slide-in'):
                    with tag('div', klass='flex justify-between items-start'):
                        line('h2', 'Cómo utilizar este módulo', klass='text-lg font-semibold text-blue-700 mb-3')
                        with tag('button', klass='text-gray-400 hover:text-gray-600', onclick='toggleDescription()'):
                            doc.asis('<i class="fas fa-times"></i>')
                    with tag('div', klass='space-y-3 text-gray-700'):
                        with tag('div', klass='flex items-start'):
                            doc.asis('<i class="fas fa-plus-circle text-green-600 mt-1 mr-3"></i>')
                            line('p', f'Usa el formulario para agregar nuevos registros de {module_name.capitalize()}.')
                        with tag('div', klass='flex items-start'):
                            doc.asis('<i class="fas fa-table text-blue-600 mt-1 mr-3"></i>')
                            line('p', 'La tabla muestra todos los registros y permite filtrarlos usando la barra de búsqueda.')
                        with tag('div', klass='flex items-start'):
                            doc.asis('<i class="fas fa-edit text-yellow-600 mt-1 mr-3"></i>')
                            line('p', f'Puedes editar todos los campos excepto el identificador ({field_names[0]}).')
                        with tag('div', klass='flex items-start'):
                            doc.asis('<i class="fas fa-trash-alt text-red-600 mt-1 mr-3"></i>')
                            line('p', 'Elimina registros cuando ya no sean necesarios.')

            # Contenido principal
            with tag('div', klass='container mx-auto px-4'):
                # Formulario principal con diseño en tarjeta
                with tag('div', klass='bg-white rounded-lg shadow-sm p-6 mb-6'):
                    with tag('h2', klass='text-lg font-semibold text-gray-800 mb-4 flex items-center'):
                        doc.asis('<i class="fas fa-plus-circle text-green-600 mr-2"></i>')
                        text('Añadir Nuevo Registro')
                    
                    with tag('form', id='data-form', klass='mb-4'):
                        with tag('div', klass='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'):
                            for fname, ftype in zip(field_names, field_types):
                                with tag('div'):
                                    with tag('label', klass='block text-sm font-medium text-gray-700 mb-1'):
                                        text(f'{fname.capitalize()}:')
                                        # Añadir asterisco para campos requeridos
                                        if fname == field_names[0] or ftype.lower() == 'int':
                                            doc.asis(' <span class="text-red-500">*</span>')
                                    
                                    if ftype.lower() == 'bool':
                                        with tag('div', klass='flex items-center mt-1'):
                                            doc.stag('input', id=fname, type='checkbox', 
                                                    klass='w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500')
                                            with tag('label', klass='ml-2 text-sm text-gray-700', **{'for': fname}):
                                                text('Activado')
                                    else:
                                        attrs = {'class': 'input-field w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 text-gray-700'}
                                        if ftype.lower() == 'int':
                                            attrs['required'] = 'required'
                                            attrs['min'] = '0'
                                            tp = 'number'
                                        elif ftype.lower() == 'float':
                                            attrs['step'] = 'any'
                                            tp = 'number'
                                        else:
                                            tp = 'text'
                                        
                                        doc.stag('input', id=fname, type=tp, placeholder=f'Ingrese {fname}', **attrs)
                        
                        # Botón de envío con estilo mejorado
                        with tag('div', klass='mt-6'):
                            with tag('button', type='submit', id='submit-btn', klass='bg-gradient-to-r from-green-500 to-green-600 text-white px-5 py-2 rounded-md shadow-sm hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 transition-all flex items-center'):
                                doc.asis('<i class="fas fa-save mr-2"></i>')
                                text('Guardar')
                
                # Barra de búsqueda
                with tag('div', klass='bg-white rounded-lg shadow-sm p-4 mb-6'):
                    with tag('div', klass='flex flex-wrap items-center'):
                        with tag('div', klass='relative flex-grow'):
                            doc.stag('input', id='search-input', type='text', placeholder='Buscar...', 
                                    klass='w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-gray-700')
                            with tag('div', klass='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'):
                                doc.asis('<i class="fas fa-search text-gray-400"></i>')
                        
                        with tag('div', klass='mt-2 sm:mt-0 sm:ml-4'):
                            with tag('button', id='reset-search', klass='bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 transition-colors flex items-center'):
                                doc.asis('<i class="fas fa-redo-alt mr-2"></i>')
                                text('Restablecer')
                
                # Tabla de datos mejorada
                with tag('div', klass='bg-white rounded-lg shadow-sm overflow-hidden'):
                    with tag('div', klass='p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center'):
                        with tag('h2', klass='text-lg font-semibold text-gray-800 flex items-center'):
                            doc.asis('<i class="fas fa-table text-blue-600 mr-2"></i>')
                            text('Registros')
                        with tag('div', id='record-count', klass='text-sm text-gray-500'):
                            text('Cargando registros...')
                    
                    # Contenedor con scroll para la tabla
                    with tag('div', klass='table-container'):
                        with tag('table', klass='min-w-full divide-y divide-gray-200'):
                            with tag('thead', klass='bg-gray-50'):
                                with tag('tr'):
                                    for fn in field_names:
                                        with tag('th', scope='col', klass='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'):
                                            text(fn.capitalize())
                                    with tag('th', scope='col', klass='px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider'):
                                        text('Acciones')
                            with tag('tbody', id='data-table-body', klass='bg-white divide-y divide-gray-200'):
                                # Los datos se llenarán con JavaScript
                                with tag('tr', id='loading-row'):
                                    with tag('td', colspan=str(len(field_names) + 1), klass='px-6 py-10 text-center text-sm text-gray-500'):
                                        doc.asis('<i class="fas fa-spinner fa-spin mr-2"></i>')
                                        text('Cargando datos...')

            # Modal de edición mejorado
            with tag('div', id='edit-modal', klass='fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 hidden'):
                with tag('div', klass='bg-white rounded-lg shadow-xl w-full max-w-md mx-4 fade-in'):
                    with tag('div', klass='px-6 py-4 border-b border-gray-200 flex justify-between items-center'):
                        with tag('h3', klass='text-lg font-semibold text-gray-800 flex items-center'):
                            doc.asis('<i class="fas fa-edit text-blue-600 mr-2"></i>')
                            text(f'Editar {module_name.capitalize()}')
                        with tag('button', type='button', klass='text-gray-400 hover:text-gray-500 focus:outline-none', onclick='closeEditModal()'):
                            doc.asis('<i class="fas fa-times"></i>')
                    
                    with tag('form', id='edit-form'):
                        with tag('div', klass='p-6 space-y-4'):
                            # Campo oculto para el ID
                            doc.stag('input', type='hidden', id=f'edit-{field_names[0]}')
                            
                            for fname, ftype in zip(field_names[1:], field_types[1:]):
                                if ftype.lower() == 'bool':
                                    with tag('div', klass='flex items-center'):
                                        doc.stag('input', id=f'edit-{fname}', type='checkbox',
                                                klass='w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500')
                                        with tag('label', klass='ml-2 text-sm text-gray-700', **{'for': f'edit-{fname}'}):
                                            text(fname.capitalize())
                                else:
                                    with tag('div'):
                                        with tag('label', klass='block text-sm font-medium text-gray-700 mb-1', **{'for': f'edit-{fname}'}):
                                            text(fname.capitalize())
                                        attrs = {'class': 'input-field w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-blue-500'}
                                        if ftype.lower() == 'float':
                                            attrs['step'] = 'any'
                                            tp = 'number'
                                        elif ftype.lower() == 'int':
                                            tp = 'number'
                                        else:
                                            tp = 'text'
                                        doc.stag('input', id=f'edit-{fname}', type=tp, **attrs)
                        
                        with tag('div', klass='px-6 py-4 border-t border-gray-200 flex justify-end space-x-3'):
                            with tag('button', type='button', klass='px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors', onclick='closeEditModal()'):
                                text('Cancelar')
                            with tag('button', type='submit', klass='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center'):
                                doc.asis('<i class="fas fa-save mr-2"></i>')
                                text('Guardar Cambios')
            
            # Modal de confirmación para eliminar
            with tag('div', id='delete-modal', klass='fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 hidden'):
                with tag('div', klass='bg-white rounded-lg shadow-xl w-full max-w-md mx-4 fade-in'):
                    with tag('div', klass='p-6'):
                        with tag('div', klass='flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto mb-4'):
                            doc.asis('<i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>')
                        with tag('h3', klass='text-lg font-medium text-gray-900 text-center mb-2'):
                            text('Confirmar eliminación')
                        with tag('p', klass='text-gray-500 text-center'):
                            text(f'¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.')
                        
                        with tag('div', klass='mt-6 flex justify-center space-x-4'):
                            with tag('button', type='button', id='cancel-delete', klass='px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors'):
                                text('Cancelar')
                            with tag('button', type='button', id='confirm-delete', klass='px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors flex items-center'):
                                doc.asis('<i class="fas fa-trash-alt mr-2"></i>')
                                text('Eliminar')
    
    html_str = doc.getvalue()
    soup = BeautifulSoup(html_str, 'html.parser')
    
    # Generar el contenido JavaScript en un archivo separado
    js_content = generate_js_content(module_name, field_names, field_types)
    
    return soup.prettify(), js_content

def generate_js_content(module_name, field_names, field_types):
    """
    Genera el contenido JavaScript para el servicio.
    
    Args:
        module_name: Nombre del módulo
        field_names: Lista de nombres de campos
        field_types: Lista de tipos de campos
        
    Returns:
        str: Contenido JavaScript
    """
    # Para addItem
    add_fields = []
    for f, t in zip(field_names, field_types):
        if t.lower() == 'int':
            add_fields.append(f"{f}: parseInt(document.getElementById('{f}').value) || 0")
        elif t.lower() == 'float':
            add_fields.append(f"{f}: parseFloat(document.getElementById('{f}').value) || 0")
        elif t.lower() == 'bool':
            add_fields.append(f"{f}: document.getElementById('{f}').checked")
        else:
            add_fields.append(f"{f}: document.getElementById('{f}').value")
    add_fields_str = ",\n        ".join(add_fields)

    # Para updateItem
    update_fields = []
    for f, t in zip(field_names[1:], field_types[1:]):
        if t.lower() == 'int':
            update_fields.append(f"{f}: parseInt(document.getElementById('edit-{f}').value) || 0")
        elif t.lower() == 'float':
            update_fields.append(f"{f}: parseFloat(document.getElementById('edit-{f}').value) || 0")
        elif t.lower() == 'bool':
            update_fields.append(f"{f}: document.getElementById('edit-{f}').checked")
        else:
            update_fields.append(f"{f}: document.getElementById('edit-{f}').value")
    update_fields_str = ",\n        ".join(update_fields)
    
    # Generar el código para las celdas de la tabla
    table_cells_code = ""
    for i, (field, field_type) in enumerate(zip(field_names, field_types)):
        cell_code = f"""
        // {field}
        const cell{i} = document.createElement('td');
        cell{i}.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        """
        
        if field_type.lower() == 'bool':
            cell_code += f"""if (typeof item.{field} === "boolean") {{
            cell{i}.innerHTML = item.{field} ? '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Sí</span>' : '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">No</span>';
        }}"""
        else:
            cell_code += f"cell{i}.textContent = item.{field};"
            
        cell_code += f"""
        row.appendChild(cell{i});
        """
        
        table_cells_code += cell_code
    
    js_content = f"""/**
 * JavaScript para la gestión de {module_name}
 * Generado automáticamente
 */

// Variables globales
let allData = [];
let currentItemId = null;

// Cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {{
    // Inicializar eventos
    document.getElementById('data-form').addEventListener('submit', addItem);
    document.getElementById('edit-form').addEventListener('submit', updateItem);
    document.getElementById('search-input').addEventListener('input', filterTable);
    document.getElementById('reset-search').addEventListener('click', resetSearch);
    document.getElementById('confirm-delete').addEventListener('click', confirmDelete);
    document.getElementById('cancel-delete').addEventListener('click', closeDeleteModal);
    
    // Cargar datos iniciales
    fetchData();
}});

/**
 * Obtiene los datos del servidor y actualiza la tabla
 */
async function fetchData() {{
    try {{
        const response = await fetch('/{module_name}/');
        
        if (!response.ok) {{
            throw new Error(`Error HTTP: ${{response.status}}`);
        }}
        
        const data = await response.json();
        
        // Verificar si la respuesta es un array
        if (!Array.isArray(data)) {{
            console.error("La respuesta no es un array:", data);
            showToast('Error al cargar los datos. La respuesta no tiene el formato esperado.', 'error');
            return;
        }}
        
        // Guardar datos para filtrado
        allData = data;
        
        // Actualizar la UI
        updateTable(data);
        updateRecordCount(data.length);
        
    }} catch (error) {{
        console.error("Error al cargar datos:", error);
        showToast(`Error al cargar los datos: ${{error.message}}`, 'error');
        
        const tableBody = document.getElementById('data-table-body');
        tableBody.innerHTML = `
            <tr>
                <td colspan="{len(field_names) + 1}" class="px-6 py-4 text-center text-red-500">
                    <i class="fas fa-exclamation-circle mr-2"></i>
                    Error al cargar datos. Intente recargar la página.
                </td>
            </tr>
        `;
    }}
}}

/**
 * Actualiza la tabla con los datos proporcionados
 */
function updateTable(data) {{
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = '';
    
    if (data.length === 0) {{
        tableBody.innerHTML = `
            <tr>
                <td colspan="{len(field_names) + 1}" class="px-6 py-4 text-center text-gray-500">
                    No se encontraron registros
                </td>
            </tr>
        `;
        return;
    }}
    
    data.forEach((item, index) => {{
        const row = document.createElement('tr');
        row.className = index % 2 === 0 ? 'bg-white' : 'bg-gray-50';
        row.classList.add('hover:bg-blue-50', 'transition-colors');
        
        // Crear celdas para cada campo
        {table_cells_code}
        
        // Celda de acciones
        const actionsCell = document.createElement('td');
        actionsCell.className = 'px-6 py-4 whitespace-nowrap text-right text-sm font-medium';
        actionsCell.innerHTML = `
            <button class="bg-blue-100 text-blue-700 hover:bg-blue-200 px-3 py-1 rounded-md mr-2 hover-raise" onclick="editItem(${{item.{field_names[0]}}})">
                <i class="fas fa-edit mr-1"></i> Editar
            </button>
            <button class="bg-red-100 text-red-700 hover:bg-red-200 px-3 py-1 rounded-md hover-raise" onclick="showDeleteModal(${{item.{field_names[0]}}})">
                <i class="fas fa-trash-alt mr-1"></i> Eliminar
            </button>
        `;
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    }});
}}

/**
 * Actualiza el contador de registros
 */
function updateRecordCount(count) {{
    const recordCount = document.getElementById('record-count');
    recordCount.textContent = count === 1 
        ? '1 registro encontrado' 
        : `${{count}} registros encontrados`;
}}

/**
 * Añade un nuevo registro
 */
async function addItem(event) {{
    event.preventDefault();
    
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Guardando...';
    
    const formData = {{
        {add_fields_str}
    }};
    
    try {{
        const response = await fetch('/{module_name}/', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(formData)
        }});
        
        if (!response.ok) {{
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al crear el registro");
        }}
        
        const result = await response.json();
        console.log("Registro creado:", result);
        
        // Limpiar formulario
        document.getElementById('data-form').reset();
        
        // Refrescar datos
        fetchData();
        
        // Mostrar notificación
        showToast('Registro creado correctamente', 'success');
        
    }} catch (error) {{
        console.error("Error:", error);
        showToast(`Error: ${{error.message}}`, 'error');
    }} finally {{
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-save mr-2"></i> Guardar';
    }}
}}

/**
 * Muestra el modal de edición con los datos del registro
 */
function editItem(id) {{
    fetch(`/{module_name}/id/${{id}}`)
        .then(response => {{
            if (!response.ok) {{
                throw new Error("Error al obtener los datos del registro");
            }}
            return response.json();
        }})
        .then(data => {{
            // Guardar el ID actual
            currentItemId = id;
            
            // Rellenar el formulario
            document.getElementById('edit-{field_names[0]}').value = data.{field_names[0]};
            
            {';'.join([
                f"document.getElementById('edit-{f}').{('checked = data.' + f) if t.lower() == 'bool' else ('value = data.' + f)}"
                for f, t in zip(field_names[1:], field_types[1:])
            ])};
            
            // Mostrar el modal
            document.getElementById('edit-modal').classList.remove('hidden');
        }})
        .catch(error => {{
            console.error("Error al obtener datos para editar:", error);
            showToast(`Error: ${{error.message}}`, 'error');
        }});
}}

/**
 * Cierra el modal de edición
 */
function closeEditModal() {{
    document.getElementById('edit-modal').classList.add('hidden');
    currentItemId = null;
}}

/**
 * Actualiza un registro
 */
async function updateItem(event) {{
    event.preventDefault();
    
    if (!currentItemId) {{
        showToast('Error: No se pudo identificar el registro a actualizar', 'error');
        return;
    }}
    
    const id = currentItemId;
    const updatedData = {{
        {update_fields_str}
    }};
    
    try {{
        const response = await fetch(`/{module_name}/id/${{id}}`, {{
            method: 'PUT',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(updatedData)
        }});
        
        if (!response.ok) {{
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al actualizar el registro");
        }}
        
        // Cerrar modal y refrescar datos
        closeEditModal();
        fetchData();
        
        // Mostrar notificación
        showToast('Registro actualizado correctamente', 'success');
        
    }} catch (error) {{
        console.error("Error:", error);
        showToast(`Error: ${{error.message}}`, 'error');
    }}
}}

/**
 * Muestra el modal de confirmación para eliminar
 */
function showDeleteModal(id) {{
    currentItemId = id;
    document.getElementById('delete-modal').classList.remove('hidden');
}}

/**
 * Cierra el modal de confirmación para eliminar
 */
function closeDeleteModal() {{
    document.getElementById('delete-modal').classList.add('hidden');
    currentItemId = null;
}}

/**
 * Elimina un registro después de confirmar
 */
async function confirmDelete() {{
    if (!currentItemId) {{
        showToast('Error: No se pudo identificar el registro a eliminar', 'error');
        closeDeleteModal();
        return;
    }}
    
    const id = currentItemId;
    
    try {{
        const response = await fetch(`/{module_name}/id/${{id}}`, {{ method: 'DELETE' }});
        
        if (!response.ok) {{
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al eliminar el registro");
        }}
        
        // Cerrar modal y refrescar datos
        closeDeleteModal();
        fetchData();
        
        // Mostrar notificación
        showToast('Registro eliminado correctamente', 'success');
        
    }} catch (error) {{
        console.error("Error:", error);
        showToast(`Error: ${{error.message}}`, 'error');
        closeDeleteModal();
    }}
}}

/**
 * Filtra la tabla según el texto de búsqueda
 */
function filterTable() {{
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    
    if (!searchTerm) {{
        updateTable(allData);
        updateRecordCount(allData.length);
        return;
    }}
    
    const filteredData = allData.filter(item => {{
        return {" || ".join([f"String(item.{field}).toLowerCase().includes(searchTerm)" for field in field_names])};
    }});
    
    updateTable(filteredData);
    updateRecordCount(filteredData.length);
}}

/**
 * Restablece la búsqueda
 */
function resetSearch() {{
    document.getElementById('search-input').value = '';
    updateTable(allData);
    updateRecordCount(allData.length);
}}

/**
 * Muestra/oculta la descripción
 */
function toggleDescription() {{
    const description = document.getElementById('description');
    description.classList.toggle('hidden');
}}

/**
 * Muestra una notificación toast
 */
function showToast(message, type = 'success') {{
    // Crear el elemento toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${{type}} slide-in`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="${{type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'}} mr-2"></i>
            <span>${{message}}</span>
        </div>
    `;
    
    // Añadir al contenedor
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    // Eliminar después de 5 segundos
    setTimeout(() => {{
        toast.style.opacity = '0';
        setTimeout(() => {{
            container.removeChild(toast);
        }}, 300);
    }}, 5000);
}}
"""
    
    return js_content