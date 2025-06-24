document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    let usuarios = [];
    let paginaActual = 1;
    let usuariosPorPagina = 10;
    let usuarioIdActual = null;
    let totalPaginas = 0;

    // Elementos del DOM
    const usuariosTableBody = document.getElementById('usuariosTableBody');
    const startRange = document.getElementById('startRange');
    const endRange = document.getElementById('endRange');
    const totalUsuarios = document.getElementById('totalUsuarios');
    const paginationNumbers = document.getElementById('paginationNumbers');
    const btnAnterior = document.getElementById('btnAnterior');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const btnAnteriorMobile = document.getElementById('btnAnteriorMobile');
    const btnSiguienteMobile = document.getElementById('btnSiguienteMobile');
    const searchUsuarios = document.getElementById('searchUsuarios');
    const filterRol = document.getElementById('filterRol');
    const filterEstado = document.getElementById('filterEstado');
    const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');
    
    // Elementos del modal
    const modalUsuario = document.getElementById('modalUsuario');
    const modalTitle = document.getElementById('modalTitle');
    const formUsuario = document.getElementById('formUsuario');
    const usuarioId = document.getElementById('usuarioId');
    const btnNuevoUsuario = document.getElementById('btnNuevoUsuario');
    const btnCerrarModal = document.getElementById('btnCerrarModal');
    const btnCancelar = document.getElementById('btnCancelar');
    
    // Elementos del modal de confirmación
    const modalConfirmarEliminar = document.getElementById('modalConfirmarEliminar');
    const nombreUsuarioEliminar = document.getElementById('nombreUsuarioEliminar');
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    
    // Elementos de notificación
    const notificacionExito = document.getElementById('notificacionExito');
    const mensajeExito = document.getElementById('mensajeExito');
    const notificacionError = document.getElementById('notificacionError');
    const mensajeError = document.getElementById('mensajeError');

    // Cargar usuarios al iniciar
    cargarUsuarios();

    // Cargar componentes (navbar, breadcrumb, etc.)
    if (window.loadComponents) {
        loadComponents();
    } else {
        console.error("La función loadComponents no está disponible");
    }
    // ----- Funciones de carga y renderizado -----
    
    // Cargar usuarios desde el servidor
    function cargarUsuarios() {
        // Mostrar estado de carga
        usuariosTableBody.innerHTML = `
            <tr class="animate-pulse">
                <td colspan="7" class="px-6 py-4 whitespace-nowrap">
                    <div class="text-center text-gray-400">Cargando usuarios...</div>
                </td>
            </tr>
        `;

        // Obtener parámetros de filtro
        const busqueda = searchUsuarios.value.trim();
        const rol = filterRol.value;
        const estado = filterEstado.value;

        // Construir URL con parámetros de consulta
        let url = '/usuarios_admin/usuarios?';
        if (busqueda) url += `search=${encodeURIComponent(busqueda)}&`;
        if (rol) url += `rol=${encodeURIComponent(rol)}&`;
        if (estado) url += `estado=${encodeURIComponent(estado)}&`;

        console.log("URL de la API:", url); // Depuración

        // Realizar la petición a la API
        fetch(url)
            .then(response => {
                console.log("Estado de la respuesta:", response.status); // Depuración
                if (response.status === 401) {
                    console.error("Error de autorización: el usuario no tiene permisos.");
                    throw new Error("No autorizado. Verifique sus permisos.");
                }
                if (!response.ok) {
                    throw new Error(`Error al cargar usuarios: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Datos recibidos:", data); // Depuración
                if (!data || data.length === 0) {
                    console.warn("No se encontraron usuarios en la respuesta de la API.");
                }
                usuarios = data;
                renderizarUsuarios();
                actualizarPaginacion();
            })
            .catch(error => {
                console.error('Error al cargar usuarios:', error);
                mostrarNotificacionError(error.message);
                usuariosTableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="px-6 py-4 whitespace-nowrap">
                            <div class="text-center text-red-500">Error al cargar usuarios. Intente nuevamente.</div>
                        </td>
                    </tr>
                `;
            });
    }
    
     // Renderizar usuarios en la tabla
    function renderizarUsuarios() {
        // Si no hay usuarios, mostrar mensaje
        if (usuarios.length === 0) {
            usuariosTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 whitespace-nowrap">
                        <div class="text-center text-gray-500">No se encontraron usuarios</div>
                    </td>
                </tr>
            `;
            return;
        }
        
        // Calcular índices para paginación
        const inicio = (paginaActual - 1) * usuariosPorPagina;
        const fin = Math.min(inicio + usuariosPorPagina, usuarios.length);
        const usuariosPaginados = usuarios.slice(inicio, fin);
        
        // Actualizar información de paginación
        startRange.textContent = inicio + 1;
        endRange.textContent = fin;
        totalUsuarios.textContent = usuarios.length;
        
        // Renderizar usuarios
        let html = '';
        
        usuariosPaginados.forEach(usuario => {
            // IMPORTANTE: Definir rolMostrar ANTES de usarlo en el template
            let rolMostrar = 'usuario'; // Valor por defecto
            
            // Verificar si usuario.rol existe y no es vacío
            if (usuario.rol) {
                // Si el rol es un string, usarlo directamente
                if (typeof usuario.rol === 'string') {
                    rolMostrar = usuario.rol;
                } 
                // Si es un objeto, intentar obtener el nombre
                else if (typeof usuario.rol === 'object' && usuario.rol !== null) {
                    rolMostrar = usuario.rol.nombre || 'usuario';
                }
            } 
            // Si usuario.roles existe y tiene elementos, usar el primero
            else if (usuario.roles && usuario.roles.length > 0) {
                rolMostrar = usuario.roles[0].nombre || 'usuario';
            }
            
            // Determinar clases para el badge de estado
            let estadoClass = usuario.estado === 'activo' 
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800';
                
            // Formatear fecha de último acceso
            let ultimoAcceso = usuario.ultimo_acceso
                ? new Date(usuario.ultimo_acceso).toLocaleString()
                : 'Nunca';
                
            html += `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="flex-shrink-0 h-10 w-10">
                                <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                                    <span class="text-gray-500 font-medium">${usuario.usuario.substring(0, 2).toUpperCase()}</span>
                                </div>
                            </div>
                            <div class="ml-4">
                                <div class="text-sm font-medium text-gray-900">${usuario.usuario}</div>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">${usuario.nombre || '-'}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">${usuario.email || '-'}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900 capitalize">${rolMostrar}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoClass}">
                            ${usuario.estado || 'inactivo'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${ultimoAcceso}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button data-id="${usuario.id}" class="btn-editar text-blue-600 hover:text-blue-900 mr-3">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button data-id="${usuario.id}" data-nombre="${usuario.nombre || usuario.usuario}" class="btn-eliminar text-red-600 hover:text-red-900">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        usuariosTableBody.innerHTML = html;
        
        // Agregar listeners a botones de acción
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                cargarUsuarioParaEditar(id);
            });
        });
        
        document.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                const nombre = this.getAttribute('data-nombre');
                mostrarConfirmacionEliminar(id, nombre);
            });
        });
    }
    
    // Actualizar la paginación
    function actualizarPaginacion() {
        totalPaginas = Math.ceil(usuarios.length / usuariosPorPagina);
        
        // Actualizar estado de botones anterior/siguiente
        btnAnterior.disabled = paginaActual <= 1;
        btnSiguiente.disabled = paginaActual >= totalPaginas;
        btnAnteriorMobile.disabled = paginaActual <= 1;
        btnSiguienteMobile.disabled = paginaActual >= totalPaginas;
        
        btnAnterior.classList.toggle('opacity-50', paginaActual <= 1);
        btnSiguiente.classList.toggle('opacity-50', paginaActual >= totalPaginas);
        btnAnteriorMobile.classList.toggle('opacity-50', paginaActual <= 1);
        btnSiguienteMobile.classList.toggle('opacity-50', paginaActual >= totalPaginas);
        
        // Generar números de página
        let paginationHTML = '';
        
        // Limitar el número de botones de página para no saturar la UI
        const maxPagesToShow = 5;
        let startPage = Math.max(1, paginaActual - Math.floor(maxPagesToShow / 2));
        let endPage = Math.min(totalPaginas, startPage + maxPagesToShow - 1);
        
        // Ajustar el rango si estamos cerca del final
        if (endPage - startPage + 1 < maxPagesToShow && startPage > 1) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
        }
        
        // Botón para la primera página si no es visible
        if (startPage > 1) {
            paginationHTML += `
                <button data-page="1" class="pagination-number relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                    1
                </button>
            `;
            
            // Ellipsis si hay un salto
            if (startPage > 2) {
                paginationHTML += `
                    <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                        ...
                    </span>
                `;
            }
        }
        
        // Números de página
        for (let i = startPage; i <= endPage; i++) {
            const isActive = i === paginaActual;
            const activeClass = isActive
                ? 'bg-blue-50 border-blue-500 text-blue-600 z-10'
                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50';
                
            paginationHTML += `
                <button data-page="${i}" class="pagination-number relative inline-flex items-center px-4 py-2 border ${activeClass} text-sm font-medium">
                    ${i}
                </button>
            `;
        }
        
        // Botón para la última página si no es visible
        if (endPage < totalPaginas) {
            // Ellipsis si hay un salto
            if (endPage < totalPaginas - 1) {
                paginationHTML += `
                    <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                        ...
                    </span>
                `;
            }
            
            paginationHTML += `
                <button data-page="${totalPaginas}" class="pagination-number relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                    ${totalPaginas}
                </button>
            `;
        }
        
        paginationNumbers.innerHTML = paginationHTML;
        
        // Agregar event listeners a los botones de paginación
        document.querySelectorAll('.pagination-number').forEach(btn => {
            btn.addEventListener('click', function() {
                const pagina = parseInt(this.getAttribute('data-page'));
                paginaActual = pagina;
                renderizarUsuarios();
                actualizarPaginacion();
            });
        });
    }
    
    // ----- Funciones de gestión de usuarios -----
    
    // Cargar usuario para editar
