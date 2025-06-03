/**
 * JavaScript para la gestión de Órdenes de Trabajo (OT)
 * Este archivo maneja todas las interacciones con la API para OTs, operaciones y reportes de tiempo
 */

// Variables globales
let allOts = [];
let currentOtId = null;
let currentOperacionId = null;
let currentReporteId = null;
let selectedOtOperaciones = null;
let selectedOtReportes = null;
let selectedOperacionReportes = null;

// Cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar eventos para tabs
    setupTabSystem();
    
    // Eventos para la gestión de OTs
    document.getElementById('ot-form').addEventListener('submit', crearOt);
    document.getElementById('search-ot-input').addEventListener('input', filtrarOts);
    document.getElementById('reset-ot-search').addEventListener('click', resetBusquedaOt);
    document.getElementById('filter-estado').addEventListener('change', filtrarOts);
    
    // Eventos para operaciones
    document.getElementById('select-ot-operaciones').addEventListener('change', seleccionarOtOperaciones);
    document.getElementById('operacion-form')?.addEventListener('submit', crearOperacion);
    document.getElementById('edit-operacion-form')?.addEventListener('submit', actualizarOperacion);
    
    // Eventos para reportes de tiempo
    document.getElementById('select-ot-reportes').addEventListener('change', seleccionarOtReportes);
    document.getElementById('select-operacion-reportes')?.addEventListener('change', seleccionarOperacionReportes);
    document.getElementById('reporte-tiempo-form')?.addEventListener('submit', crearReporteTiempo);
    
    // Eventos para modales de confirmación
    document.getElementById('confirm-delete').addEventListener('click', confirmarEliminacion);
    document.getElementById('cancel-delete').addEventListener('click', cerrarModalEliminar);
    
    // Botón finalizar OT
    document.getElementById('btn-finalizar-ot')?.addEventListener('click', finalizarOt);
    
    // Cargar datos iniciales
    cargarOts();
    cargarDepositos();
});

/************************
 * CONFIGURACIÓN INICIAL
 ************************/

/**
 * Configura el sistema de tabs
 */
function setupTabSystem() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Desactivar todos los botones y contenidos
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Activar el botón clickeado y su contenido correspondiente
            button.classList.add('active');
            const targetTab = button.getAttribute('data-tab');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

/**************************
 * GESTIÓN DE OT
 **************************/

/**
 * Carga las OTs desde el servidor
 */
async function cargarOts() {
    try {
        const response = await fetch('/ot/');
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Verificar si la respuesta es un array
        if (!Array.isArray(data)) {
            console.error("La respuesta no es un array:", data);
            mostrarToast('Error al cargar las OTs. La respuesta no tiene el formato esperado.', 'error');
            return;
        }
        
        // Guardar datos para filtrado
        allOts = data;
        
        // Actualizar la UI
        actualizarTarjetasOt(data);
        actualizarSelectOt(data);
        
    } catch (error) {
        console.error("Error al cargar OTs:", error);
        mostrarToast(`Error al cargar las OTs: ${error.message}`, 'error');
        
        const container = document.getElementById('ot-cards-container');
        container.innerHTML = `
            <div class="col-span-full bg-red-50 p-4 rounded-lg shadow-sm text-center text-red-500">
                <i class="fas fa-exclamation-circle text-xl mb-2"></i>
                <p>Error al cargar las órdenes de trabajo. Intente recargar la página.</p>
            </div>
        `;
    }
}

/**
 * Carga los depósitos disponibles para el selector
 */
async function cargarDepositos() {
    try {
        // Aquí podrías hacer una llamada a la API para obtener los depósitos
        // Por ahora usaremos datos de ejemplo
        const data = [
            { id: 1, nombre: "Depósito Principal" },
            { id: 2, nombre: "Depósito Secundario" },
            { id: 3, nombre: "Depósito de Repuestos" }
        ];
        
        const selectDeposito = document.getElementById('id_deposito');
        
        // Limpiar opciones existentes excepto la primera
        while (selectDeposito.options.length > 1) {
            selectDeposito.remove(1);
        }
        
        // Agregar opciones
        data.forEach(dep => {
            const option = document.createElement('option');
            option.value = dep.id;
            option.textContent = dep.nombre;
            selectDeposito.appendChild(option);
        });
        
    } catch (error) {
        console.error("Error al cargar depósitos:", error);
        mostrarToast("Error al cargar depósitos", "error");
    }
}

