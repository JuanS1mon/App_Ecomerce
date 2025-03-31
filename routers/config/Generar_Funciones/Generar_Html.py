def generate_html_form(module_name, field_names, field_types):
    from yattag import Doc
    from bs4 import BeautifulSoup

    doc, tag, text, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')

    # Construimos el HTML
    with tag('html', lang='es'):
        with tag('head'):
            doc.stag('meta', charset='UTF-8')
            line('title', f'Gestión de {module_name.capitalize()}')
            doc.stag('script', src='https://cdn.tailwindcss.com')
            doc.stag('link', rel='stylesheet',
                     href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css')

            # Separamos el bloque conflictivo
            # Construimos la parte de row.innerHTML sin usar f-string anidado:
            row_cells = "".join([f"<td class='border px-4 py-2'>${{item.{f}}}</td>" for f in field_names])

            # Para addItem
            add_fields = []
            for f, t in zip(field_names, field_types):
                if t.lower() == 'int':
                    add_fields.append(f"{f}: parseInt(document.getElementById('{f}').value)")
                elif t.lower() == 'float':
                    add_fields.append(f"{f}: parseFloat(document.getElementById('{f}').value)")
                elif t.lower() == 'bool':
                    add_fields.append(f"{f}: document.getElementById('{f}').checked")
                else:
                    add_fields.append(f"{f}: document.getElementById('{f}').value")
            add_fields_str = ", ".join(add_fields)

            # Para updateItem
            update_fields = []
            for f, t in zip(field_names[1:], field_types[1:]):
                if t.lower() == 'int':
                    update_fields.append(f"{f}: parseInt(document.getElementById('edit-{f}').value)")
                elif t.lower() == 'float':
                    update_fields.append(f"{f}: parseFloat(document.getElementById('edit-{f}').value)")
                elif t.lower() == 'bool':
                    update_fields.append(f"{f}: document.getElementById('edit-{f}').checked")
                else:
                    update_fields.append(f"{f}: document.getElementById('edit-{f}').value")
            update_fields_str = ", ".join(update_fields)

            # Insertamos el bloque completo usando doc.asis
            script_content = f"""
window.onload = function() {{
    fetchData();
}};

async function fetchData() {{
    const response = await fetch('/{module_name}/');
    const data = await response.json();
    if (!Array.isArray(data)) {{
        console.error("La respuesta no es un array:", data);
        return;
    }}
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = '';
    data.forEach(item => {{
        const row = document.createElement('tr');
        row.innerHTML = `
            {row_cells}
            <td class='border px-4 py-2'>
                <button class='bg-blue-500 text-white px-2 py-1' onclick='editItem(${{item.{field_names[0]}}})'>Editar</button>
                <button class='bg-red-500 text-white px-2 py-1' onclick='deleteItem(${{item.{field_names[0]}}})'>Eliminar</button>
            </td>
        `;
        tableBody.appendChild(row);
    }});
}}

async function addItem(event) {{
    event.preventDefault();
    const formData = {{
        {add_fields_str}
    }};
    try {{
        const respuesta = await fetch('/{module_name}/', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(formData)
        }});
        if (!respuesta.ok) {{
            throw new Error("Error al crear {module_name}");
        }}
        console.log("Registro creado:", await respuesta.json());
        document.getElementById('data-form').reset();
        fetchData();
    }} catch (error) {{
        console.error(error);
    }}
}}

function editItem(id) {{
    fetch(`/{module_name}/id/${{id}}`)
      .then(response => response.json())
      .then(data => {{
          document.getElementById('edit-{field_names[0]}').value = data.{field_names[0]};
          {";".join(
              f"document.getElementById('edit-{f}').value = data.{f}"
              if t.lower() not in ['bool']
              else f"document.getElementById('edit-{f}').checked = data.{f}"
              for f, t in zip(field_names[1:], field_types[1:])
          )};
          document.getElementById('edit-modal').classList.remove('hidden');
      }});
}}

function closeEditModal() {{
    document.getElementById('edit-modal').classList.add('hidden');
}}

async function updateItem(event) {{
    event.preventDefault();
    const id = document.getElementById('edit-{field_names[0]}').value;
    const updatedData = {{
        {update_fields_str}
    }};
    await fetch(`/{module_name}/id/${{id}}`, {{
        method: 'PUT',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(updatedData)
    }});
    closeEditModal();
    fetchData();
}}

async function deleteItem(id) {{
    await fetch(`/{module_name}/id/${{id}}`, {{ method: 'DELETE' }});
    fetchData();
}};

// Función para mostrar/ocultar la sección de descripción
function toggleDescription() {{
    const description = document.getElementById('description');
    description.classList.toggle('hidden');
}}
"""
            doc.asis("<script>" + script_content + "</script>")

        with tag('body', klass='bg-gray-100 min-h-screen'):
            # Barra de navegación
            doc.asis(f"""
<nav class="bg-gray-800 p-4 relative z-30">
  <div class="container mx-auto flex justify-between items-center">
      <div class="flex items-center space-x-4">
          <a href="">
              <img src="../static/img/logo_mapache.gif" alt="Logo" class="h-8 w-auto">
          </a>
          <a href="/index" class="text-white text-lg font-semibold hover:text-gray-300">Inicio</a>
          <span class="text-gray-400">/</span>
          <span class="text-white text-lg font-semibold">{module_name}</span>
      </div>
      <div class="flex items-center space-x-4 relative">
          <a href="/docs" class="text-white hover:text-gray-300">Documentación</a>
          <a href="/generar" class="text-white hover:text-gray-300">Generar API</a>
          <a href="/migraciones/admin_migraciones" class="text-white hover:text-gray-300">Migraciones</a>
      </div>
  </div>
</nav>
""")
 # Agregamos la descripción de la app
            with tag('div', klass='flex justify-center p-4'):
                    doc.asis("""
            <!-- Descripción de la app -->
            <div class="bg-blue-50 p-6 rounded-lg shadow-md max-w-lg text-center">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-bold text-blue-600">Gestión de Datos</h2>
                    <button id="toggleButton" class="text-blue-600 hover:underline text-xl ml-2" onclick="toggleDescription()">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </div>
                <div id="description" class="hidden">
                    <p class="text-gray-700">
                        Este formulario HTML permite la carga de datos en una tabla. Puedes agregar nuevos registros utilizando el formulario de entrada.
                    </p>
                    <p class="text-gray-700 mt-2">
                        La tabla muestra los datos ingresados y permite editar todos los campos excepto el primer campo, que actúa como identificador único.
                    </p>
                    <p class="text-gray-700 mt-2">
                        Además, puedes eliminar cualquier registro de la tabla utilizando el botón de eliminar correspondiente.
                    </p>
                    <p class="text-gray-700 mt-2">
                        Utiliza esta herramienta para gestionar tus datos de manera eficiente, permitiendo agregar, editar y eliminar registros según sea necesario.
                    </p>
                </div>
            </div>
                    """)
            with tag('div', klass='p-4'):
                with tag('div', klass='flex justify-center mb-4'):
                    line('h1', f'Gestión de {module_name.capitalize()}', klass='text-2xl text-center')
               
                with tag('form', id='data-form', klass='mb-4', onsubmit='addItem(event)'):
                    with tag('div', klass='flex flex-wrap -mx-2'):
                        for fname, ftype in zip(field_names, field_types):
                            with tag('div', klass='w-full md:w-1/4 px-2 mb-4'):
                                if ftype.lower() == 'bool':
                                    with tag('div', klass='flex items-center'):
                                        line('label', f'{fname}:', klass='mr-2')
                                        doc.stag('input', id=fname, type='checkbox', klass='w-4 h-4 align-middle')
                                else:
                                    line('label', f'{fname}:', klass='block')
                                    tp = 'number' if ftype.lower() in ['int','float'] else 'text'
                                    attrs = {}
                                    if ftype.lower() == 'int':
                                        attrs['required'] = 'required'
                                    if ftype.lower() == 'float':
                                        attrs['step'] = 'any'
                                    doc.stag('input', id=fname, type=tp,
                                             klass='w-full border px-2 py-1 bg-white-800',
                                             **attrs)
                    with tag('button', type='submit', klass='bg-green-500 text-white px-4 py-2'):
                        text('Agregar')

                with tag('table', klass='table-auto w-full border-collapse'):
                    with tag('thead'):
                        with tag('tr'):
                            for fn in field_names:
                                line('th', fn, klass='border px-4 py-2')
                            line('th', 'Acciones', klass='border px-4 py-2')
                    with tag('tbody', id='data-table-body'):
             
                        with tag('div', id='edit-modal', klass='fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 hidden'):
                            with tag('div', klass='bg-gray-800 p-4 rounded w-96'):
                                line('h2', f'Editar {module_name.capitalize()}', klass='text-xl mb-4 text-white')
                                with tag('form', id='edit-form', onsubmit='updateItem(event)'):
                                    doc.stag('input', type='hidden', id=f'edit-{field_names[0]}')
                                    for fname, ftype in zip(field_names[1:], field_types[1:]):
                                        with tag('div', klass='mb-2'):
                                            if ftype.lower() == 'bool':
                                                with tag('div', klass='flex items-center'):
                                                    line('label', f'{fname}:', klass='mr-2 text-white')
                                                    doc.stag('input', id=f'edit-{fname}', type='checkbox', klass='w-4 h-4')
                                            else:
                                                line('label', f'{fname}:', klass='text-white')
                                                tp = 'number' if ftype.lower() in ['int','float'] else 'text'
                                                attrs = {}
                                                if ftype.lower() == 'float':
                                                    attrs['step'] = 'any'
                                                doc.stag(
                                                    'input',
                                                    id=f'edit-{fname}',
                                                    type=tp,
                                                    klass='border px-2 py-1 w-full bg-gray-800 text-white',
                                                    **attrs )

                                    with tag('div', klass='flex justify-end'):
                                        with tag('button', type='button', klass='mr-2 px-4 py-2 bg-red-500 text-white', onclick='closeEditModal()'):
                                            text('Cancelar')
                                        with tag('button', type='submit', klass='bg-blue-500 text-white px-4 py-2'):
                                            text('Guardar')

    html_str = doc.getvalue()
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.prettify()