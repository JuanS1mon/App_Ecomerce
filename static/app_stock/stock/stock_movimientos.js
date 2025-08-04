/**
 * JavaScript para la gestión de movimientos de stock y confirmaciones
 */

// Variables globales
let allData = [];
let currentMovimiento = null;
let detalleMovimiento = [];

// Cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Inicializar eventos
        const searchInput = document.getElementById('search-input');
        const resetSearchBtn = document.getElementById('reset-search');
        
        if (searchInput) {
            searchInput.addEventListener('input', filterTable);
        } else {
            console.error('Elemento search-input no encontrado');
        }
        
        if (resetSearchBtn) {
            resetSearchBtn.addEventListener('click', resetSearch);
        } else {
            console.error('Elemento reset-search no encontrado');
        }
        
        // Añadimos un botón para ver todos los movimientos confirmados y no confirmados
        const searchContainer = document.querySelector('.flex-grow')?.parentNode;
        if (!searchContainer) {
            console.error('Contenedor de búsqueda no encontrado');
            return;
        }
    
    // Crear contenedor para botones de filtro
    const filtroDiv = document.createElement('div');
    filtroDiv.className = 'flex items-center mt-3 md:mt-0 md:ml-4 gap-3';
    filtroDiv.innerHTML = `
        <button id="btn-pendientes" class="bg-amber-100 text-amber-700 px-3 py-2 rounded-md hover:bg-amber-200 transition-colors flex items-center">
            <i class="fas fa-clock mr-2"></i>
            Solo pendientes
        </button>
        <button id="btn-todos" class="bg-blue-100 text-blue-700 px-3 py-2 rounded-md hover:bg-blue-200 transition-colors flex items-center">
            <i class="fas fa-list-ul mr-2"></i>
            Ver todos
        </button>
    `;
      // Insertamos los botones antes del botón "Restablecer"
    const resetButton = document.getElementById('reset-search')?.parentNode;
    if (resetButton) {
        searchContainer.insertBefore(filtroDiv, resetButton);
    } else {
        // Si no encontramos el botón, añadimos al final del contenedor
        searchContainer.appendChild(filtroDiv);
    }
    
    // Mantenemos el checkbox oculto para compatibilidad
    const checkboxDiv = document.createElement('div');
    checkboxDiv.className = 'hidden';
    checkboxDiv.innerHTML = `
        <label class="flex items-center cursor-pointer">
            <input type="checkbox" id="filtro-confirmados" class="form-checkbox h-4 w-4 text-blue-600 rounded">
            <span class="ml-2 text-sm text-gray-700">Mostrar confirmados</span>
        </label>
    `;
    document.body.appendChild(checkboxDiv);
    
    // Eventos para los botones
    const btnPendientes = document.getElementById('btn-pendientes');
    const btnTodos = document.getElementById('btn-todos');
    const filtroConfirmados = document.getElementById('filtro-confirmados');
    
    if (btnPendientes && btnTodos && filtroConfirmados) {
        btnPendientes.addEventListener('click', () => {
            filtroConfirmados.checked = false;
            cambiarFiltroConfirmados();
            btnPendientes.classList.add('bg-amber-200');
            btnTodos.classList.remove('bg-blue-200');
        });
        
        btnTodos.addEventListener('click', () => {
            filtroConfirmados.checked = true;
            cambiarFiltroConfirmados();
            btnTodos.classList.add('bg-blue-200');
            btnPendientes.classList.remove('bg-amber-200');
        });
        
        // Añadimos el evento al checkbox (para compatibilidad con código existente)
        filtroConfirmados.addEventListener('change', cambiarFiltroConfirmados);
    } else {
        console.error('No se pudieron encontrar los elementos para el filtro de confirmados');
    }      // Cargar datos iniciales y marcar el botón de pendientes como seleccionado
    try {
        fetchMovimientosPendientes(false);
    } catch (error) {
        console.error('Error al cargar movimientos pendientes:', error);
        showToast('Error al cargar datos iniciales. Intente recargar la página.', 'error');
    }
    
    // Por defecto, el botón de pendientes está activo
    setTimeout(() => {
        const btnPendientes = document.getElementById('btn-pendientes');
        if (btnPendientes) {
            btnPendientes.classList.add('bg-amber-200');
        }
    }, 100);

    // Buscar la tabla y agregar la columna de estado
    const headerRow = document.querySelector('thead tr');
    
    if (headerRow) {
        // Crear la columna de estado antes de "Acciones"
        const estadoHeader = document.createElement('th');
        estadoHeader.className = 'px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider';
        estadoHeader.innerHTML = 'Estado';
        
        // Insertar antes de la última columna (Acciones)
        headerRow.insertBefore(estadoHeader, headerRow.lastElementChild);
    } else {
        console.error('Fila de encabezado de la tabla no encontrada');
    }

    const resetAllButton = document.querySelector('button[id="reset-all"]');
    if (resetAllButton) {
        resetAllButton.addEventListener('click', resetAllFilters);
    } else {
        const resetSearchButton = document.getElementById('reset-search');
        if (resetSearchButton) {
            // Si no existe el botón específico, usamos el de reset search
            resetSearchButton.addEventListener('click', resetAllFilters);
        }
    }
    
    } catch (error) {
        console.error('Error al inicializar la página:', error);
        showToast('Error al cargar la página. Intente recargar.', 'error');
    }
});

/**
 * Obtiene los movimientos pendientes del servidor y actualiza la tabla
 */