/**
 * Actualiza el listado de OT en forma de tarjetas
 */
function actualizarTarjetasOt(data) {
    const container = document.getElementById('ot-cards-container');
    container.innerHTML = '';
    
    // Remover el loader
    const loader = document.getElementById('loading-ots');
    if (loader) {
        loader.remove();
    }
    
    if (data.length === 0) {
        container.innerHTML = `
            <div class="col-span-full bg-white p-4 rounded-lg shadow-sm text-center text-gray-500">
                <i class="fas fa-search text-xl mb-2"></i>
                <p>No se encontraron órdenes de trabajo</p>
            </div>
        `;
        return;
    }
    
    data.forEach(ot => {
        const estadoClase = `estado-${ot.estado || 'pendiente'}`;
        const fechaCreadaFormat = ot.fecha_creacion ? new Date(ot.fecha_creacion).toLocaleDateString() : 'N/A';
        
        const tarjeta = document.createElement('div');
        tarjeta.className = 'bg-white rounded-lg shadow-sm p-4 card-ot';
        tarjeta.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <h3 class="font-semibold text-lg text-gray-800">${ot.titulo || ot.id_trabajo || `OT #${ot.id}`}</h3>
                <span class="px-2 py-1 rounded-full text-xs font-medium ${estadoClase}">
                    ${ot.estado || 'pendiente'}
                </span>
            </div>
            <div class="mb-3">
                <div class="text-sm text-gray-600 mb-1"><span class="font-medium">ID:</span> ${ot.id}</div>
                <div class="text-sm text-gray-600 mb-1"><span class="font-medium">Trabajo:</span> ${ot.id_trabajo || 'N/A'}</div>
                <div class="text-sm text-gray-600 mb-1"><span class="font-medium">Área:</span> ${ot.area || 'N/A'}</div>
                <div class="text-sm text-gray-600"><span class="font-medium">Fecha:</span> ${fechaCreadaFormat}</div>
            </div>
            <div class="border-t border-gray-100 pt-3 flex justify-between">
                <button onclick="verOt(${ot.id})" class="text-blue-600 hover:text-blue-800 text-sm flex items-center">
                    <i class="fas fa-eye mr-1"></i> Ver detalles
                </button>
                <div>
                    <button onclick="editarOt(${ot.id})" class="text-yellow-600 hover:text-yellow-800 text-sm mr-2">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="mostrarModalEliminar('ot', ${ot.id})" class="text-red-600 hover:text-red-800 text-sm">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(tarjeta);
    });
}

/**
 * Actualiza los selectores de OT
 */
function actualizarSelectOt(data) {
    const selectOtOperaciones = document.getElementById('select-ot-operaciones');
    const selectOtReportes = document.getElementById('select-ot-reportes');
    
    // Limpiar opciones existentes excepto la primera
    while (selectOtOperaciones.options.length > 1) {
        selectOtOperaciones.remove(1);
    }
    
    while (selectOtReportes.options.length > 1) {
        selectOtReportes.remove(1);
    }
    
    // Agregar opciones
    data.forEach(ot => {
        const optionText = `${ot.id} - ${ot.titulo || ot.id_trabajo || 'Sin título'}`;
        
        const optionOperaciones = document.createElement('option');
        optionOperaciones.value = ot.id;
        optionOperaciones.textContent = optionText;
        selectOtOperaciones.appendChild(optionOperaciones);
        
        const optionReportes = document.createElement('option');
        optionReportes.value = ot.id;
        optionReportes.textContent = optionText;
        selectOtReportes.appendChild(optionReportes);
    });
}

/**
 * Crea una nueva OT
 */
