def generate_html_form(module_name, field_names, field_types):
    from yattag import Doc
    from bs4 import BeautifulSoup

    doc, tag, text, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')

    with tag('html', lang='es'):
        with tag('head'):
            doc.stag('meta', charset='UTF-8')
            line('title', f'Gestión de {module_name.capitalize()}')
            doc.stag('script', src='https://cdn.tailwindcss.com')
            doc.stag('link', rel='stylesheet',
                     href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css')
            with tag('script'):
                doc.asis(f"""
window.onload = function() {{
    document.documentElement.classList.add('dark');
    fetchData();
}};

async function fetchData() {{
    const response = await fetch('/{module_name}/');
    const data = await response.json();
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = '';
    data.forEach(item => {{
        const row = document.createElement('tr');
        row.innerHTML = `
            {''.join([
                f'<td class="border px-4 py-2">${{item.{f}}}</td>'
                for f in field_names
            ])}
            <td class="border px-4 py-2">
                <button class="bg-blue-500 text-white px-2 py-1" onclick="editItem(${{item.{field_names[0]}}})">Editar</button>
                <button class="bg-red-500 text-white px-2 py-1" onclick="deleteItem(${{item.{field_names[0]}}})">Eliminar</button>
            </td>
        `;
        tableBody.appendChild(row);
    }});
}}


async function addItem(event) {{
    event.preventDefault();
    const formData = {{
        {', '.join([
            f"{f}: {'parseInt' if t.lower()=='int' else 'parseFloat' if t.lower()=='float' else ''}document.getElementById('{f}').value"
            if t.lower() != 'bool' else f"{f}: document.getElementById('{f}').checked"
            for f, t in zip(field_names, field_types)
        ])}
    }};
    try {{
      const respuesta = await fetch('/{module_name}/', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
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
            {chr(10).join([
                f"document.getElementById('edit-{f}').value = data.{f};" if t.lower()!='bool'
                else f"document.getElementById('edit-{f}').checked = data.{f};"
                for f, t in zip(field_names, field_types)
            ])}
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
        {', '.join([
            f"{f}: {'parseFloat' if t.lower()=='float' else ''}document.getElementById('edit-{f}').value"
            if t.lower() not in ['bool','int']
            else f"{f}: parseInt(document.getElementById('edit-{f}').value)"
            if t.lower()=='int'
            else f"{f}: document.getElementById('edit-{f}').checked"
            for f,t in zip(field_names[1:], field_types[1:])
        ])}
    }};
    await fetch(`/{module_name}/id/${{id}}`, {{
        method: 'PUT',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(updatedData)
    }});
    closeEditModal();
    fetchData();
}}

async function deleteItem(id) {{
    await fetch(`/{module_name}/id/${{id}}`, {{ method: 'DELETE' }});
    fetchData();
}}
""")
        with tag('body', klass='p-4 bg-gray-900 text-white'):
            with tag('div', klass='flex justify-between items-center mb-4'):
                line('h1', f'Gestión de {module_name.capitalize()}', klass='text-2xl')
            with tag('form', id='data-form', klass='mb-4', onsubmit='addItem(event)'):
                with tag('div', klass='flex flex-wrap -mx-2'):
                    for fname, ftype in zip(field_names, field_types):
                        with tag('div', klass='w-full md:w-1/4 px-2 mb-4'):
                            if ftype.lower() == 'bool':
                                with tag('div', klass='flex items-center'):
                                    line('label', f'{fname}:', klass='mr-2')
                                    doc.stag('input', id=fname, type='checkbox', klass='w-4 h-4')
                            else:
                                line('label', f'{fname}:', klass='block')
                                tp = 'number' if ftype.lower() in ['int','float'] else 'text'
                                attrs = {}
                                if ftype.lower() in ['int','float']:
                                    attrs['step'] = 'any' if ftype.lower()=='float' else None
                                    attrs['required'] = 'required'
                                doc.stag('input', id=fname, type=tp,
                                         klass='w-full border px-2 py-1 bg-gray-800 text-white',
                                         **{k:v for k,v in attrs.items() if v is not None})
            with tag('button', type='submit', klass='bg-green-500 text-white px-4 py-2'):
                text('Agregar')
            with tag('table', klass='table-auto w-full border-collapse'):
                with tag('thead'):
                    with tag('tr'):
                        for fn in field_names:
                            line('th', fn, klass='border px-4 py-2')
                        line('th', 'Acciones', klass='border px-4 py-2')
                with tag('tbody', id='data-table-body'):
                    text('<!-- Los datos se cargarán aquí -->')
            with tag('div', id='edit-modal', klass='fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 hidden'):
                with tag('div', klass='bg-gray-800 p-4 rounded w-96'):
                    line('h2', f'Editar {module_name.capitalize()}', klass='text-xl mb-4')
                    with tag('form', id='edit-form', onsubmit='updateItem(event)'):
                        doc.stag('input', type='hidden', id=f'edit-{field_names[0]}')
                        for fname, ftype in zip(field_names[1:], field_types[1:]):
                            with tag('div', klass='mb-2'):
                                if ftype.lower() == 'bool':
                                    with tag('div', klass='flex items-center'):
                                        line('label', f'{fname}:', klass='mr-2')
                                        doc.stag('input', id=f'edit-{fname}', type='checkbox', klass='w-4 h-4')
                                else:
                                    line('label', f'{fname}:')
                                    tp = 'number' if ftype.lower() in ['int','float'] else 'text'
                                    attrs = {}
                                    if ftype.lower() == 'float':
                                        attrs['step'] = 'any'
                                    doc.stag('input', id=f'edit-{fname}', type=tp,
                                             klass='border px-2 py-1 w-full bg-gray-800 text-white',
                                             **attrs)
                        with tag('div', klass='flex justify-end'):
                            with tag('button', type='button', klass='mr-2 px-4 py-2', onclick='closeEditModal()'):
                                text('Cancelar')
                            with tag('button', type='submit', klass='bg-blue-500 text-white px-4 py-2'):
                                text('Guardar')

    html_content = doc.getvalue()
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.prettify()