/**
 * JavaScript para la gestión de stock_historico
 * Generado automáticamente
 */

// Variables globales
let allData = [];
let currentItemId = null;

// Cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar eventos
    document.getElementById('data-form').addEventListener('submit', addItem);
    document.getElementById('edit-form').addEventListener('submit', updateItem);
    document.getElementById('search-input').addEventListener('input', filterTable);
    document.getElementById('reset-search').addEventListener('click', resetSearch);
    document.getElementById('confirm-delete').addEventListener('click', confirmDelete);
    document.getElementById('cancel-delete').addEventListener('click', closeDeleteModal);
    
    // Cargar datos iniciales
    fetchData();
});

/**
 * Obtiene los datos del servidor y actualiza la tabla
 */
async function fetchData() {
    try {
        const response = await fetch('/stock_historico/');
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Verificar si la respuesta es un array
        if (!Array.isArray(data)) {
            console.error("La respuesta no es un array:", data);
            showToast('Error al cargar los datos. La respuesta no tiene el formato esperado.', 'error');
            return;
        }
        
        // Guardar datos para filtrado
        allData = data;
        
        // Actualizar la UI
        updateTable(data);
        updateRecordCount(data.length);
        
    } catch (error) {
        console.error("Error al cargar datos:", error);
        showToast(`Error al cargar los datos: ${error.message}`, 'error');
        
        const tableBody = document.getElementById('data-table-body');
        tableBody.innerHTML = `
            <tr>
                <td colspan="12" class="px-6 py-4 text-center text-red-500">
                    <i class="fas fa-exclamation-circle mr-2"></i>
                    Error al cargar datos. Intente recargar la página.
                </td>
            </tr>
        `;
    }
}

/**
 * Actualiza la tabla con los datos proporcionados
 */