async function crearOt(event) {
    event.preventDefault();
    
    const submitBtn = document.getElementById('submit-ot-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Creando...';
    
    const formData = {
        id_trabajo: document.getElementById('id_trabajo').value,
        titulo: document.getElementById('titulo').value,
        area: document.getElementById('area').value,
        personal: document.getElementById('personal').value,
        tiempo_estimado: document.getElementById('tiempo_estimado').value,
        descripcion: document.getElementById('descripcion').value,
        id_deposito: document.getElementById('id_deposito').value || null
    };
    
    try {
        const response = await fetch('/ot/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al crear la OT");
        }
        
        const result = await response.json();
        console.log("OT creada:", result);
        
        // Limpiar formulario
        document.getElementById('ot-form').reset();
        
        // Refrescar datos
        cargarOts();
        
        // Mostrar notificación
        mostrarToast('OT creada correctamente', 'success');
        
        // Redirigir a la tab de operaciones con la OT seleccionada
        document.querySelector('[data-tab="tab-operaciones"]').click();
        setTimeout(() => {
            document.getElementById('select-ot-operaciones').value = result.id;
            seleccionarOtOperaciones({target: {value: result.id}});
        }, 500);
        
    } catch (error) {
        console.error("Error:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-save mr-2"></i> Crear Orden de Trabajo';
    }
}

/**
 * Muestra el modal con los detalles de una OT
 */
async function verOt(id) {
    try {
        const response = await fetch(`/ot/id/${id}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const ot = await response.json();
        currentOtId = id;
        
        const detalleContainer = document.getElementById('ot-detalle-container');
        const btnFinalizarOt = document.getElementById('btn-finalizar-ot');
        
        // Estado para mostrar/ocultar botón de finalizar
        const mostrarBotonFinalizar = ot.estado === 'en_proceso';
        btnFinalizarOt.classList.toggle('hidden', !mostrarBotonFinalizar);
        btnFinalizarOt.style.display = mostrarBotonFinalizar ? 'flex' : 'none';
        
        // Formatear fechas
        const fechaCreacion = ot.fecha_creacion ? new Date(ot.fecha_creacion).toLocaleString() : 'N/A';
        const fechaInicio = ot.fecha_inicio ? new Date(ot.fecha_inicio).toLocaleString() : 'N/A';
        const fechaFin = ot.fecha_fin ? new Date(ot.fecha_fin).toLocaleString() : 'N/A';
        
        // HTML para el contenido del modal
        detalleContainer.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">${ot.titulo || 'Sin título'}</h3>
                    <div class="space-y-2">
                        <div><span class="font-medium text-gray-700">ID:</span> ${ot.id}</div>
                        <div><span class="font-medium text-gray-700">ID Trabajo:</span> ${ot.id_trabajo}</div>
                        <div><span class="font-medium text-gray-700">Área:</span> ${ot.area || 'N/A'}</div>
                        <div><span class="font-medium text-gray-700">Personal:</span> ${ot.personal || 'N/A'}</div>
                        <div><span class="font-medium text-gray-700">Depósito:</span> ${ot.id_deposito || 'N/A'}</div>
                        <div><span class="font-medium text-gray-700">Tiempo Estimado:</span> ${ot.tiempo_estimado || 'N/A'}</div>
                    </div>
                </div>
                <div>
                    <div class="bg-gray-50 p-3 rounded-lg mb-3">
                        <div class="text-sm">
                            <div class="mb-2"><span class="font-medium text-gray-700">Estado:</span>
                                <span class="px-2 py-1 rounded-full text-xs font-medium estado-${ot.estado || 'pendiente'} ml-2">
                                    ${ot.estado || 'pendiente'}
                                </span>
                            </div>
                            <div class="mb-2"><span class="font-medium text-gray-700">Fecha Creación:</span> ${fechaCreacion}</div>
                            <div class="mb-2"><span class="font-medium text-gray-700">Fecha Inicio:</span> ${fechaInicio}</div>
                            <div><span class="font-medium text-gray-700">Fecha Finalización:</span> ${fechaFin}</div>
                        </div>
                    </div>
                    <div>
                        <h4 class="font-medium text-gray-700 mb-2">Descripción:</h4>
                        <p class="text-gray-600 bg-gray-50 p-3 rounded-lg text-sm">${ot.descripcion || 'Sin descripción'}</p>
                    </div>
                </div>
            </div>
            <div class="border-t border-gray-200 pt-4">
                <h3 class="text-md font-semibold text-gray-800 mb-3">Operaciones</h3>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Orden</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Responsable</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tiempo Est.</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200" id="operaciones-modal-body">
                            ${ot.operaciones && ot.operaciones.length > 0 ? 
                                ot.operaciones.map(op => `
                                    <tr>
                                        <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800">${op.orden}</td>
                                        <td class="px-4 py-2 text-sm text-gray-800">${op.descripcion}</td>
                                        <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800">${op.responsable || 'N/A'}</td>
                                        <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800">${op.tiempo_estimado || 'N/A'}</td>
                                        <td class="px-4 py-2 whitespace-nowrap text-sm">
                                            <span class="px-2 py-1 rounded-full text-xs font-medium estado-${op.estado || 'pendiente'}">
                                                ${op.estado || 'pendiente'}
                                            </span>
                                        </td>
                                    </tr>
                                `).join('') : 
                                `<tr><td colspan="5" class="px-4 py-3 text-sm text-gray-500 text-center">No hay operaciones registradas</td></tr>`
                            }
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        // Mostrar el modal
        document.getElementById('ver-ot-modal').classList.remove('hidden');
    } catch (error) {
        console.error("Error al obtener detalles de OT:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Finaliza una OT
 */
async function finalizarOt() {
    if (!currentOtId) {
        mostrarToast('No se pudo identificar la OT a finalizar', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/ot/id/${currentOtId}/finalizar`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "No se pudo finalizar la OT");
        }
        
        // Cerrar modal y recargar datos
        closeVerOtModal();
        cargarOts();
        
        mostrarToast('OT finalizada correctamente', 'success');
    } catch (error) {
        console.error("Error al finalizar OT:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Filtra las OT según texto de búsqueda y estado seleccionado
 */
function filtrarOts() {
    const searchTerm = document.getElementById('search-ot-input').value.toLowerCase();
    const estadoFiltro = document.getElementById('filter-estado').value;
    
    let filteredData = [...allOts];
    
    // Filtrar por estado
    if (estadoFiltro) {
        filteredData = filteredData.filter(ot => ot.estado === estadoFiltro);
    }
    
    // Filtrar por texto
    if (searchTerm) {
        filteredData = filteredData.filter(ot => {
            return (
                String(ot.id).toLowerCase().includes(searchTerm) || 
                (ot.id_trabajo && ot.id_trabajo.toLowerCase().includes(searchTerm)) ||
                (ot.titulo && ot.titulo.toLowerCase().includes(searchTerm)) ||
                (ot.area && ot.area.toLowerCase().includes(searchTerm)) ||
                (ot.personal && ot.personal.toLowerCase().includes(searchTerm)) ||
                (ot.descripcion && ot.descripcion.toLowerCase().includes(searchTerm))
            );
        });
    }
    
    actualizarTarjetasOt(filteredData);
}

/**
 * Resetea la búsqueda y filtros de OT
 */
function resetBusquedaOt() {
    document.getElementById('search-ot-input').value = '';
    document.getElementById('filter-estado').value = '';
    actualizarTarjetasOt(allOts);
}

/**************************
 * GESTIÓN DE OPERACIONES
 **************************/

/**
 * Maneja el cambio en el selector de OT para operaciones
 */
async function seleccionarOtOperaciones(event) {
    const otId = event.target.value;
    const container = document.getElementById('operaciones-container');
    
    if (!otId) {
        container.classList.add('hidden');
        return;
    }
    
    try {
        const response = await fetch(`/ot/id/${otId}/operaciones`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const operaciones = await response.json();
        selectedOtOperaciones = otId;
        
        // Mostrar el contenedor de operaciones
        container.classList.remove('hidden');
        
        // Actualizar tabla de operaciones
        actualizarTablaOperaciones(operaciones);
        
    } catch (error) {
        console.error("Error al cargar operaciones:", error);
        mostrarToast(`Error al cargar operaciones: ${error.message}`, 'error');
        container.classList.add('hidden');
    }
}

/**
 * Actualiza la tabla de operaciones
 */
function actualizarTablaOperaciones(operaciones) {
    const tableBody = document.getElementById('operaciones-table-body');
    tableBody.innerHTML = '';
    
    if (operaciones.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    No hay operaciones registradas para esta OT
                </td>
            </tr>
        `;
        return;
    }
    
    operaciones.forEach(op => {
        const row = document.createElement('tr');
        const estadoClase = `estado-${op.estado || 'pendiente'}`;
        
        // Calcular el total de horas reportadas
        let horasReportadas = 0;
        if (op.reportes_tiempo && op.reportes_tiempo.length > 0) {
            horasReportadas = op.reportes_tiempo.reduce((total, rep) => total + rep.horas, 0);
        }
        
        row.innerHTML = `
            <td class="px-6 py-3 whitespace-nowrap text-sm text-gray-800">${op.orden || 'N/A'}</td>
            <td class="px-6 py-3 text-sm text-gray-800">${op.descripcion}</td>
            <td class="px-6 py-3 whitespace-nowrap text-sm text-gray-800">${op.responsable || 'N/A'}</td>
            <td class="px-6 py-3 whitespace-nowrap text-sm text-gray-800">${op.tiempo_estimado || 'N/A'}</td>
            <td class="px-6 py-3 whitespace-nowrap text-sm">
                <span class="px-2 py-1 rounded-full text-xs font-medium ${estadoClase}">
                    ${op.estado || 'pendiente'}
                </span>
            </td>
            <td class="px-6 py-3 whitespace-nowrap text-sm text-gray-800">${horasReportadas.toFixed(1)}</td>
            <td class="px-6 py-3 whitespace-nowrap text-right text-sm font-medium">
                <button class="text-blue-600 hover:text-blue-800 mr-2" onclick="registrarTiempo(${op.id})">
                    <i class="fas fa-clock"></i>
                </button>
                <button class="text-yellow-600 hover:text-yellow-800 mr-2" onclick="editarOperacion(${op.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="text-red-600 hover:text-red-800" onclick="mostrarModalEliminar('operacion', ${op.id})">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Crea una nueva operación para la OT seleccionada
 */
async function crearOperacion(event) {
    event.preventDefault();
    
    if (!selectedOtOperaciones) {
        mostrarToast('No se ha seleccionado una OT', 'error');
        return;
    }
    
    const submitBtn = document.getElementById('submit-operacion-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Agregando...';
    
    const formData = {
        ot_id: parseInt(selectedOtOperaciones),
        descripcion: document.getElementById('operacion-descripcion').value,
        tiempo_estimado: document.getElementById('operacion-tiempo').value || null,
        responsable: document.getElementById('operacion-responsable').value || null,
        orden: parseInt(document.getElementById('operacion-orden').value) || null
    };
    
    try {
        const response = await fetch('/ot/operaciones', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al crear la operación");
        }
        
        // Limpiar formulario
        document.getElementById('operacion-form').reset();
        document.getElementById('operacion-orden').value = 1;
        
        // Recargar operaciones
        const event = { target: { value: selectedOtOperaciones } };
        seleccionarOtOperaciones(event);
        
        mostrarToast('Operación agregada correctamente', 'success');
        
    } catch (error) {
        console.error("Error:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus-circle mr-2"></i> Agregar Operación';
    }
}

/**
 * Muestra el modal de edición de operación
 */
async function editarOperacion(id) {
    try {
        const response = await fetch(`/ot/operaciones/id/${id}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const operacion = await response.json();
        currentOperacionId = id;
        
        // Rellenar el formulario de edición
        document.getElementById('edit-operacion-id').value = operacion.id;
        document.getElementById('edit-operacion-descripcion').value = operacion.descripcion;
        document.getElementById('edit-operacion-responsable').value = operacion.responsable || '';
        document.getElementById('edit-operacion-tiempo').value = operacion.tiempo_estimado || '';
        document.getElementById('edit-operacion-orden').value = operacion.orden || 1;
        document.getElementById('edit-operacion-estado').value = operacion.estado || 'pendiente';
        
        // Mostrar el modal
        document.getElementById('edit-operacion-modal').classList.remove('hidden');
        
    } catch (error) {
        console.error("Error al obtener operación:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Actualiza una operación
 */
async function actualizarOperacion(event) {
    event.preventDefault();
    
    if (!currentOperacionId) {
        mostrarToast('No se pudo identificar la operación a actualizar', 'error');
        return;
    }
    
    try {
        const formData = {
            descripcion: document.getElementById('edit-operacion-descripcion').value,
            responsable: document.getElementById('edit-operacion-responsable').value || null,
            tiempo_estimado: document.getElementById('edit-operacion-tiempo').value || null,
            orden: parseInt(document.getElementById('edit-operacion-orden').value) || null,
            estado: document.getElementById('edit-operacion-estado').value
        };
        
        const response = await fetch(`/ot/operaciones/id/${currentOperacionId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al actualizar la operación");
        }
        
        // Cerrar modal
        closeEditOperacionModal();
        
        // Recargar operaciones
        const event = { target: { value: selectedOtOperaciones } };
        seleccionarOtOperaciones(event);
        
        // También recargar las OTs
        cargarOts();
        
        mostrarToast('Operación actualizada correctamente', 'success');
        
    } catch (error) {
        console.error("Error:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Finalizará directamente una operación cuando se presiona el botón
 */
async function finalizarOperacion(id) {
    try {
        const response = await fetch(`/ot/operaciones/id/${id}/finalizar`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al finalizar la operación");
        }
        
        // Recargar operaciones
        const event = { target: { value: selectedOtOperaciones } };
        seleccionarOtOperaciones(event);
        
        // También recargar las OTs
        cargarOts();
        
        mostrarToast('Operación finalizada correctamente', 'success');
        
    } catch (error) {
        console.error("Error:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Redirige a la pestaña de reportes de tiempo con la operación seleccionada
 */
function registrarTiempo(operacionId) {
    // Buscar la OT de esta operación
    fetch(`/ot/operaciones/id/${operacionId}`)
        .then(response => response.json())
        .then(operacion => {
            const otId = operacion.ot_id;
            
            // Cambiar a la pestaña de reportes
            document.querySelector('[data-tab="tab-reportes"]').click();
            
            // Seleccionar la OT y la operación
            setTimeout(() => {
                document.getElementById('select-ot-reportes').value = otId;
                
                // Simular el evento change
                const event = { target: { value: otId } };
                seleccionarOtReportes(event);
                
                // Esperar a que se carguen las operaciones y seleccionar la operación
                setTimeout(() => {
                    document.getElementById('select-operacion-reportes').value = operacionId;
                    
                    // Simular el evento change para cargar los reportes de tiempo
                    const opEvent = { target: { value: operacionId } };
                    seleccionarOperacionReportes(opEvent);
                }, 500);
            }, 300);
        })
        .catch(error => {
            console.error("Error:", error);
            mostrarToast(`Error: ${error.message}`, 'error');
        });
}

/**************************
 * GESTIÓN DE REPORTES DE TIEMPO
 **************************/

/**
 * Maneja el cambio en el selector de OT para reportes de tiempo
 */
async function seleccionarOtReportes(event) {
    const otId = event.target.value;
    const selectOperacionContainer = document.getElementById('select-operacion-container');
    const reporteContainer = document.getElementById('reporte-tiempo-container');
    
    if (!otId) {
        selectOperacionContainer.classList.add('hidden');
        reporteContainer.classList.add('hidden');
        return;
    }
    
    try {
        const response = await fetch(`/ot/id/${otId}/operaciones`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const operaciones = await response.json();
        selectedOtReportes = otId;
        
        // Actualizar el selector de operaciones
        const selectOperacion = document.getElementById('select-operacion-reportes');
        
        // Limpiar opciones existentes excepto la primera
        while (selectOperacion.options.length > 1) {
            selectOperacion.remove(1);
        }
        
        // Agregar opciones
        operaciones.forEach(op => {
            const option = document.createElement('option');
            option.value = op.id;
            option.textContent = `${op.orden || ''} - ${op.descripcion}`;
            selectOperacion.appendChild(option);
        });
        
        // Mostrar selector de operaciones
        selectOperacionContainer.classList.remove('hidden');
        
        // Ocultar sección de reportes hasta que se seleccione una operación
        reporteContainer.classList.add('hidden');
        
    } catch (error) {
        console.error("Error al cargar operaciones:", error);
        mostrarToast(`Error al cargar operaciones: ${error.message}`, 'error');
        selectOperacionContainer.classList.add('hidden');
        reporteContainer.classList.add('hidden');
    }
}

/**
 * Maneja el cambio en el selector de operación para reportes de tiempo
 */
async function seleccionarOperacionReportes(event) {
    const operacionId = event.target.value;
    const reporteContainer = document.getElementById('reporte-tiempo-container');
    
    if (!operacionId) {
        reporteContainer.classList.add('hidden');
        return;
    }
    
    try {
        const response = await fetch(`/ot/operaciones/id/${operacionId}/tiempos`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const reportes = await response.json();
        selectedOperacionReportes = operacionId;
        
        // Mostrar sección de reportes
        reporteContainer.classList.remove('hidden');
        
        // Actualizar tabla de reportes
        actualizarTablaReportes(reportes);
        
    } catch (error) {
        console.error("Error al cargar reportes de tiempo:", error);
        mostrarToast(`Error al cargar reportes: ${error.message}`, 'error');
        reporteContainer.classList.add('hidden');
    }
}

/**
 * Actualiza la tabla de reportes de tiempo
 */
function actualizarTablaReportes(reportes) {
    const tableBody = document.getElementById('reportes-table-body');
    tableBody.innerHTML = '';
    
    if (reportes.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                    No hay reportes de tiempo para esta operación
                </td>
            </tr>
        `;
        return;
    }
    
    reportes.forEach(reporte => {
        const row = document.createElement('tr');
        
        // Formatear fecha
        const fecha = reporte.fecha ? new Date(reporte.fecha).toLocaleString() : 'N/A';
        
        row.innerHTML = `
            <td class="px-6 py-3 whitespace-nowrap text-sm text-gray-800">${fecha}</td>
            <td class="px-6 py-3 text-sm text-gray-800">${reporte.horas}</td>
            <td class="px-6 py-3 text-sm text-gray-800">${reporte.usuario}</td>
            <td class="px-6 py-3 text-sm text-gray-800">${reporte.descripcion || ''}</td>
            <td class="px-6 py-3 whitespace-nowrap text-right text-sm font-medium">
                <button class="text-red-600 hover:text-red-800" onclick="mostrarModalEliminar('reporte', ${reporte.id})">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Crea un nuevo reporte de tiempo
 */
async function crearReporteTiempo(event) {
    event.preventDefault();
    
    if (!selectedOperacionReportes) {
        mostrarToast('No se ha seleccionado una operación', 'error');
        return;
    }
    
    const submitBtn = document.getElementById('submit-reporte-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Registrando...';
    
    const formData = {
        operacion_id: parseInt(selectedOperacionReportes),
        horas: parseFloat(document.getElementById('reporte-horas').value),
        usuario: document.getElementById('reporte-usuario').value,
        descripcion: document.getElementById('reporte-descripcion').value || null
    };
    
    try {
        const response = await fetch('/ot/tiempos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al registrar tiempo");
        }
        
        // Limpiar formulario
        document.getElementById('reporte-tiempo-form').reset();
        
        // Recargar reportes
        const event = { target: { value: selectedOperacionReportes } };
        seleccionarOperacionReportes(event);
        
        mostrarToast('Tiempo registrado correctamente', 'success');
        
    } catch (error) {
        console.error("Error:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus-circle mr-2"></i> Registrar Tiempo';
    }
}

/**************************
 * FUNCIONES AUXILIARES
 **************************/

/**
 * Solicita confirmación al usuario antes de continuar con una iteración
 * @param {function} callbackSuccess - Función a ejecutar si el usuario confirma
 * @param {function} callbackCancel - Función opcional a ejecutar si el usuario cancela
 */
function confirmarIteracion(callbackSuccess, callbackCancel = null) {
    // Crear modal de confirmación si no existe
    if (!document.getElementById('confirmacion-iteracion-modal')) {
        const modal = document.createElement('div');
        modal.id = 'confirmacion-iteracion-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden';
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                <h3 class="text-lg font-semibold text-gray-800 mb-3">Confirmar acción</h3>
                <p class="text-gray-600 mb-4">¿Desea continuar con la iteración?</p>
                <div class="flex justify-end space-x-3">
                    <button id="cancel-iteracion" class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
                        Cancelar
                    </button>
                    <button id="confirm-iteracion" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                        Continuar
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Agregar eventos
        document.getElementById('confirm-iteracion').addEventListener('click', function() {
            document.getElementById('confirmacion-iteracion-modal').classList.add('hidden');
            if (typeof callbackSuccess === 'function') callbackSuccess();
        });
        
        document.getElementById('cancel-iteracion').addEventListener('click', function() {
            document.getElementById('confirmacion-iteracion-modal').classList.add('hidden');
            if (typeof callbackCancel === 'function') callbackCancel();
        });
    }
    
    // Mostrar el modal
    document.getElementById('confirmacion-iteracion-modal').classList.remove('hidden');
}

/**
 * Muestra el modal de confirmación para eliminar
 */
function mostrarModalEliminar(tipo, id) {
    const modalEliminar = document.getElementById('delete-modal');
    const mensajeEliminar = document.getElementById('delete-message');
    
    let mensaje = '¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.';
    
    // Guardar tipo y ID para la eliminación
    modalEliminar.setAttribute('data-tipo', tipo);
    modalEliminar.setAttribute('data-id', id);
    
    if (tipo === 'ot') {
        mensaje = '¿Está seguro de que desea eliminar esta Orden de Trabajo? Se eliminarán todas sus operaciones y reportes de tiempo asociados. Esta acción no se puede deshacer.';
    } else if (tipo === 'operacion') {
        mensaje = '¿Está seguro de que desea eliminar esta operación? Se eliminarán todos los reportes de tiempo asociados. Esta acción no se puede deshacer.';
    } else if (tipo === 'reporte') {
        mensaje = '¿Está seguro de que desea eliminar este reporte de tiempo? Esta acción no se puede deshacer.';
    }
    
    mensajeEliminar.textContent = mensaje;
    modalEliminar.classList.remove('hidden');
}

/**
 * Cierra el modal de confirmación para eliminar
 */
function cerrarModalEliminar() {
    document.getElementById('delete-modal').classList.add('hidden');
}

/**
 * Confirma la eliminación del elemento seleccionado
 */
async function confirmarEliminacion() {
    const modal = document.getElementById('delete-modal');
    const tipo = modal.getAttribute('data-tipo');
    const id = modal.getAttribute('data-id');
    
    if (!tipo || !id) {
        mostrarToast('Error: No se pudo identificar el elemento a eliminar', 'error');
        cerrarModalEliminar();
        return;
    }
    
    try {
        let url = '';
        
        if (tipo === 'ot') {
            url = `/ot/id/${id}`;
        } else if (tipo === 'operacion') {
            url = `/ot/operaciones/id/${id}`;
        } else if (tipo === 'reporte') {
            url = `/ot/tiempos/id/${id}`;
        }
        
        const response = await fetch(url, { method: 'DELETE' });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al eliminar el elemento");
        }
        
        // Cerrar modal
        cerrarModalEliminar();
        
        // Recargar datos según el tipo eliminado
        if (tipo === 'ot') {
            cargarOts();
        } else if (tipo === 'operacion') {
            const event = { target: { value: selectedOtOperaciones } };
            seleccionarOtOperaciones(event);
            cargarOts(); // Recargar OTs también, por si cambió el estado
        } else if (tipo === 'reporte') {
            const event = { target: { value: selectedOperacionReportes } };
            seleccionarOperacionReportes(event);
        }
        
        mostrarToast(`${tipo.charAt(0).toUpperCase() + tipo.slice(1)} eliminado correctamente`, 'success');
        
    } catch (error) {
        console.error("Error:", error);
        mostrarToast(`Error: ${error.message}`, 'error');
        cerrarModalEliminar();
    }
}

/**
 * Función para cerrar el modal de detalles de OT
 */
function closeVerOtModal() {
    document.getElementById('ver-ot-modal').classList.add('hidden');
    currentOtId = null;
}

/**
 * Función para cerrar el modal de edición de operación
 */
function closeEditOperacionModal() {
    document.getElementById('edit-operacion-modal').classList.add('hidden');
    currentOperacionId = null;
}

/**
 * Muestra una notificación toast
 */
function mostrarToast(message, type = 'success') {
    // Crear el elemento toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} slide-in`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="${type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Añadir al contenedor
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    // Eliminar después de 5 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 5000);
}