// Función para cargar un usuario para editar
function cargarUsuarioParaEditar(id) {
    const usuario = usuarios.find(u => u.id == id);
    if (!usuario) {
        mostrarNotificacionError('Usuario no encontrado');
        return;
    }
    
    console.log("Cargando usuario para editar:", usuario);
    
    try {
        // Verificar y actualizar elementos del modal para edición
        if (modalTitle) {
            modalTitle.textContent = 'Editar Usuario';
        }
        
        if (usuarioId) {
            usuarioId.value = usuario.id;
        }
        
        // Actualizar variable global
        usuarioIdActual = usuario.id;
        
        // Capturar elementos y verificar que existan antes de asignar valores
        // Usar funciones auxiliares para evitar errores
        setValueSafely('usuario', usuario.usuario);
        setValueSafely('nombre', usuario.nombre);
        setValueSafely('email', usuario.email);
        setValueSafely('password', ''); // No mostrar contraseña actual
        
        // Manejar el rol con cuidado ya que podría venir en diferentes formatos
        let rolValue = 'usuario'; // Valor por defecto
        
        if (typeof usuario.rol === 'string') {
            rolValue = usuario.rol;
        } else if (usuario.rol && usuario.rol.id) {
            rolValue = usuario.rol.id;
        } else if (usuario.roles && usuario.roles.length > 0) {
            rolValue = usuario.roles[0].id || usuario.roles[0].nombre || 'usuario';
        }
        
        setValueSafely('rol', rolValue);
        setValueSafely('estado', usuario.estado || 'activo');
        
        // Mostrar el modal
        mostrarModal();
    } catch (error) {
        console.error("Error al cargar datos para editar:", error);
        mostrarNotificacionError("Error al cargar el formulario de edición");
    }
}
// Función de ayuda para establecer valores de manera segura
function setValueSafely(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        if (element.type === 'checkbox') {
            element.checked = !!value;
        } else {
            element.value = value || '';
        }
    } else {
        console.warn(`Elemento con ID '${elementId}' no encontrado en el DOM`);
    }
}   
    // Preparar formulario para nuevo usuario
    function prepararNuevoUsuario() {
        // Actualizar modal para modo creación
        modalTitle.textContent = 'Nuevo Usuario';
        usuarioId.value = '';
        usuarioIdActual = null;
        
        // Limpiar el formulario
        document.getElementById('usuario').value = '';
        document.getElementById('nombre').value = '';
        document.getElementById('email').value = '';
        document.getElementById('password').value = '';
        document.getElementById('rol').value = 'usuario'; // Valor por defecto
        document.getElementById('estado').value = 'activo'; // Valor por defecto
        
        // Mostrar el modal
        mostrarModal();
    }
    