async function fetchMovimientosPendientes(mostrarConfirmados = false) {
    try {
        const url = mostrarConfirmados 
            ? '/stock/movimientos/pendientes?mostrar_confirmados=true' 
            : '/stock/movimientos/pendientes';
        
        const response = await fetch(url);
        
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
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        <i class="fas fa-exclamation-circle mr-2"></i>
                        Error al cargar datos. Intente recargar la página.
                    </td>
                </tr>
            `;
        }
    }
}

/**
 * Actualiza la tabla con los datos proporcionados
 */
function updateTable(data) {
    const tableBody = document.getElementById('data-table-body');
    if (!tableBody) {
        console.error('Elemento data-table-body no encontrado');
        return;
    }
    
    tableBody.innerHTML = '';
    
    if (data.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-4 text-center text-gray-500">
                    No se encontraron movimientos pendientes
                </td>
            </tr>
        `;
        return;
    }
    
    data.forEach((item, index) => {
        const row = document.createElement('tr');
        row.className = index % 2 === 0 ? 'bg-white' : 'bg-gray-50';
        row.classList.add('hover:bg-blue-50', 'transition-colors');
        
        // Nro movimiento
        const cell1 = document.createElement('td');
        cell1.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell1.textContent = item.nro_movimiento;
        row.appendChild(cell1);
        
        // Código artículo
        const cell2 = document.createElement('td');
        cell2.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell2.textContent = item.codigo_art;
        row.appendChild(cell2);
        
        // Fecha
        const cell3 = document.createElement('td');
        cell3.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        cell3.textContent = item.fecha;
        row.appendChild(cell3);        // Depósitos origen-destino 
        const cell4 = document.createElement('td');
        cell4.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        
        // Obtener nombres de depósitos desde todas las posibles fuentes
        let origenNombre = 'Origen';
        let destinoNombre = 'Destino';
        
        // 1. Intentar obtener de campos específicos
        if (item.deposito_origen && item.deposito_origen.trim() !== '') {
            origenNombre = item.deposito_origen;
        }
        
        if (item.deposito_destino && item.deposito_destino.trim() !== '') {
            destinoNombre = item.deposito_destino;
        }
        
        // 2. Si no hay datos en campos específicos, intentar parsear del campo depositos
        if ((origenNombre === 'Origen' || destinoNombre === 'Destino') && item.depositos) {
            // Intentar diferentes separadores comunes
            let depositos = [];
            
            if (item.depositos.includes(' → ')) {
                depositos = item.depositos.split(' → ');
            } else if (item.depositos.includes('->')) {
                depositos = item.depositos.split('->');
            } else if (item.depositos.includes('>')) {
                depositos = item.depositos.split('>');
            } else if (item.depositos.includes('-')) {
                depositos = item.depositos.split('-');
            }
            
            if (depositos.length >= 2) {
                if (origenNombre === 'Origen') {
                    origenNombre = depositos[0].trim();
                }
                if (destinoNombre === 'Destino') {
                    destinoNombre = depositos[1].trim();
                }
            }
        }
        
        // Mostrar el flujo de depósitos con los nombres obtenidos
        cell4.innerHTML = `
            <div class="flex items-center">
                <span class="text-amber-700 font-medium" title="Depósito Origen (Prepara el stock)">
                    ${origenNombre}
                    <i class="fas fa-box text-amber-600 ml-1 text-xs"></i>
                </span>
                <i class="fas fa-arrow-right text-gray-400 mx-1"></i>
                <span class="text-blue-700 font-medium" title="Depósito Destino (Recibe el stock)">
                    ${destinoNombre}
                    <i class="fas fa-inbox text-blue-600 ml-1 text-xs"></i>
                </span>
            </div>
        `;
        row.appendChild(cell4);
        
        // Cantidad preparada (origen)
        const cell5 = document.createElement('td');
        cell5.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        const cantPreparada = parseFloat(item.total_preparado);
        cell5.innerHTML = cantPreparada > 0 
            ? `<span class="badge badge-amber">${cantPreparada.toFixed(2)}</span>` 
            : '-';
        row.appendChild(cell5);
          // Cantidad reservada (destino)
        const cell6 = document.createElement('td');
        cell6.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-800';
        const cantReservada = parseFloat(item.total_reservado);
        cell6.innerHTML = cantReservada > 0 
            ? `<span class="badge badge-blue">${cantReservada.toFixed(2)}</span>` 
            : '-';
        row.appendChild(cell6);        // Estado de confirmación
        const cellEstado = document.createElement('td');
        cellEstado.className = 'px-6 py-4 whitespace-nowrap text-sm text-center';
        cellEstado.id = `estado-${item.nro_movimiento}`;  // Añadir ID para facilitar las actualizaciones
        
        // Detectamos si es una posible confirmación parcial 
        // (si tiene cantidades con decimales o no coinciden preparado/reservado)
        const cantidadFraccionada = (cantPreparada % 1 !== 0) || (cantReservada % 1 !== 0);
        const cantidadesNoCoinciden = Math.abs(cantPreparada - cantReservada) > 0.001;
        const posibleConfirmacionParcial = cantidadFraccionada || cantidadesNoCoinciden;
        
        if (item.confirmado) {
            cellEstado.innerHTML = `
                <span class="badge badge-green">
                    <i class="fas fa-check-circle mr-1"></i> Confirmado
                </span>
            `;
            // Agregar una clase a la fila para los elementos confirmados
            row.classList.add('confirmed-row');
        } else if (posibleConfirmacionParcial) {
            cellEstado.innerHTML = `
                <span class="badge badge-amber">
                    <i class="fas fa-exclamation-circle mr-1"></i> Parcialmente confirmado
                </span>
            `;
            // Añadir una clase específica para estos casos
            row.classList.add('partial-confirmed-row');
        } else {
            cellEstado.innerHTML = `
                <span class="badge badge-gray">
                    <i class="fas fa-clock mr-1"></i> Pendiente
                </span>
            `;
        }
        row.appendChild(cellEstado);
          // Acciones
        const actionsCell = document.createElement('td');
        actionsCell.className = 'px-6 py-4 whitespace-nowrap text-right text-sm font-medium';
        
        // Botones diferentes según el estado
        if (item.confirmado) {
            actionsCell.innerHTML = `
                <div class="flex justify-end gap-2">
                    <button class="bg-blue-100 text-blue-700 hover:bg-blue-200 px-2 py-1 rounded-md hover-raise" 
                        onclick="showDetailModal(${item.nro_movimiento}, ${item.codigo_art})">
                        <i class="fas fa-eye mr-1"></i> Ver
                    </button>
                    <button class="bg-indigo-100 text-indigo-700 hover:bg-indigo-200 px-2 py-1 rounded-md hover-raise"
                        onclick="verHistorialConfirmaciones(${item.nro_movimiento}, ${item.codigo_art})">
                        <i class="fas fa-history mr-1"></i> Historial
                    </button>
                    <button class="bg-yellow-100 text-yellow-700 hover:bg-yellow-200 px-2 py-1 rounded-md hover-raise"
                        onclick="revertirConfirmacion(${item.nro_movimiento}, ${item.codigo_art})">
                        <i class="fas fa-undo mr-1"></i> Revertir
                    </button>
                </div>
            `;
        } else {
            actionsCell.innerHTML = `
                <button class="bg-blue-100 text-blue-700 hover:bg-blue-200 px-3 py-1 rounded-md hover-raise" 
                    onclick="showDetailModal(${item.nro_movimiento}, ${item.codigo_art})">
                    <i class="fas fa-eye mr-1"></i> Ver detalle
                </button>
            `;
        }
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

/**
 * Actualiza el contador de registros
 */
function updateRecordCount(count) {
    const recordCount = document.getElementById('record-count');
    if (!recordCount) {
        console.error('Elemento record-count no encontrado');
        return;
    }
    
    const filtroConfirmados = document.getElementById('filtro-confirmados');
    const mostrarConfirmados = filtroConfirmados ? filtroConfirmados.checked : false;
    
    if (mostrarConfirmados) {
        recordCount.textContent = count === 1 
            ? '1 movimiento en total' 
            : `${count} movimientos en total`;
    } else {
        recordCount.textContent = count === 1 
            ? '1 movimiento pendiente' 
            : `${count} movimientos pendientes`;
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
        return String(item.nro_movimiento).toLowerCase().includes(searchTerm) || 
               String(item.codigo_art).toLowerCase().includes(searchTerm) || 
               String(item.fecha).toLowerCase().includes(searchTerm) || 
               String(item.depositos).toLowerCase().includes(searchTerm);
    });
    
    updateTable(filteredData);
    updateRecordCount(filteredData.length);
}

/**
 * Restablece la búsqueda
 */
function resetSearch() {
    try {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = '';
        } else {
            console.error('Elemento search-input no encontrado');
        }
        
        // Actualizar la tabla con todos los datos disponibles
        updateTable(allData);
        updateRecordCount(allData.length);
    } catch (error) {
        console.error('Error al restablecer búsqueda:', error);
        showToast('Error al restablecer búsqueda. Intente nuevamente.', 'error');
    }
}

/**
 * Restablece todos los filtros y recarga los datos
 */
function resetAllFilters() {
    // Limpiar búsqueda
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
    }
    
    // Desmarcar checkbox de mostrar confirmados
    const filtroConfirmados = document.getElementById('filtro-confirmados');
    if (filtroConfirmados) {
        filtroConfirmados.checked = false;
    }
    
    // Actualizar aspecto de los botones
    const btnPendientes = document.getElementById('btn-pendientes');
    const btnTodos = document.getElementById('btn-todos');
    
    if (btnPendientes) {
        btnPendientes.classList.add('bg-amber-200');
    }
    
    if (btnTodos) {
        btnTodos.classList.remove('bg-blue-200');
    }
    
    // Recargar datos sin filtros
    try {
        fetchMovimientosPendientes(false);
    } catch (error) {
        console.error('Error al restablecer filtros:', error);
        showToast('Error al restablecer filtros. Intente nuevamente.', 'error');
    }
}

