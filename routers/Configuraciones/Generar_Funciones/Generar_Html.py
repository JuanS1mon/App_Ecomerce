def generate_html_form(module_name, field_names, field_types):
    from yattag import Doc
    from bs4 import BeautifulSoup

    doc, tag, text, line = Doc().ttl()

    with tag('html', lang='es'):
        with tag('head'):
            doc.stag('meta', charset='UTF-8')
            line('title', f'Gestión de {module_name.capitalize()}')
            doc.stag('script', src='https://cdn.tailwindcss.com')
            doc.stag('link', rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css')
            with tag('script', type='text/javascript'):
                doc.asis("""
                // Aplicar el modo oscuro al cargar la página
                window.onload = function() {
                    document.documentElement.classList.add('dark');
                    fetchData();
                }

                async function fetchData() {
                    const response = await fetch('/{module_name}/');
                    const data = await response.json();
                    const tableBody = document.getElementById('data-table-body');
                    tableBody.innerHTML = '';
                    data.forEach(item => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td class="border px-4 py-2">${item.campot1}</td>
                            <td class="border px-4 py-2">${item.campot2}</td>
                            <td class="border px-4 py-2">${item.campot3}</td>
                            <td class="border px-4 py-2">${item.campot4}</td>
                            <td class="border px-4 py-2">
                                <button class="bg-blue-500 text-white px-2 py-1" onclick="editItem(${item.campot1})">Editar</button>
                                <button class="bg-red-500 text-white px-2 py-1" onclick="deleteItem(${item.campot1})">Eliminar</button>
                            </td>
                        `;
                        tableBody.appendChild(row);
                    });
                }

                async function addItem(event) {
                    event.preventDefault();
                    const formData = {
                        campot1: parseInt(document.getElementById('campot1').value),
                        campot2: document.getElementById('campot2').value,
                        campot3: parseFloat(document.getElementById('campot3').value),
                        campot4: document.getElementById('campot4').checked
                    };
                    await fetch('/{module_name}/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(formData)
                    });
                    fetchData();
                    document.getElementById('data-form').reset();
                }

                function editItem(id) {
                    fetch(`/{module_name}/id/${id}`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('edit-campot1').value = data.campot1;
                            document.getElementById('edit-campot2').value = data.campot2;
                            document.getElementById('edit-campot3').value = data.campot3;
                            document.getElementById('edit-campot4').checked = data.campot4;
                            document.getElementById('edit-modal').classList.remove('hidden');
                        });
                }

                function closeEditModal() {
                    document.getElementById('edit-modal').classList.add('hidden');
                }

                async function updateItem(event) {
                    event.preventDefault();
                    const id = document.getElementById('edit-campot1').value;
                    const updatedData = {
                        campot2: document.getElementById('edit-campot2').value,
                        campot3: parseFloat(document.getElementById('edit-campot3').value),
                        campot4: document.getElementById('edit-campot4').checked
                    };
                    await fetch(`/{module_name}/id/${id}`, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(updatedData)
                    });
                    closeEditModal();
                    fetchData();
                }

                async function deleteItem(id) {
                    await fetch(`/{module_name}/id/${id}`, { method: 'DELETE' });
                    fetchData();
                }
                """)

        with tag('body', klass='p-4 bg-gray-900 text-white'):
            with tag('div', klass='flex justify-between items-center mb-4'):
                line('h1', f'Gestión de {module_name.capitalize()}', klass='text-2xl')
            with tag('form', id='data-form', klass='mb-4', onsubmit='addItem(event)'):
                with tag('div', klass='flex flex-wrap -mx-2'):
                    for field_name, field_type in zip(field_names, field_types):
                        with tag('div', klass='w-full md:w-1/4 px-2 mb-4'):
                            line('label', f'{field_name}:', klass='block')
                            input_type = 'text' if field_type == 'str' else 'number' if field_type in ['int', 'float'] else 'checkbox'
                            doc.stag('input', id=field_name, type=input_type, klass='w-full border px-2 py-1 bg-gray-800 text-white', required=True if field_type != 'bool' else False)
                doc.stag('button', type='submit', klass='bg-green-500 text-white px-4 py-2', value='Agregar')

            with tag('table', klass='table-auto w-full border-collapse'):
                with tag('thead'):
                    with tag('tr'):
                        for field_name in field_names:
                            line('th', field_name, klass='border px-4 py-2')
                        line('th', 'Acciones', klass='border px-4 py-2')
                with tag('tbody', id='data-table-body'):
                    text('<!-- Los datos se cargarán aquí -->')

            with tag('div', id='edit-modal', klass='fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 hidden'):
                with tag('div', klass='bg-gray-800 p-4 rounded w-96'):
                    line('h2', f'Editar {module_name.capitalize()}', klass='text-xl mb-4')
                    with tag('form', id='edit-form', onsubmit='updateItem(event)'):
                        doc.stag('input', type='hidden', id='edit-campot1')
                        for field_name, field_type in zip(field_names[1:], field_types[1:]):
                            with tag('div', klass='mb-2'):
                                line('label', f'{field_name}:')
                                input_type = 'text' if field_type == 'str' else 'number' if field_type in ['int', 'float'] else 'checkbox'
                                doc.stag('input', id=f'edit-{field_name}', type=input_type, klass='border px-2 py-1 w-full bg-gray-800 text-white')
                        with tag('div', klass='flex justify-end'):
                            doc.stag('button', type='button', klass='mr-2 px-4 py-2', onclick='closeEditModal()', value='Cancelar')
                            doc.stag('button', type='submit', klass='bg-blue-500 text-white px-4 py-2', value='Guardar')

    html_content = doc.getvalue()

    # Formatear el contenido HTML usando BeautifulSoup para mayor legibilidad
    soup = BeautifulSoup(html_content, 'html.parser')
    html_content = soup.prettify()

    return html_content