// Función mejorada para mostrar el modal
function mostrarModal() {
    try {
        // Verificar si los elementos existen antes de manipularlos
        const backdropElement = document.getElementById('modalBackdrop');
        
        if (!modalUsuario) {
            throw new Error("El modal de usuario no existe en el DOM");
        }
        
        // Mostrar backdrop y modal
        if (backdropElement) {
            backdropElement.classList.remove('hidden');
            
            // Animación de entrada
            setTimeout(() => {
                backdropElement.classList.add('opacity-50');
            }, 10);
        }
        
        modalUsuario.classList.remove('hidden');
        
        // Animación de entrada
        setTimeout(() => {
            modalUsuario.classList.add('opacity-100');
            modalUsuario.classList.add('translate-y-0');
        }, 10);
        
        // Intentar enfocar el primer campo
        const usuarioInput = document.getElementById('usuario');
        if (usuarioInput) {
            usuarioInput.focus();
        }
    } catch (error) {
        console.error("Error al mostrar el modal:", error);
        mostrarNotificacionError("No se pudo mostrar el formulario");
    }
}
    
    // Ocultar modal de usuario
    function ocultarModal() {
        // Animación de salida
        document.getElementById('modalBackdrop').classList.remove('opacity-50');
        modalUsuario.classList.remove('opacity-100');
        modalUsuario.classList.remove('translate-y-0');
        
        // Ocultar después de la animación
        setTimeout(() => {
            document.getElementById('modalBackdrop').classList.add('hidden');
            modalUsuario.classList.add('hidden');
        }, 300);
    }
    
    // Mostrar confirmación para eliminar usuario
    function mostrarConfirmacionEliminar(id, nombre) {
        usuarioIdActual = id;
        nombreUsuarioEliminar.textContent = nombre;
        
        // Mostrar backdrop y modal
        document.getElementById('modalEliminarBackdrop').classList.remove('hidden');
        modalConfirmarEliminar.classList.remove('hidden');
        
        // Animación de entrada
        setTimeout(() => {
            document.getElementById('modalEliminarBackdrop').classList.add('opacity-50');
            modalConfirmarEliminar.classList.add('opacity-100');
            modalConfirmarEliminar.classList.add('translate-y-0');
        }, 10);
    }
    
    // Ocultar confirmación para eliminar usuario
    function ocultarConfirmacionEliminar() {
        // Animación de salida
        document.getElementById('modalEliminarBackdrop').classList.remove('opacity-50');
        modalConfirmarEliminar.classList.remove('opacity-100');
        modalConfirmarEliminar.classList.remove('translate-y-0');
        
        // Ocultar después de la animación
        setTimeout(() => {
            document.getElementById('modalEliminarBackdrop').classList.add('hidden');
            modalConfirmarEliminar.classList.add('hidden');
        }, 300);
    }
    
    // Guardar usuario (crear o actualizar)
    function guardarUsuario(event) {
        event.preventDefault();

        const datos = {
            usuario: formUsuario.usuario.value,
            nombre: formUsuario.nombre.value,
            email: formUsuario.email.value,
            password: formUsuario.password.value
        };

        // Validar datos antes de enviar
        if (!datos.usuario || !datos.nombre || !datos.email) {
            mostrarNotificacionError('Todos los campos son obligatorios');
            return;
        }

        // Determinar si es creación o edición
        const url = usuarioIdActual 
            ? `/usuarios_admin/usuarios/${usuarioIdActual}` 
            : '/usuarios_admin/usuarios';
        const method = usuarioIdActual ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.detail || 'Error al guardar usuario');
                });
            }
            return response.json();
        })
        .then(data => {
            // Cerrar modal
            ocultarModal();

            // Mostrar notificación de éxito
            mostrarNotificacionExito(usuarioIdActual 
                ? 'Usuario actualizado correctamente' 
                : 'Usuario creado correctamente');

            // Recargar lista de usuarios
            cargarUsuarios();
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacionError(error.message);
        });
    }
    
    // Eliminar usuario
    function eliminarUsuario() {
        if (!usuarioIdActual) {
            mostrarNotificacionError('No se ha seleccionado ningún usuario');
            return;
        }
        
        // ACTUALIZADO: Usar la ruta correcta del router
        fetch(`/usuarios_admin/usuarios/${usuarioIdActual}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.detail || 'Error al eliminar usuario');
                });
            }
            return response.json();
        })
        .then(data => {
            // Cerrar modal de confirmación
            ocultarConfirmacionEliminar();
            
            // Mostrar notificación de éxito
            mostrarNotificacionExito('Usuario eliminado correctamente');
            
            // Recargar lista de usuarios
            cargarUsuarios();
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacionError(error.message);
        });
    }
    
    // ----- Funciones de notificación -----
    
    // Mostrar notificación de éxito
    function mostrarNotificacionExito(mensaje) {
        // 1. Ocultar notificación de error si está visible
        ocultarNotificacionError();
        
        // 2. Actualizar mensaje
        mensajeExito.textContent = mensaje;
        
        // 3. Mostrar elemento
        notificacionExito.classList.remove('hidden');
        notificacionExito.classList.remove('translate-x-full');
        notificacionExito.classList.add('translate-x-0');
        notificacionExito.classList.add('opacity-100');
        
        // 4. Ocultar automáticamente después de 3 segundos
        setTimeout(() => {
            ocultarNotificacionExito();
        }, 3000);
    }
    
    // Ocultar notificación de éxito
    function ocultarNotificacionExito() {
        notificacionExito.classList.remove('translate-x-0');
        notificacionExito.classList.remove('opacity-100');
        notificacionExito.classList.add('translate-x-full');
        
        setTimeout(() => {
            notificacionExito.classList.add('hidden');
        }, 300);
    }
    
    // Mostrar notificación de error
    function mostrarNotificacionError(mensaje) {
        // 1. Ocultar notificación de éxito si está visible
        ocultarNotificacionExito();
        
        // 2. Actualizar mensaje
        mensajeError.textContent = mensaje;
        
        // 3. Mostrar elemento
        notificacionError.classList.remove('hidden');
        notificacionError.classList.remove('translate-x-full');
        notificacionError.classList.add('translate-x-0');
        notificacionError.classList.add('opacity-100');
        
        // 4. Ocultar automáticamente después de 4 segundos
        setTimeout(() => {
            ocultarNotificacionError();
        }, 4000);
    }
    
    // Ocultar notificación de error
    function ocultarNotificacionError() {
        notificacionError.classList.remove('translate-x-0');
        notificacionError.classList.remove('opacity-100');
        notificacionError.classList.add('translate-x-full');
        
        setTimeout(() => {
            notificacionError.classList.add('hidden');
        }, 300);
    }




    // ----- Event Listeners -----
    
    // Botón para crear nuevo usuario
    btnNuevoUsuario.addEventListener('click', prepararNuevoUsuario);
    
    // Botones para cerrar modal
    btnCerrarModal.addEventListener('click', ocultarModal);
    btnCancelar.addEventListener('click', ocultarModal);
    
    // Envío de formulario
    formUsuario.addEventListener('submit', guardarUsuario);
    
    // Botones para cancelar y confirmar eliminación
    btnCancelarEliminar.addEventListener('click', ocultarConfirmacionEliminar);
    btnConfirmarEliminar.addEventListener('click', eliminarUsuario);
    
    // Botones de paginación
    btnAnterior.addEventListener('click', () => {
        if (paginaActual > 1) {
            paginaActual--;
            renderizarUsuarios();
            actualizarPaginacion();
        }
    });
    
    btnSiguiente.addEventListener('click', () => {
        if (paginaActual < totalPaginas) {
            paginaActual++;
            renderizarUsuarios();
            actualizarPaginacion();
        }
    });
    
    btnAnteriorMobile.addEventListener('click', () => {
        if (paginaActual > 1) {
            paginaActual--;
            renderizarUsuarios();
            actualizarPaginacion();
        }
    });
    
    btnSiguienteMobile.addEventListener('click', () => {
        if (paginaActual < totalPaginas) {
            paginaActual++;
            renderizarUsuarios();
            actualizarPaginacion();
        }
    });
    
    // Botón para aplicar filtros
    btnAplicarFiltros.addEventListener('click', () => {
        paginaActual = 1; // Volver a la primera página al filtrar
        cargarUsuarios();
    });
    
    // Buscar al presionar Enter en el campo de búsqueda
    searchUsuarios.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            paginaActual = 1;
            cargarUsuarios();
        }
    });
    
    // Cerrar modales al hacer clic en el backdrop
    document.getElementById('modalBackdrop').addEventListener('click', (e) => {
        if (e.target === document.getElementById('modalBackdrop')) {
            ocultarModal();
        }
    });
    
    document.getElementById('modalEliminarBackdrop').addEventListener('click', (e) => {
        if (e.target === document.getElementById('modalEliminarBackdrop')) {
            ocultarConfirmacionEliminar();
        }
    });
    
    // Si tienes estos elementos en tu HTML, activa los listeners
    // Si no existen, estas líneas no tendrán efecto
    const btnCerrarNotificacionExito = document.getElementById('btnCerrarNotificacionExito');
    const btnCerrarNotificacionError = document.getElementById('btnCerrarNotificacionError');
    
    if (btnCerrarNotificacionExito) {
        btnCerrarNotificacionExito.addEventListener('click', ocultarNotificacionExito);
    }
    
    if (btnCerrarNotificacionError) {
        btnCerrarNotificacionError.addEventListener('click', ocultarNotificacionError);
    }
    
    // Interceptor global para fetch: agrega Authorization si hay token en localStorage
    const originalFetch = window.fetch;
    window.fetch = function(input, init = {}) {
        // Si la URL es relativa y apunta a /usuarios_admin, agrega el header
        let url = typeof input === 'string' ? input : input.url;
        if (url && url.startsWith('/usuarios_admin')) {
            const token = localStorage.getItem('access_token');
            if (token) {
                init.headers = init.headers || {};
                // Si ya existe Authorization, no lo sobrescribas
                if (!init.headers['Authorization'] && !init.headers['authorization']) {
                    init.headers['Authorization'] = 'Bearer ' + token;
                }
            }
        }
        return originalFetch(input, init);
    };
});