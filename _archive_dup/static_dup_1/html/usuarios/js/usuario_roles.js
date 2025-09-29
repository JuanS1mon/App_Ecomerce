document.addEventListener('DOMContentLoaded', function() {
    // Cargar componentes (navbar, footer, etc.)
    if (window.loadComponents) {
        loadComponents();
    } else {
        console.error("La función loadComponents no está disponible");
    }

    // Variables globales
    let roles = [];
    let currentPage = 1;
    const itemsPerPage = 10;
    let totalPages = 0;
    let totalRoles = 0;
    let currentRolId = null;
    let permisos = [];

    // Elementos DOM
    const rolesTableBody = document.getElementById('rolesTableBody');
    const btnNuevoRol = document.getElementById('btnNuevoRol');
    const modalRol = document.getElementById('modalRol');
    const modalBackdrop = document.getElementById('modalBackdrop');
    const btnCerrarModal = document.getElementById('btnCerrarModal');
    const formRol = document.getElementById('formRol');
    const btnCancelar = document.getElementById('btnCancelar');
    const searchRoles = document.getElementById('searchRoles');
    const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');
    const modalUsuariosRol = document.getElementById('modalUsuariosRol');
    const listaUsuariosRol = document.getElementById('listaUsuariosRol');
    const btnCerrarModalUsuarios = document.getElementById('btnCerrarModalUsuarios');
    const btnCerrarListaUsuarios = document.getElementById('btnCerrarListaUsuarios');
    const modalConfirmarEliminar = document.getElementById('modalConfirmarEliminar');
    const nombreRolEliminar = document.getElementById('nombreRolEliminar');
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    const notificacionExito = document.getElementById('notificacionExito');
    const mensajeExito = document.getElementById('mensajeExito');
    const notificacionError = document.getElementById('notificacionError');
    const mensajeError = document.getElementById('mensajeError');
    const startRange = document.getElementById('startRange');
    const endRange = document.getElementById('endRange');
    const totalRolesElement = document.getElementById('totalRoles');
    const btnAnterior = document.getElementById('btnAnterior');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const btnAnteriorMobile = document.getElementById('btnAnteriorMobile');
    const btnSiguienteMobile = document.getElementById('btnSiguienteMobile');
    const paginationNumbers = document.getElementById('paginationNumbers');

    // Inicializar la página
    init();

    // Función de inicialización
    function init() {
        // Cargar roles
        cargarRoles();
        
        // Cargar permisos disponibles
        cargarPermisos();

        // Configurar event listeners
        configurarEventListeners();
    }

    // Cargar roles desde la API
    function cargarRoles(searchQuery = '') {
        // Mostrar indicador de carga
        rolesTableBody.innerHTML = `
            <tr class="animate-pulse">
                <td colspan="6" class="px-6 py-4 whitespace-nowrap">
                    <div class="text-center text-gray-400">Cargando roles...</div>
                </td>
            </tr>
        `;

        // Construir URL de la API con parámetros de búsqueda y paginación
        let url = `/api/roles?page=${currentPage}&limit=${itemsPerPage}`;
        if (searchQuery) {
            url += `&search=${encodeURIComponent(searchQuery)}`;
        }

        // Realizar la petición a la API
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al cargar roles');
                }
                return response.json();
            })
            .then(data => {
                roles = data.items || [];
                totalRoles = data.total || 0;
                totalPages = Math.ceil(totalRoles / itemsPerPage);
                
                actualizarTablaRoles();
                actualizarPaginacion();
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion('error', 'Error al cargar los roles: ' + error.message);
                rolesTableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-4 whitespace-nowrap">
                            <div class="text-center text-red-500">Error al cargar roles. Intente nuevamente.</div>
                        </td>
                    </tr>
                `;
            });
    }

    // Cargar permisos disponibles
    function cargarPermisos() {
        fetch('/api/permisos')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al cargar permisos');
                }
                return response.json();
            })
            .then(data => {
                permisos = data || [];
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion('error', 'Error al cargar los permisos: ' + error.message);
            });
    }

    // Actualizar la tabla de roles con los datos actuales
    function actualizarTablaRoles() {
        if (roles.length === 0) {
            rolesTableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-4 whitespace-nowrap">
                        <div class="text-center text-gray-500">No se encontraron roles</div>
                    </td>
                </tr>
            `;
            return;
        }

        rolesTableBody.innerHTML = '';
        
        roles.forEach(rol => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50';
            
            // Formatear la fecha de creación si existe
            const fechaCreacion = rol.fecha_creacion ? new Date(rol.fecha_creacion).toLocaleString() : 'N/A';
            
            // Contar permisos si existen
            const permisosCount = rol.permisos ? rol.permisos.length : 0;
            
            // Contar usuarios asignados si existen
            const usuariosCount = rol.usuarios_count || 0;
            
            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <i class="fas fa-user-tag text-blue-500"></i>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${rol.nombre}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-900">${rol.descripcion || 'Sin descripción'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        ${permisosCount} permisos
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <button class="text-blue-600 hover:text-blue-900 text-sm font-medium ver-usuarios" data-id="${rol.id}" data-nombre="${rol.nombre}">
                        ${usuariosCount} usuarios <i class="fas fa-eye ml-1"></i>
                    </button>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${fechaCreacion}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button class="text-indigo-600 hover:text-indigo-900 mr-3 editar-rol" data-id="${rol.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="text-red-600 hover:text-red-900 eliminar-rol" data-id="${rol.id}" data-nombre="${rol.nombre}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            
            rolesTableBody.appendChild(tr);
        });

        // Añadir event listeners a los botones de la tabla
        document.querySelectorAll('.ver-usuarios').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const rolId = e.currentTarget.dataset.id;
                const rolNombre = e.currentTarget.dataset.nombre;
                verUsuariosRol(rolId, rolNombre);
            });
        });

        document.querySelectorAll('.editar-rol').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const rolId = e.currentTarget.dataset.id;
                editarRol(rolId);
            });
        });

        document.querySelectorAll('.eliminar-rol').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const rolId = e.currentTarget.dataset.id;
                const rolNombre = e.currentTarget.dataset.nombre;
                confirmarEliminarRol(rolId, rolNombre);
            });
        });
    }

    // Actualizar la paginación
    function actualizarPaginacion() {
        // Actualizar el rango mostrado
        const start = (currentPage - 1) * itemsPerPage + 1;
        const end = Math.min(currentPage * itemsPerPage, totalRoles);
        
        startRange.textContent = totalRoles > 0 ? start : 0;
        endRange.textContent = end;
        totalRolesElement.textContent = totalRoles;

        // Desactivar/activar botones de navegación
        btnAnterior.disabled = currentPage <= 1;
        btnSiguiente.disabled = currentPage >= totalPages;
        btnAnteriorMobile.disabled = currentPage <= 1;
        btnSiguienteMobile.disabled = currentPage >= totalPages;

        btnAnterior.classList.toggle('opacity-50', currentPage <= 1);
        btnSiguiente.classList.toggle('opacity-50', currentPage >= totalPages);
        btnAnteriorMobile.classList.toggle('opacity-50', currentPage <= 1);
        btnSiguienteMobile.classList.toggle('opacity-50', currentPage >= totalPages);

        // Actualizar números de página
        paginationNumbers.innerHTML = '';
        
        // Determinar qué números de página mostrar
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        
        if (endPage - startPage < 4 && totalPages > 4) {
            startPage = Math.max(1, endPage - 4);
        }

        // Añadir botones de página
        for (let i = startPage; i <= endPage; i++) {
            const pageButton = document.createElement('button');
            pageButton.className = `relative inline-flex items-center px-4 py-2 border text-sm font-medium
                ${i === currentPage 
                    ? 'bg-blue-50 border-blue-500 text-blue-600 z-10'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'}`;
            pageButton.textContent = i;
            pageButton.addEventListener('click', () => {
                currentPage = i;
                cargarRoles(searchRoles.value);
            });
            paginationNumbers.appendChild(pageButton);
        }
    }

    // Función para mostrar el formulario de nuevo rol
    function mostrarFormularioNuevoRol() {
        currentRolId = null;
        document.getElementById('modalTitle').textContent = 'Nuevo Rol';
        document.getElementById('rolId').value = '';
        document.getElementById('nombre').value = '';
        document.getElementById('descripcion').value = '';
        
        mostrarPermisos([]);
        
        // Mostrar el modal
        modalRol.classList.remove('hidden');
    }

    // Función para mostrar permisos en el formulario
    function mostrarPermisos(permisosSeleccionados = []) {
        const permisosContainer = document.getElementById('permisosContainer');
        
        if (!permisos || permisos.length === 0) {
            permisosContainer.innerHTML = '<div class="text-gray-500 text-center">No hay permisos disponibles</div>';
            return;
        }

        permisosContainer.innerHTML = '';
        
        // Ordenar permisos por categoría
        const permisosPorCategoria = {};
        
        permisos.forEach(permiso => {
            const categoria = permiso.categoria || 'General';
            
            if (!permisosPorCategoria[categoria]) {
                permisosPorCategoria[categoria] = [];
            }
            
            permisosPorCategoria[categoria].push(permiso);
        });

        // Crear elementos para cada categoría
        Object.keys(permisosPorCategoria).sort().forEach(categoria => {
            const categoriaDiv = document.createElement('div');
            categoriaDiv.className = 'mb-3';
            
            const categoriaHeader = document.createElement('h4');
            categoriaHeader.className = 'text-sm font-medium text-gray-700 mb-2';
            categoriaHeader.textContent = categoria;
            categoriaDiv.appendChild(categoriaHeader);
            
            // Crear checkbox para cada permiso en la categoría
            permisosPorCategoria[categoria].forEach(permiso => {
                const isChecked = permisosSeleccionados.some(p => p.id === permiso.id);
                
                const permisoDiv = document.createElement('div');
                permisoDiv.className = 'flex items-center mb-2';
                
                permisoDiv.innerHTML = `
                    <input type="checkbox" id="permiso_${permiso.id}" name="permisos[]" value="${permiso.id}" 
                           class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                           ${isChecked ? 'checked' : ''}>
                    <label for="permiso_${permiso.id}" class="ml-2 block text-sm text-gray-900">
                        ${permiso.nombre}
                        <span class="text-xs text-gray-500 block">${permiso.descripcion || ''}</span>
                    </label>
                `;
                
                categoriaDiv.appendChild(permisoDiv);
            });
            
            permisosContainer.appendChild(categoriaDiv);
        });
    }

    // Función para editar un rol existente
    function editarRol(rolId) {
        // Obtener datos del rol desde la API
        fetch(`/api/roles/${rolId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al cargar el rol');
                }
                return response.json();
            })
            .then(rol => {
                currentRolId = rol.id;
                document.getElementById('modalTitle').textContent = 'Editar Rol';
                document.getElementById('rolId').value = rol.id;
                document.getElementById('nombre').value = rol.nombre;
                document.getElementById('descripcion').value = rol.descripcion || '';
                
                mostrarPermisos(rol.permisos || []);
                
                // Mostrar el modal
                modalRol.classList.remove('hidden');
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion('error', 'Error al cargar el rol: ' + error.message);
            });
    }

    // Función para guardar un rol (crear o actualizar)
    function guardarRol(formData) {
        const rolId = document.getElementById('rolId').value;
        const url = rolId ? `/api/roles/${rolId}` : '/api/roles';
        const method = rolId ? 'PUT' : 'POST';
        
        // Obtener los permisos seleccionados
        const permisosSeleccionados = Array.from(document.querySelectorAll('input[name="permisos[]"]:checked'))
            .map(checkbox => checkbox.value);
        
        // Crear el objeto de datos a enviar
        const data = {
            nombre: formData.get('nombre'),
            descripcion: formData.get('descripcion'),
            permisos: permisosSeleccionados
        };
        
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.detail || 'Error al guardar el rol');
                });
            }
            return response.json();
        })
        .then(data => {
            // Cerrar el modal
            modalRol.classList.add('hidden');
            
            // Mostrar notificación de éxito
            mostrarNotificacion('exito', `Rol ${rolId ? 'actualizado' : 'creado'} correctamente`);
            
            // Recargar la lista de roles
            cargarRoles(searchRoles.value);
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('error', error.message);
        });
    }

    // Función para ver los usuarios asignados a un rol
    function verUsuariosRol(rolId, rolNombre) {
        // Establecer el nombre del rol en el título
        document.getElementById('nombreRolUsuarios').textContent = rolNombre;
        
        // Mostrar mensaje de carga
        listaUsuariosRol.innerHTML = '<li class="animate-pulse text-center text-gray-400 py-4">Cargando usuarios...</li>';
        
        // Mostrar el modal
        modalUsuariosRol.classList.remove('hidden');
        
        // Cargar los usuarios del rol
        fetch(`/api/roles/${rolId}/usuarios`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al cargar usuarios');
                }
                return response.json();
            })
            .then(usuarios => {
                if (usuarios.length === 0) {
                    listaUsuariosRol.innerHTML = '<li class="text-center text-gray-500 py-4">No hay usuarios asignados a este rol</li>';
                    return;
                }
                
                listaUsuariosRol.innerHTML = '';
                
                usuarios.forEach(usuario => {
                    const li = document.createElement('li');
                    li.className = 'py-4';
                    
                    li.innerHTML = `
                        <div class="flex items-center space-x-4">
                            <div class="flex-shrink-0">
                                <div class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                                    <span class="text-gray-600 font-medium">${usuario.nombre.charAt(0).toUpperCase()}</span>
                                </div>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-medium text-gray-900 truncate">
                                    ${usuario.nombre}
                                </p>
                                <p class="text-sm text-gray-500 truncate">
                                    ${usuario.usuario} | ${usuario.mail || 'Sin email'}
                                </p>
                            </div>
                            <div>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    usuario.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }">
                                    ${usuario.activo ? 'Activo' : 'Inactivo'}
                                </span>
                            </div>
                        </div>
                    `;
                    
                    listaUsuariosRol.appendChild(li);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                listaUsuariosRol.innerHTML = `<li class="text-center text-red-500 py-4">Error: ${error.message}</li>`;
            });
    }

    // Función para mostrar el modal de confirmación de eliminación
    function confirmarEliminarRol(rolId, rolNombre) {
        currentRolId = rolId;
        nombreRolEliminar.textContent = rolNombre;
        modalConfirmarEliminar.classList.remove('hidden');
    }

    // Función para eliminar un rol
    function eliminarRol() {
        if (!currentRolId) return;
        
        fetch(`/api/roles/${currentRolId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.detail || 'Error al eliminar el rol');
                });
            }
            return response.json();
        })
        .then(data => {
            // Cerrar el modal
            modalConfirmarEliminar.classList.add('hidden');
            
            // Mostrar notificación de éxito
            mostrarNotificacion('exito', 'Rol eliminado correctamente');
            
            // Recargar la lista de roles
            cargarRoles(searchRoles.value);
        })
        .catch(error => {
            console.error('Error:', error);
            modalConfirmarEliminar.classList.add('hidden');
            mostrarNotificacion('error', error.message);
        });
    }

    // Función para mostrar notificaciones
    function mostrarNotificacion(tipo, mensaje) {
        const notificacion = tipo === 'exito' ? notificacionExito : notificacionError;
        const mensajeElement = tipo === 'exito' ? mensajeExito : mensajeError;
        
        mensajeElement.textContent = mensaje;
        
        // Mostrar la notificación
        notificacion.classList.remove('translate-x-full', 'opacity-0');
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            notificacion.classList.add('translate-x-full', 'opacity-0');
        }, 5000);
    }

    // Configurar todos los event listeners
    function configurarEventListeners() {
        // Botón Nuevo Rol
        btnNuevoRol.addEventListener('click', mostrarFormularioNuevoRol);
        
        // Botones para cerrar el modal
        btnCerrarModal.addEventListener('click', () => modalRol.classList.add('hidden'));
        btnCancelar.addEventListener('click', () => modalRol.classList.add('hidden'));
        modalBackdrop.addEventListener('click', () => modalRol.classList.add('hidden'));
        
        // Modal de usuarios
        btnCerrarModalUsuarios.addEventListener('click', () => modalUsuariosRol.classList.add('hidden'));
        btnCerrarListaUsuarios.addEventListener('click', () => modalUsuariosRol.classList.add('hidden'));
        document.getElementById('modalUsuariosBackdrop').addEventListener('click', () => modalUsuariosRol.classList.add('hidden'));
        
        // Modal de confirmación de eliminación
        btnCancelarEliminar.addEventListener('click', () => modalConfirmarEliminar.classList.add('hidden'));
        document.getElementById('modalEliminarBackdrop').addEventListener('click', () => modalConfirmarEliminar.classList.add('hidden'));
        btnConfirmarEliminar.addEventListener('click', eliminarRol);
        
        // Formulario
        formRol.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(formRol);
            guardarRol(formData);
        });
        
        // Filtros y búsqueda
        btnAplicarFiltros.addEventListener('click', () => {
            currentPage = 1;
            cargarRoles(searchRoles.value);
        });
        
        searchRoles.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                currentPage = 1;
                cargarRoles(searchRoles.value);
                e.preventDefault();
            }
        });
        
        // Paginación
        btnAnterior.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                cargarRoles(searchRoles.value);
            }
        });
        
        btnSiguiente.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                cargarRoles(searchRoles.value);
            }
        });
        
        btnAnteriorMobile.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                cargarRoles(searchRoles.value);
            }
        });
        
        btnSiguienteMobile.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                cargarRoles(searchRoles.value);
            }
        });
    }
});