/**
 * Muestra el modal de detalle del movimiento
 */
async function showDetailModal(nroMovimiento, codigoArt) {
    currentMovimiento = { nroMovimiento, codigoArt };
    
    // Verificar y actualizar título
    const detailTitle = document.getElementById('detail-title');
    if (detailTitle) {
        detailTitle.textContent = `#${nroMovimiento}`;
    }
    
    // Mostrar el modal si existe
    const detailModal = document.getElementById('detail-modal');
    if (detailModal) {
        detailModal.classList.remove('hidden');
    }
    
    // Restablecer contenido solo si los elementos existen
    const articuloInfo = document.getElementById('articulo-info');
    if (articuloInfo) {
        articuloInfo.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Cargando información...';
    }
    
    const movimientoInfo = document.getElementById('movimiento-info');
    if (movimientoInfo) {
        movimientoInfo.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Cargando información...';
    }
    
    const depositosTable = document.getElementById('depositos-table');
    if (depositosTable) {
        depositosTable.innerHTML = '<tr><td colspan="5" class="px-4 py-3 text-center text-sm text-gray-500"><i class="fas fa-spinner fa-spin mr-2"></i> Cargando depósitos...</td></tr>';
    }
    
    const cantidadConfirmar = document.getElementById('cantidad-confirmar');
    if (cantidadConfirmar) {
        cantidadConfirmar.value = '';
    }
    
    try {
        // Obtener el detalle del movimiento
        const response = await fetch(`/stock/movimientos/detalle/${nroMovimiento}/${codigoArt}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        detalleMovimiento = data;
        
        // Llenar información del artículo si el elemento existe
        if (articuloInfo && data.length > 0) {
            articuloInfo.innerHTML = `
                <div class="grid grid-cols-2 gap-2">
                    <div class="text-gray-500">Código:</div>
                    <div>${codigoArt}</div>
                    
                    <div class="text-gray-500">Descripción:</div>
                    <div>${data[0].articulo_nombre || 'No disponible'}</div>
                    
                    <div class="text-gray-500">Serie:</div>
                    <div>${data[0].id_articulos_serie}</div>
                </div>
            `;
        }
        
        // Llenar información del movimiento si el elemento existe
        if (movimientoInfo && data.length > 0) {
            movimientoInfo.innerHTML = `
                <div class="grid grid-cols-2 gap-2">
                    <div class="text-gray-500">Nro. Movimiento:</div>
                    <div>${nroMovimiento}</div>
                    
                    <div class="text-gray-500">Fecha:</div>
                    <div>${data[0].fecha}</div>
                    
                    <div class="text-gray-500">Observación:</div>
                    <div>${data[0].observacion || '-'}</div>
                </div>
            `;
        }
          
        // Llenar tabla de depósitos si el elemento existe
        if (depositosTable) {
            depositosTable.innerHTML = '';
              // Identificar depósito origen y destino
            // Para entender correctamente el flujo de los movimientos:
            // El origen es el que tiene cantidad preparada (el que va a enviar)
            // El destino es el que tiene cantidad reservada (el que va a recibir)
            
            // Verificar primero el caso especial de depósitos 2 y 3
            const tieneDeposito2 = data.some(d => d.id_deposito === 2);
            const tieneDeposito3 = data.some(d => d.id_deposito === 3);
            let depositoOrigen = null;
            let depositoDestino = null;
            
            // Si ambos depósitos están involucrados, forzamos que 3 sea origen y 2 sea destino
            if (tieneDeposito2 && tieneDeposito3) {
                depositoOrigen = data.find(d => d.id_deposito === 3);
                depositoDestino = data.find(d => d.id_deposito === 2);
                console.log('CASO ESPECIAL: Forzando depósito 3 como origen y depósito 2 como destino');
            } else {
                // Identificación normal usando criterios positivos
                depositoOrigen = data.find(d => d.cant_preparado > 0);
                depositoDestino = data.find(d => d.cant_reservado > 0);
            }

            console.log('Primera búsqueda - Depósito origen (cant_preparado > 0):', depositoOrigen);
            console.log('Primera búsqueda - Depósito destino (cant_reservado > 0):', depositoDestino);
            
            // Si no encontramos alguno de los depósitos con el criterio principal, usamos criterios alternativos
            if (!depositoOrigen) {
                // Buscamos cualquier depósito que tenga preparado diferente de 0
                depositoOrigen = data.find(d => d.cant_preparado != 0);
                console.log('Búsqueda alternativa - Depósito origen (cant_preparado != 0):', depositoOrigen);
                
                // Si aún no hay origen, intentamos identificarlo por disponible negativo
                if (!depositoOrigen) {
                    const depositoDisponibleNegativo = data.find(d => d.cant_disponible < 0);
                    if (depositoDisponibleNegativo) {
                        // Si hay un depósito con disponible negativo y reservado positivo, 
                        // el origen probablemente sea el otro depósito 
                        if (depositoDisponibleNegativo.cant_reservado > 0 && data.length === 2) {
                            depositoOrigen = data.find(d => d.id_deposito !== depositoDisponibleNegativo.id_deposito);
                            console.log('Inferencia por disponible negativo - Depósito origen:', depositoOrigen);
                        }
                    }
                }
                
                // Última alternativa: si aún no hay origen, y hay solo 2 depósitos, el origen es el que NO es destino
                if (!depositoOrigen && depositoDestino && data.length === 2) {
                    depositoOrigen = data.find(d => d.id_deposito !== depositoDestino.id_deposito);
                    console.log('Inferencia automática - Depósito origen por exclusión:', depositoOrigen);
                }
            }
            
            if (!depositoDestino) {
                // Buscamos cualquier depósito que tenga reservado diferente de 0
                depositoDestino = data.find(d => d.cant_reservado != 0);
                console.log('Búsqueda alternativa - Depósito destino (cant_reservado != 0):', depositoDestino);
            }
            
            // Si todavía no tenemos ambos depósitos, inferimos el que falta
            if (depositoOrigen && !depositoDestino && data.length === 2) {
                // Si tenemos origen pero no destino, el destino es el otro depósito
                depositoDestino = data.find(d => d.id_deposito !== depositoOrigen.id_deposito);
                console.log('Inferencia - Depósito destino por descarte:', depositoDestino);
            }
            
            if (!depositoOrigen && depositoDestino && data.length === 2) {
                // Si tenemos destino pero no origen, el origen es el otro depósito
                depositoOrigen = data.find(d => d.id_deposito !== depositoDestino.id_deposito);
                console.log('Inferencia - Depósito origen por descarte:', depositoOrigen);
            }
            
            console.log('Depósito origen final:', depositoOrigen);
            console.log('Depósito destino final:', depositoDestino);
            
            // Calcular las cantidades relevantes para la operación
            const cantidadPreparada = depositoOrigen ? Math.abs(depositoOrigen.cant_preparado) : 0;
            const cantidadReservada = depositoDestino ? Math.abs(depositoDestino.cant_reservado) : 0;
            
            console.log('Cantidad preparada (origen):', cantidadPreparada);
            console.log('Cantidad reservada (destino):', cantidadReservada);
            
            // Actualizamos la advertencia de stock negativo
            const stockWarning = document.getElementById('stock-warning');
            if (stockWarning && (depositoOrigen?.cant_disponible < 0 || depositoDestino?.cant_disponible < 0)) {
                stockWarning.classList.remove('hidden');
            } else if (stockWarning) {
                stockWarning.classList.add('hidden');
            }
            
            // Calcular cantidad máxima a confirmar
            let cantidadMaxima = 0;
            
            // Si ambos valores están presentes, usamos el menor de los dos
            if (cantidadPreparada > 0 && cantidadReservada > 0) {
                cantidadMaxima = Math.min(cantidadPreparada, cantidadReservada);
                console.log('Cantidad máxima calculada (min de ambos):', cantidadMaxima);
            } else if (cantidadPreparada > 0) {
                // Si solo hay preparado, usamos esa cantidad
                cantidadMaxima = cantidadPreparada;
                console.log('Cantidad máxima calculada (solo preparado):', cantidadMaxima);
            } else if (cantidadReservada > 0) {
                // Si solo hay reservado, usamos esa cantidad
                cantidadMaxima = cantidadReservada;
                console.log('Cantidad máxima calculada (solo reservado):', cantidadMaxima);
            } else {
                // Si ninguno tiene valor, intentamos usar cualquier valor disponible
                console.log('No se encontraron cantidades positivas para el cálculo');
            }
              
            // Actualizar visualización del flujo de movimiento
            const flujoMovimiento = document.getElementById('flujo-movimiento');
            if (flujoMovimiento) {
                actualizarVisualizacionFlujo(depositoOrigen, depositoDestino, cantidadMaxima);
            }
                // Si solo tenemos destino pero no origen, mostramos un mensaje informativo
            if (!depositoOrigen && depositoDestino) {
                const avisoDiv = document.createElement('div');
                avisoDiv.className = 'bg-yellow-50 p-3 rounded-lg text-sm text-yellow-800 mb-4';
                avisoDiv.innerHTML = `
                    <div class="flex items-start">
                        <i class="fas fa-info-circle text-yellow-600 mt-0.5 mr-2"></i>
                        <div>
                            <p class="font-medium">Aviso: Solo se identificó el depósito destino</p>
                            <p class="mt-1">Se infiere que el otro depósito es el origen. Verifique antes de confirmar.</p>
                        </div>
                    </div>
                `;
                
                // Buscamos la sección de depósitos
                const depositosTables = document.getElementById('depositos-table')?.closest('.p-4');
                if (depositosTables) {
                    depositosTables.insertBefore(avisoDiv, depositosTables.firstChild);
                }
            }
            
            // Si detectamos el caso especial de depósitos 2 y 3, mostramos una alerta
            if (tieneDeposito2 && tieneDeposito3) {
                const avisoEspecialDiv = document.createElement('div');
                avisoEspecialDiv.className = 'bg-blue-50 p-3 rounded-lg text-sm text-blue-800 mb-4';
                avisoEspecialDiv.innerHTML = `
                    <div class="flex items-start">
                        <i class="fas fa-info-circle text-blue-600 mt-0.5 mr-2"></i>
                        <div>
                            <p class="font-medium">Caso especial: Depósitos 2 y 3</p>
                            <p class="mt-1">Se ha detectado un movimiento entre los depósitos 2 y 3. Se ha configurado automáticamente el depósito 3 como origen y el depósito 2 como destino.</p>
                        </div>
                    </div>
                `;
                
                // Buscamos la sección de depósitos
                const depositosTables = document.getElementById('depositos-table')?.closest('.p-4');
                if (depositosTables) {
                    depositosTables.insertBefore(avisoEspecialDiv, depositosTables.firstChild);
                }
            }
            
            // Actualizar el máximo en la UI
            const maxCantidad = document.getElementById('max-cantidad');
            if (maxCantidad) {
                maxCantidad.textContent = cantidadMaxima.toFixed(2);
            }
            
            const inputCantidad = document.getElementById('cantidad-confirmar');
            if (inputCantidad) {
                inputCantidad.max = cantidadMaxima;
                
                // Establecer el valor inicial y asegurarnos de que se aplique correctamente
                if (cantidadMaxima > 0) {
                    // Establecer al valor máximo calculado
                    inputCantidad.value = cantidadMaxima.toFixed(2);
                } else {
                    // Si la cantidad máxima es 0, verificamos si hay alguna cantidad que podamos usar
                    if (cantidadPreparada > 0) {
                        inputCantidad.value = cantidadPreparada.toFixed(2);
                        if (maxCantidad) maxCantidad.textContent = cantidadPreparada.toFixed(2);
                    } else if (cantidadReservada > 0) {
                        inputCantidad.value = cantidadReservada.toFixed(2);
                        if (maxCantidad) maxCantidad.textContent = cantidadReservada.toFixed(2);
                    } else {
                        // Último recurso: tratar de encontrar algún valor positivo
                        const algunaCantidad = Math.max(cantidadPreparada, cantidadReservada);
                        if (algunaCantidad > 0) {
                            inputCantidad.value = algunaCantidad.toFixed(2);
                            if (maxCantidad) maxCantidad.textContent = algunaCantidad.toFixed(2);
                        } else {
                            // Si todo falla, poner 0
                            inputCantidad.value = "0.00";
                            if (maxCantidad) maxCantidad.textContent = "0.00";
                        }
                    }
                }
                
                // Verificar que el valor se haya establecido correctamente
                console.log("Valor inicial establecido:", inputCantidad.value);
            }
            
            // Agregar filas a la tabla
            data.forEach(dep => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-gray-50';
                
                // Depósito
                const cell1 = document.createElement('td');
                cell1.className = 'px-4 py-3 whitespace-nowrap text-sm text-gray-800';
                cell1.textContent = dep.deposito_nombre;
                row.appendChild(cell1);
                
                // Función (origen o destino)
                const cell2 = document.createElement('td');
                cell2.className = 'px-4 py-3 whitespace-nowrap text-sm';
                
                // Verificar si este depósito es el origen o destino identificado previamente
                if (depositoOrigen && dep.id_deposito === depositoOrigen.id_deposito) {
                    // Si es el origen, mostramos el badge correspondiente
                    console.log("Marcando depósito como origen:", dep.id_deposito);
                    cell2.innerHTML = `
                        <div class="flex items-center">
                            <span class="badge badge-yellow mr-1">Origen</span>
                            <i class="fas fa-arrow-right text-gray-500 ml-1"></i>
                        </div>
                    `;
                } else if (depositoDestino && dep.id_deposito === depositoDestino.id_deposito) {
                    // Si es el destino, mostramos el badge correspondiente
                    console.log("Marcando depósito como destino:", dep.id_deposito);
                    cell2.innerHTML = `
                        <div class="flex items-center">
                            <i class="fas fa-arrow-right text-gray-500 mr-1"></i>
                            <span class="badge badge-blue">Destino</span>
                        </div>
                    `;
                } else {
                    // Si no es ni origen ni destino
                    cell2.textContent = '-';
                }
                row.appendChild(cell2);
                
                // Cantidad disponible
                const cell3 = document.createElement('td');
                cell3.className = 'px-4 py-3 whitespace-nowrap text-sm text-right';
                if (dep.cant_disponible < 0) {
                    cell3.className += ' text-red-600 font-medium';
                    cell3.innerHTML = `${dep.cant_disponible.toFixed(2)} <i class="fas fa-exclamation-circle text-red-500 ml-1" title="Disponible negativo"></i>`;
                } else {
                    cell3.className += ' text-gray-800';
                    cell3.textContent = dep.cant_disponible.toFixed(2);
                }
                row.appendChild(cell3);
                
                // Cantidad reservada
                const cell4 = document.createElement('td');
                cell4.className = 'px-4 py-3 whitespace-nowrap text-sm text-right';
                
                if (dep.cant_reservado != 0) {
                    // Si es un valor no cero, lo mostramos con formato
                    const esNegativo = dep.cant_reservado < 0;
                    
                    if (esNegativo) {
                        cell4.className += ' text-orange-600';
                        cell4.innerHTML = `${dep.cant_reservado.toFixed(2)} <i class="fas fa-exclamation-triangle text-orange-500 ml-1 text-xs" title="Valor negativo"></i>`;
                    } else {
                        // Si es el depósito destino, resaltamos en azul
                        if (depositoDestino && dep.id_deposito === depositoDestino.id_deposito) {
                            cell4.className += ' text-blue-700 font-medium';
                        } else {
                            cell4.className += ' text-gray-800';
                        }
                        cell4.textContent = dep.cant_reservado.toFixed(2);
                    }
                } else {
                    cell4.className += ' text-gray-400';
                    cell4.textContent = '-';
                }
                
                row.appendChild(cell4);
                
                // Cantidad preparada
                const cell5 = document.createElement('td');
                cell5.className = 'px-4 py-3 whitespace-nowrap text-sm text-right';
                
                if (dep.cant_preparado != 0) {
                    // Si es un valor no cero, lo mostramos con formato
                    const esNegativo = dep.cant_preparado < 0;
                    
                    if (esNegativo) {
                        cell5.className += ' text-orange-600';
                        cell5.innerHTML = `${dep.cant_preparado.toFixed(2)} <i class="fas fa-exclamation-triangle text-orange-500 ml-1 text-xs" title="Valor negativo"></i>`;
                    } else {
                        // Si es el depósito origen, resaltamos en ámbar
                        if (depositoOrigen && dep.id_deposito === depositoOrigen.id_deposito) {
                            cell5.className += ' text-amber-700 font-medium';
                        } else {
                            cell5.className += ' text-gray-800';
                        }
                        cell5.textContent = dep.cant_preparado.toFixed(2);
                    }
                } else {
                    cell5.className += ' text-gray-400';
                    cell5.textContent = '-';
                }
                
                row.appendChild(cell5);
                
                depositosTable.appendChild(row);
            });
        }
        
    } catch (error) {
        console.error("Error al obtener detalle:", error);
        showToast(`Error: ${error.message}`, 'error');
        closeDetailModal();
    }
}

/**
 * Cierra el modal de detalle
 */
function closeDetailModal() {
    const detailModal = document.getElementById('detail-modal');
    if (detailModal) {
        detailModal.classList.add('hidden');
    }
    
    currentMovimiento = null;
    detalleMovimiento = [];
    
    // Eliminar la explicación de confirmación si existe
    const explicacion = document.getElementById('explicacion-confirmacion');
    if (explicacion) {
        explicacion.remove();
    }
}

/**
 * Confirma un movimiento de stock
 */
async function confirmarMovimiento() {
    if (!currentMovimiento) {
        showToast('Error: No se ha seleccionado un movimiento para confirmar', 'error');
        return;
    }

    const { nroMovimiento, codigoArt } = currentMovimiento;
    
    const cantidadInput = document.getElementById('cantidad-confirmar');
    if (!cantidadInput) {
        showToast('Error: No se pudo encontrar el campo de cantidad', 'error');
        return;
    }
    
    const cantidadConfirmar = parseFloat(cantidadInput.value.trim());

    if (isNaN(cantidadConfirmar) || cantidadConfirmar <= 0) {
        showToast('Error: La cantidad a confirmar debe ser mayor que cero', 'error');
        return;
    }    // Definir depositoOrigen desde detalleMovimiento
    let depositoOrigen = null;
    
    // Verificar si estamos en el caso especial de depósitos 2 y 3
    const tieneDeposito2 = detalleMovimiento.some(d => d.id_deposito === 2);
    const tieneDeposito3 = detalleMovimiento.some(d => d.id_deposito === 3);
    
    if (tieneDeposito2 && tieneDeposito3) {
        // Caso especial: forzar depósito 3 como origen
        depositoOrigen = detalleMovimiento.find(d => d.id_deposito === 3);
        console.log('Caso especial: Forzando depósito 3 como origen');
    } else {
        // Caso general: usar la lógica existente
        depositoOrigen = detalleMovimiento.find(d => d.cant_preparado > 0);
    }
    
    if (!depositoOrigen) {
        showToast('Error: No se pudo identificar el depósito origen', 'error');
        return;
    }

    currentMovimiento.depositoOrigen = depositoOrigen.id_deposito;
    console.log('Depósito origen asignado a currentMovimiento:', currentMovimiento.depositoOrigen);

    const btnConfirmar = document.getElementById('btn-confirmar');
    if (!btnConfirmar) {
        showToast('Error: No se pudo encontrar el botón de confirmar', 'error');
        return;
    }    
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Procesando...';
    
    try {
        // Intentar realizar la petición al servidor
        console.log('Enviando solicitud de confirmación:', {
            nroMovimiento,
            codigoArt,
            depositoOrigen: currentMovimiento.depositoOrigen,
            cantidadConfirmar,
            detalleMovimiento: detalleMovimiento // Agregamos toda la información del detalle del movimiento
        });
        
        // Obtener todos los depósitos involucrados para confirmar el movimiento completo
        // Esta información es necesaria para que el backend cree los registros correctamente
          // Preparamos el cuerpo de la solicitud con la información completa
        const requestBody = {
            cantidades: {
                [currentMovimiento.depositoOrigen]: cantidadConfirmar,
            },
            completarMovimiento: true, // Indicamos que queremos completar el movimiento
            observacion: "Confirmacion movi " + nroMovimiento // Usamos la misma observación que en tu ejemplo
        };
          const response = await fetch(`/stock/movimientos/confirmar/${nroMovimiento}/${codigoArt}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        // Mostrar información detallada sobre la respuesta para depurar
        console.log('Respuesta del servidor:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries([...response.headers]),
        });

        if (!response.ok) {
            // Intentar obtener más información del error
            let errorMessage = `Error HTTP: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (parseError) {
                console.error('No se pudo parsear la respuesta de error:', parseError);
            }
            throw new Error(errorMessage);
        }
        
        // Procesar la respuesta exitosa
        const result = await response.json();
          // Actualizar el estado en la UI según la respuesta
        if (result.estado === 'parcial') {
            showToast('Confirmación parcial realizada correctamente.', 'success');
            // Verificar si el elemento existe antes de intentar modificarlo
            const estadoElement = document.querySelector(`#estado-${nroMovimiento}`);
            if (estadoElement) {
                estadoElement.innerHTML = '<span class="badge badge-amber">Parcialmente confirmado</span>';
            } else {
                console.warn(`Elemento #estado-${nroMovimiento} no encontrado`);
            }
        } else if (result.estado === 'completo') {
            showToast('Confirmación completa realizada correctamente.', 'success');
            // Verificar si el elemento existe antes de intentar modificarlo
            const estadoElement = document.querySelector(`#estado-${nroMovimiento}`);
            if (estadoElement) {
                estadoElement.innerHTML = '<span class="badge badge-green">Confirmado</span>';
            } else {
                console.warn(`Elemento #estado-${nroMovimiento} no encontrado`);
            }
        } else {
            // Si no tenemos un estado esperado, mostrar mensaje genérico
            showToast('Operación realizada, pero el estado es desconocido.', 'warning');
            console.warn('Estado desconocido en la respuesta:', result);
        }
        
    // Mostrar el resumen en el modal de éxito
        const successMessage = document.getElementById('success-message');
        if (successMessage) {            successMessage.innerHTML = `                <div class="text-center">
                    <i class="fas fa-check-circle text-green-500 text-4xl mb-3"></i>
                    <h3 class="text-xl font-semibold mb-2">Movimiento confirmado correctamente</h3>
                    <div class="bg-gray-50 p-4 rounded-lg my-3">
                        <div class="grid grid-cols-2 gap-2 text-sm">
                            <div class="text-gray-500">Nro. Movimiento:</div>
                            <div class="font-medium">${nroMovimiento}</div>
                            
                            <div class="text-gray-500">Código Artículo:</div>
                            <div class="font-medium">${codigoArt}</div>
                            
                            <div class="text-gray-500">Cantidad confirmada:</div>
                            <div class="font-medium">${cantidadConfirmar}</div>
                            
                            <div class="text-gray-500">Estado:</div>
                            <div class="font-medium">${result.estado === 'parcial' ? 'Parcial' : 'Completo'}</div>
                        </div>
                    </div>
                    
                    <div class="bg-blue-50 p-4 rounded-lg my-3 text-left">
                        <h4 class="font-semibold mb-2 text-blue-700">Detalle del Movimiento:</h4>
                        <div class="grid grid-cols-1 gap-3">                            <div class="border-b pb-2">
                                <p class="text-gray-600 font-semibold">Depósito Origen (${result.origen.id_deposito}):</p>
                                <div class="grid grid-cols-2 gap-1 text-sm ml-3 mt-1">
                                    <div class="text-gray-500">Disp. Anterior:</div>
                                    <div class="font-medium">${result.origen.cant_disponible_anterior.toFixed(2)}</div>
                                    <div class="text-gray-500">Mercadería Enviada:</div>
                                    <div class="font-medium text-red-600">-${result.origen.movimiento_stock.toFixed(2)}</div>
                                    <div class="text-gray-500">Disp. Actual:</div>
                                    <div class="font-medium">${result.origen.cant_disponible_nueva.toFixed(2)}</div>
                                    ${result.estado === 'parcial' ? `
                                    <div class="text-gray-500">Preparado Pendiente:</div>
                                    <div class="font-medium">${result.origen.cant_preparado_restante.toFixed(2)}</div>
                                    ` : ''}
                                </div>
                            </div>
                            <div>
                                <p class="text-gray-600 font-semibold">Depósito Destino (${result.destino.id_deposito}):</p>
                                <div class="grid grid-cols-2 gap-1 text-sm ml-3 mt-1">
                                    <div class="text-gray-500">Disp. Anterior:</div>
                                    <div class="font-medium">${result.destino.cant_disponible_anterior.toFixed(2)}</div>
                                    <div class="text-gray-500">Mercadería Recibida:</div>
                                    <div class="font-medium text-green-600">+${result.destino.movimiento_stock.toFixed(2)}</div>
                                    <div class="text-gray-500">Disp. Actual:</div>
                                    <div class="font-medium">${result.destino.cant_disponible_nueva.toFixed(2)}</div>
                                    ${result.estado === 'parcial' ? `
                                    <div class="text-gray-500">Reservado Pendiente:</div>
                                    <div class="font-medium">${result.destino.cant_reservado_restante.toFixed(2)}</div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <p class="text-green-600 mt-2">
                        ${result.estado === 'parcial' 
                            ? 'La confirmación parcial fue procesada correctamente.' 
                            : 'La confirmación completa fue procesada correctamente.'}
                    </p>
                </div>
            `;
            
            // Cerrar el modal de detalle y mostrar el modal de éxito
            const detailModal = document.getElementById('detail-modal');
            if (detailModal) {
                detailModal.classList.add('hidden');
            }
            
            const successModal = document.getElementById('success-modal');
            if (successModal) {
                successModal.classList.remove('hidden');
            }
        } else {
            console.error('Elemento success-message no encontrado');
            showToast('Movimiento confirmado correctamente pero no se pudo mostrar el resumen', 'success');
        }
        
        // Actualizar la tabla de movimientos pendientes con manejo de errores
        try {
            await fetchMovimientosPendientes();
        } catch (error) {
            console.error('Error al actualizar movimientos pendientes:', error);
        }
    } catch (error) {
        console.error('Error al confirmar movimiento:', error);
        showToast(`Error al confirmar movimiento: ${error.message}`, 'error');
    } finally {
        const btnConfirmar = document.getElementById('btn-confirmar');
        if (btnConfirmar) {
            btnConfirmar.disabled = false;
            btnConfirmar.innerHTML = 'Confirmar';
        }
    }
}

/**
 * Cierra el modal de éxito
 */
async function closeSuccessModal() {
    const successModal = document.getElementById('success-modal');
    if (successModal) {
        successModal.classList.add('hidden');
    }
    
    // Actualizar la tabla de movimientos pendientes
    try {
        await fetchMovimientosPendientes();
    } catch (err) {
        console.error('Error al actualizar movimientos pendientes después de cerrar modal:', err);
    }
}


/**
 * Cierra manualmente un movimiento de stock
 */
async function cerrarMovimientoManual() {
    if (!currentMovimiento) {
        showToast('Error: No se ha seleccionado un movimiento para cerrar', 'error');
        return;
    }

    const { nroMovimiento, codigoArt } = currentMovimiento;
    
    // Solicitar confirmación al usuario
    if (!confirm('¿Estás seguro de que deseas cerrar manualmente este movimiento? Esta acción marcará el movimiento como completado incluso si hay cantidades pendientes.')) {
        return;
    }

    const btnCerrarManual = document.getElementById('btn-cerrar-manual');
    if (!btnCerrarManual) {
        console.error('Botón cerrar-manual no encontrado');
        showToast('Error al cerrar movimiento: No se encontró el botón.', 'error');
        return;
    }    
    btnCerrarManual.disabled = true;
    btnCerrarManual.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Procesando...';
    
    try {
        // Registrar la solicitud para depuración
        console.log('Enviando solicitud para cerrar movimiento manualmente:', {
            nroMovimiento,
            codigoArt
        });
        
        const response = await fetch(`/stock/movimientos/cerrar/${nroMovimiento}/${codigoArt}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        // Registrar la respuesta para depuración
        console.log('Respuesta del servidor al cerrar movimiento:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries([...response.headers]),
        });

        if (!response.ok) {
            // Intentar obtener más información del error
            let errorMessage = `Error HTTP: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (parseError) {
                console.error('No se pudo parsear la respuesta de error:', parseError);
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        showToast('Movimiento cerrado manualmente con éxito.', 'success');
          // Mostrar el resumen en el modal de éxito
        const successMessage = document.getElementById('success-message');
        if (successMessage) {
            successMessage.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-check-double text-orange-500 text-4xl mb-3"></i>
                    <h3 class="text-xl font-semibold mb-2">Movimiento cerrado manualmente</h3>
                    <div class="bg-gray-50 p-4 rounded-lg my-3">
                        <div class="grid grid-cols-2 gap-2 text-sm">
                            <div class="text-gray-500">Nro. Movimiento:</div>
                            <div class="font-medium">${nroMovimiento}</div>
                            
                            <div class="text-gray-500">Código Artículo:</div>
                            <div class="font-medium">${codigoArt}</div>
                            
                            <div class="text-gray-500">Estado:</div>
                            <div class="font-medium">Cerrado manualmente</div>
                        </div>
                    </div>
                    <p class="text-orange-600 mt-2">
                        El movimiento ha sido cerrado manualmente. Cualquier cantidad pendiente ha sido ignorada.
                    </p>
                </div>
            `;
            
            // Cerrar el modal de detalle y mostrar el modal de éxito
            const detailModal = document.getElementById('detail-modal');
            if (detailModal) {
                detailModal.classList.add('hidden');
            }
            
            const successModal = document.getElementById('success-modal');
            if (successModal) {
                successModal.classList.remove('hidden');
            }
        } else {
            console.error('Elemento success-message no encontrado');
            showToast('Movimiento cerrado manualmente con éxito pero no se pudo mostrar el resumen', 'success');
        }
        
        // Actualizar la tabla de movimientos pendientes
        try {
            await fetchMovimientosPendientes();
        } catch (error) {
            console.error('Error al actualizar movimientos pendientes después de cerrar manualmente:', error);
        }
    } catch (error) {
        console.error('Error al cerrar movimiento manualmente:', error);
        showToast(`Error al cerrar movimiento: ${error.message}`, 'error');
    } finally {
        const btnCerrarManual = document.getElementById('btn-cerrar-manual');
        if (btnCerrarManual) {
            btnCerrarManual.disabled = false;
            btnCerrarManual.innerHTML = '<i class="fas fa-check-double mr-2"></i> Cerrar Manualmente';
        }
    }
}