function updateTable(data) {
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = '';
    
    if (data.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="12" class="px-6 py-4 text-center text-gray-500">
                    No se encontraron registros
                </td>
            </tr>
        `;
        return;
    }
    
    data.forEach((item, index) => {
        const row = document.createElement('tr');
        row.className = index % 2 === 0 ? 'bg-white' : 'bg-gray-50';
        row.classList.add('hover:bg-blue-50', 'transition-colors');
        
        // Crear celdas para cada campo
        
        // id
        const cell0 = document.createElement('td');
        cell0.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell0.textContent = item.id;
        row.appendChild(cell0);
        
        // nro_movimiento
        const cell1 = document.createElement('td');
        cell1.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell1.textContent = item.nro_movimiento;
        row.appendChild(cell1);
        
        // codigo_art
        const cell2 = document.createElement('td');
        cell2.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell2.textContent = item.codigo_art;
        row.appendChild(cell2);
        
        // id_articulos_serie
        const cell3 = document.createElement('td');
        cell3.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell3.textContent = item.id_articulos_serie;
        row.appendChild(cell3);
        
        // id_deposito
        const cell4 = document.createElement('td');
        cell4.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell4.textContent = item.id_deposito;
        row.appendChild(cell4);
        
        // cant_disponible
        const cell5 = document.createElement('td');
        cell5.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell5.textContent = item.cant_disponible;
        row.appendChild(cell5);
        
        // cant_reservado
        const cell6 = document.createElement('td');
        cell6.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell6.textContent = item.cant_reservado;
        row.appendChild(cell6);
        
        // cant_preparado
        const cell7 = document.createElement('td');
        cell7.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell7.textContent = item.cant_preparado;
        row.appendChild(cell7);
        
        // tipo
        const cell8 = document.createElement('td');
        cell8.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        if (typeof item.tipo === "boolean") {
            cell8.innerHTML = item.tipo ? '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Sí</span>' : '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">No</span>';
        }
        row.appendChild(cell8);
        
        // fecha
        const cell9 = document.createElement('td');
        cell9.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell9.textContent = item.fecha;
        row.appendChild(cell9);
        
        // observacion
        const cell10 = document.createElement('td');
        cell10.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell10.textContent = item.observacion;
        row.appendChild(cell10);
        
        
        // Celda de acciones
        const actionsCell = document.createElement('td');
        actionsCell.className = 'px-6 py-4 whitespace-nowrap text-right text-sm font-medium';
        actionsCell.innerHTML = `
            <button class="bg-blue-100 text-blue-700 hover:bg-blue-200 px-3 py-1 rounded-md mr-2 hover-raise" onclick="editItem(${item.id})">
                <i class="fas fa-edit mr-1"></i> Editar
            </button>
            <button class="bg-red-100 text-red-700 hover:bg-red-200 px-3 py-1 rounded-md hover-raise" onclick="showDeleteModal(${item.id})">
                <i class="fas fa-trash-alt mr-1"></i> Eliminar
            </button>
        `;
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

/**
 * Actualiza el contador de registros
 */
function updateRecordCount(count) {
    const recordCount = document.getElementById('record-count');
    recordCount.textContent = count === 1 
        ? '1 registro encontrado' 
        : `${count} registros encontrados`;
}

/**
 * Añade un nuevo registro
 */
async function addItem(event) {
    event.preventDefault();
    
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Guardando...';
    
    const formData = {
        id: parseInt(document.getElementById('id').value) || 0,
        nro_movimiento: parseInt(document.getElementById('nro_movimiento').value) || 0,
        codigo_art: parseInt(document.getElementById('codigo_art').value) || 0,
        id_articulos_serie: parseInt(document.getElementById('id_articulos_serie').value) || 0,
        id_deposito: parseInt(document.getElementById('id_deposito').value) || 0,
        cant_disponible: parseFloat(document.getElementById('cant_disponible').value) || 0,
        cant_reservado: parseFloat(document.getElementById('cant_reservado').value) || 0,
        cant_preparado: parseFloat(document.getElementById('cant_preparado').value) || 0,
        tipo: document.getElementById('tipo').checked,
        fecha: document.getElementById('fecha').value,
        observacion: document.getElementById('observacion').value
    };
    
    try {
        const response = await fetch('/stock_historico/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al crear el registro");
        }
        
        const result = await response.json();
        console.log("Registro creado:", result);
        
        // Limpiar formulario
        document.getElementById('data-form').reset();
        
        // Refrescar datos
        fetchData();
        
        // Mostrar notificación
        showToast('Registro creado correctamente', 'success');
        
    } catch (error) {
        console.error("Error:", error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-save mr-2"></i> Guardar';
    }
}

/**
 * Muestra el modal de edición con los datos del registro
 */
function editItem(id) {
    fetch(`/stock_historico/id/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos del registro");
            }
            return response.json();
        })
        .then(data => {
            // Guardar el ID actual
            currentItemId = id;
            
            // Rellenar el formulario
            document.getElementById('edit-id').value = data.id;
            
            document.getElementById('edit-nro_movimiento').value = data.nro_movimiento;document.getElementById('edit-codigo_art').value = data.codigo_art;document.getElementById('edit-id_articulos_serie').value = data.id_articulos_serie;document.getElementById('edit-id_deposito').value = data.id_deposito;document.getElementById('edit-cant_disponible').value = data.cant_disponible;document.getElementById('edit-cant_reservado').value = data.cant_reservado;document.getElementById('edit-cant_preparado').value = data.cant_preparado;document.getElementById('edit-tipo').checked = data.tipo;document.getElementById('edit-fecha').value = data.fecha;document.getElementById('edit-observacion').value = data.observacion;
            
            // Mostrar el modal
            document.getElementById('edit-modal').classList.remove('hidden');
        })
        .catch(error => {
            console.error("Error al obtener datos para editar:", error);
            showToast(`Error: ${error.message}`, 'error');
        });
}

/**
 * Cierra el modal de edición
 */
function closeEditModal() {
    document.getElementById('edit-modal').classList.add('hidden');
    currentItemId = null;
}

/**
 * Actualiza un registro
 */