/**
 * Muestra/oculta la descripción
 */
function toggleDescription() {
    const description = document.getElementById('description');
    if (description) {
        description.classList.toggle('hidden');
    } else {
        console.error('Elemento description no encontrado');
    }
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
    if (!container) {
        console.error('Elemento toast-container no encontrado');
        // Imprimir en la consola como alternativa
        console.log(`Toast (${type}): ${message}`);
        return;
    }
    
    container.appendChild(toast);
    
    // Eliminar después de 5 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

/**
 * Actualiza la visualización del flujo de movimiento entre depósitos
 */
function actualizarVisualizacionFlujo(depositoOrigen, depositoDestino, cantidadMaxima) {
    const contenedorFlujo = document.getElementById('flujo-movimiento');
    if (!contenedorFlujo) {
        console.error('Elemento flujo-movimiento no encontrado');
        return;
    }
    
    if (!depositoOrigen || !depositoDestino) {
        contenedorFlujo.innerHTML = `
            <div class="text-center text-sm text-gray-500 w-full">
                No se pudieron identificar claramente los depósitos origen y destino.
            </div>
        `;
        return;
    }
    
    // Formatear valores
    const cantidadFormatted = cantidadMaxima.toFixed(2);
    const dispOrigenFormatted = depositoOrigen.cant_disponible.toFixed(2);
    const dispDestinoFormatted = depositoDestino.cant_disponible.toFixed(2);
    const prepFormatted = depositoOrigen.cant_preparado != 0 ? Math.abs(depositoOrigen.cant_preparado).toFixed(2) : "0.00";
    const resvFormatted = depositoDestino.cant_reservado != 0 ? Math.abs(depositoDestino.cant_reservado).toFixed(2) : "0.00";
    
    // Determinar si mostrar etiquetas de alerta para valores negativos
    const dispOrigenNegativo = depositoOrigen.cant_disponible < 0;
    const dispDestinoNegativo = depositoDestino.cant_disponible < 0;
      // Generar el HTML para el flujo con mejor información visual
    contenedorFlujo.innerHTML = `
        <div class="deposito-box origen ${dispOrigenNegativo ? 'border-red-300 bg-red-50' : ''}">
            <div class="flex justify-between items-center mb-2">
                <h5 class="font-semibold text-sm text-gray-800 flex items-center">
                    <i class="fas fa-box text-amber-600 mr-1"></i>
                    ORIGEN: ${depositoOrigen.deposito_nombre}
                </h5>
                <span class="badge badge-amber">Preparación</span>
            </div>
            ${dispOrigenNegativo ? `
                <div class="bg-red-100 text-red-800 text-xs p-1 rounded mb-2 flex items-center">
                    <i class="fas fa-exclamation-triangle mr-1"></i>
                    Disponible negativo
                </div>
            ` : ''}
            <div class="flow-details">
                <div class="${dispOrigenNegativo ? 'text-red-700 font-medium' : ''}">
                    Disponible: ${dispOrigenFormatted}
                </div>
                <div>Preparado: ${prepFormatted} ${depositoOrigen.cant_preparado < 0 ? '<span class="text-xs text-orange-600">(valor negativo)</span>' : ''}</div>
            </div>
        </div>
        
        <div class="deposito-arrow">
            <div>
                <i class="fas fa-long-arrow-alt-right"></i>
                <div class="flow-quantity">${cantidadFormatted}</div>
                <div class="text-xs text-gray-500 text-center mt-1">Transferencia</div>
            </div>
        </div>
        
        <div class="deposito-box destino ${dispDestinoNegativo ? 'border-red-300 bg-red-50' : ''}">
            <div class="flex justify-between items-center mb-2">
                <h5 class="font-semibold text-sm text-gray-800 flex items-center">
                    <i class="fas fa-inbox text-blue-600 mr-1"></i>
                    DESTINO: ${depositoDestino.deposito_nombre}
                </h5>
                <span class="badge badge-blue">Reserva</span>
            </div>
            ${dispDestinoNegativo ? `
                <div class="bg-red-100 text-red-800 text-xs p-1 rounded mb-2 flex items-center">
                    <i class="fas fa-exclamation-triangle mr-1"></i>
                    Disponible negativo
                </div>
            ` : ''}
            <div class="flow-details">
                <div class="${dispDestinoNegativo ? 'text-red-700 font-medium' : ''}">
                    Disponible: ${dispDestinoFormatted}
                </div>
                <div>Reservado: ${resvFormatted} ${depositoDestino.cant_reservado < 0 ? '<span class="text-xs text-orange-600">(valor negativo)</span>' : ''}</div>
            </div>
        </div>
    `;
}

/**
 * Revierte la confirmación de un movimiento
 */
async function revertirConfirmacion(nroMovimiento, codigoArt) {
    if (!confirm(`¿Está seguro que desea revertir la confirmación del movimiento #${nroMovimiento}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/stock/movimientos/revertir-confirmacion/${nroMovimiento}/${codigoArt}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error al revertir la confirmación");
        }
        
        const result = await response.json();        
        showToast(`${result.mensaje}`, 'success');
        
        // Recargar los datos con el filtro actual
        const filtroConfirmados = document.getElementById('filtro-confirmados');
        const mostrarConfirmados = filtroConfirmados ? filtroConfirmados.checked : false;
        
        try {
            await fetchMovimientosPendientes(mostrarConfirmados);
        } catch (error) {
            console.error('Error al actualizar movimientos después de revertir:', error);
        }
        
    } catch (error) {
        console.error("Error:", error);
        showToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Cambia el filtro de movimientos confirmados
 */
function cambiarFiltroConfirmados() {
    const filtroElement = document.getElementById('filtro-confirmados');
    if (!filtroElement) {
        console.error('Elemento filtro-confirmados no encontrado');
        return;
    }
    
    const mostrarConfirmados = filtroElement.checked;
    
    // Actualizar título según el filtro
    const titleElement = document.querySelector('.bg-gray-50 h2');
    if (titleElement) {
        titleElement.innerHTML = mostrarConfirmados
            ? '<i class="fas fa-exchange-alt text-blue-600 mr-2"></i> Todos los Movimientos'
            : '<i class="fas fa-exchange-alt text-blue-600 mr-2"></i> Movimientos Pendientes';
    }
    
    try {
        fetchMovimientosPendientes(mostrarConfirmados);
    } catch (error) {
        console.error('Error al cambiar el filtro de confirmados:', error);
        showToast('Error al filtrar movimientos. Intente nuevamente.', 'error');
    }
}

/**
 * Obtiene y muestra el historial de confirmaciones parciales para un movimiento
 */
async function verHistorialConfirmaciones(nroMovimiento, codigoArt) {
    try {
        const response = await fetch(`/stock/movimientos/historial-confirmaciones/${nroMovimiento}/${codigoArt}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al obtener historial de confirmaciones');
        }
        
        const historial = await response.json();
        
        // Crear o actualizar modal para mostrar historial
        let historialModal = document.getElementById('historial-modal');
        
        if (!historialModal) {
            // Crear el modal si no existe
            historialModal = document.createElement('div');
            historialModal.id = 'historial-modal';
            historialModal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 modal-overlay hidden';
            
            historialModal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 fade-in">
                    <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                        <h3 class="text-lg font-semibold text-gray-800" id="historial-title">
                            Historial de Confirmaciones
                        </h3>
                        <button type="button" class="text-gray-400 hover:text-gray-600" onclick="closeHistorialModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="p-6" id="historial-content">
                        <!-- Aquí se mostrará el historial -->
                    </div>
                    <div class="px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="button" class="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600" onclick="closeHistorialModal()">
                            Cerrar
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(historialModal);
        }
        
        // Actualizar título
        const historialTitle = document.getElementById('historial-title');
        if (historialTitle) {
            historialTitle.textContent = `Historial de confirmaciones - Movimiento #${nroMovimiento}`;
        }
        
        // Actualizar contenido
        const historialContent = document.getElementById('historial-content');
        if (!historialContent) return;
        
        if (historial.length === 0) {
            historialContent.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-info-circle text-blue-500 text-4xl mb-4"></i>
                    <p class="text-gray-600">No hay historial de confirmaciones parciales para este movimiento.</p>
                </div>
            `;
        } else {
            // Crear tabla de historial
            let tableHTML = `
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white">
                        <thead>
                            <tr class="bg-gray-100 text-gray-600 uppercase text-sm leading-normal">
                                <th class="py-3 px-6 text-left">Fecha</th>
                                <th class="py-3 px-6 text-center">Cantidad Confirmada</th>
                                <th class="py-3 px-6 text-center">Depósito Origen</th>
                                <th class="py-3 px-6 text-center">Depósito Destino</th>
                                <th class="py-3 px-6 text-left">Observación</th>
                            </tr>
                        </thead>
                        <tbody class="text-gray-600 text-sm">
            `;
            
            // Agregar filas para cada confirmación
            historial.forEach(confirm => {
                tableHTML += `
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-3 px-6 text-left whitespace-nowrap">
                            ${confirm.fecha_registro}
                        </td>
                        <td class="py-3 px-6 text-center">
                            <span class="bg-green-100 text-green-800 py-1 px-3 rounded-full text-xs">
                                ${confirm.cantidad_confirmada.toFixed(2)}
                            </span>
                        </td>
                        <td class="py-3 px-6 text-center">
                            ${confirm.deposito_origen.id_deposito}
                        </td>
                        <td class="py-3 px-6 text-center">
                            ${confirm.deposito_destino.id_deposito}
                        </td>
                        <td class="py-3 px-6 text-left">
                            ${confirm.observacion || '-'}
                        </td>
                    </tr>
                `;
            });
            
            tableHTML += `
                        </tbody>
                    </table>
                </div>
                <div class="mt-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded-md">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-info-circle text-blue-500"></i>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-blue-700">
                                Este movimiento ha sido confirmado en ${historial.length} ${historial.length === 1 ? 'operación' : 'operaciones'} separadas.
                            </p>
                        </div>
                    </div>
                </div>
            `;
            
            historialContent.innerHTML = tableHTML;
        }
        
        // Mostrar el modal
        historialModal.classList.remove('hidden');
        
    } catch (error) {
        console.error('Error al cargar historial de confirmaciones:', error);
        showToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Cierra el modal de historial de confirmaciones
 */
function closeHistorialModal() {
    const historialModal = document.getElementById('historial-modal');
    if (historialModal) {
        historialModal.classList.add('hidden');
    }
}