async function updateItem(event) {
    event.preventDefault();
    
    if (!currentItemId) {
        showToast('Error: No se pudo identificar el registro a actualizar', 'error');
        return;
    }
    
    const id = currentItemId;
    const updatedData = {
        nro_movimiento: parseInt(document.getElementById('edit-nro_movimiento').value) || 0,
        codigo_art: parseInt(document.getElementById('edit-codigo_art').value) || 0,
        id_articulos_serie: parseInt(document.getElementById('edit-id_articulos_serie').value) || 0,
        id_deposito: parseInt(document.getElementById('edit-id_deposito').value) || 0,
        cant_disponible: parseFloat(document.getElementById('edit-cant_disponible').value) || 0,
        cant_reservado: parseFloat(document.getElementById('edit-cant_reservado').value) || 0,
        cant_preparado: parseFloat(document.getElementById('edit-cant_preparado').value) || 0,
        tipo: document.getElementById('edit-tipo').checked,
        fecha: document.getElementById('edit-fecha').value,
        observacion: document.getElementById('edit-observacion').value
    };
    
    try {
        const response = await fetch(`/stock_historico/id/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al actualizar el registro");
        }
        
        // Cerrar modal y refrescar datos
        closeEditModal();
        fetchData();
        
        // Mostrar notificación
        showToast('Registro actualizado correctamente', 'success');
        
    } catch (error) {
        console.error("Error:", error);
        showToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Muestra el modal de confirmación para eliminar
 */
function showDeleteModal(id) {
    currentItemId = id;
    document.getElementById('delete-modal').classList.remove('hidden');
}

/**
 * Cierra el modal de confirmación para eliminar
 */
function closeDeleteModal() {
    document.getElementById('delete-modal').classList.add('hidden');
    currentItemId = null;
}

/**
 * Elimina un registro después de confirmar
 */
async function confirmDelete() {
    if (!currentItemId) {
        showToast('Error: No se pudo identificar el registro a eliminar', 'error');
        closeDeleteModal();
        return;
    }
    
    const id = currentItemId;
    
    try {
        const response = await fetch(`/stock_historico/id/${id}`, { method: 'DELETE' });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al eliminar el registro");
        }
        
        // Cerrar modal y refrescar datos
        closeDeleteModal();
        fetchData();
        
        // Mostrar notificación
        showToast('Registro eliminado correctamente', 'success');
        
    } catch (error) {
        console.error("Error:", error);
        showToast(`Error: ${error.message}`, 'error');
        closeDeleteModal();
    }
}

/**
 * Filtra la tabla según el texto de búsqueda
 */
function filterTable() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    
    if (!searchTerm) {
        updateTable(allData);
        updateRecordCount(allData.length);
        return;
    }
    
    const filteredData = allData.filter(item => {
        return String(item.id).toLowerCase().includes(searchTerm) || String(item.nro_movimiento).toLowerCase().includes(searchTerm) || String(item.codigo_art).toLowerCase().includes(searchTerm) || String(item.id_articulos_serie).toLowerCase().includes(searchTerm) || String(item.id_deposito).toLowerCase().includes(searchTerm) || String(item.cant_disponible).toLowerCase().includes(searchTerm) || String(item.cant_reservado).toLowerCase().includes(searchTerm) || String(item.cant_preparado).toLowerCase().includes(searchTerm) || String(item.tipo).toLowerCase().includes(searchTerm) || String(item.fecha).toLowerCase().includes(searchTerm) || String(item.observacion).toLowerCase().includes(searchTerm);
    });
    
    updateTable(filteredData);
    updateRecordCount(filteredData.length);
}

/**
 * Restablece la búsqueda
 */
function resetSearch() {
    document.getElementById('search-input').value = '';
    updateTable(allData);
    updateRecordCount(allData.length);
}

/**
 * Muestra/oculta la descripción
 */
function toggleDescription() {
    const description = document.getElementById('description');
    description.classList.toggle('hidden');
}

/**
 * Muestra una notificación toast
 */
function showToast(message, type = 'success') {
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
