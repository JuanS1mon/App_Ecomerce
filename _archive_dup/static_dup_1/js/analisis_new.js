/**
 * SQL App Studio - Analizador de Datos
 * v1.2.5 - Marzo 2025
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes de la interfaz
    initProfileMenu();
    setDefaultDate();
    initEventListeners();
});

/**
 * Inicializa el menú desplegable del perfil
 */
function initProfileMenu() {
    const perfilButton = document.getElementById('perfil');
    const menuPerfil = document.getElementById('menu-perfil');
    
    if (perfilButton && menuPerfil) {
        perfilButton.addEventListener('click', function() {
            menuPerfil.classList.toggle('hidden');
        });
        
        // Cerrar menú al hacer clic fuera
        document.addEventListener('click', function(event) {
            if (!perfilButton.contains(event.target) && !menuPerfil.contains(event.target)) {
                menuPerfil.classList.add('hidden');
            }
        });
    }
}

/**
 * Establece la fecha actual por defecto en el campo end_date
 */
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    const endDateField = document.getElementById('end_date');
    if (endDateField) {
        endDateField.value = today;
        
        // Si existe un campo de fecha inicial, establecerlo a un mes antes
        const startDateField = document.getElementById('start_date');
        if (startDateField) {
            const oneMonthAgo = new Date();
            oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
            startDateField.value = oneMonthAgo.toISOString().split('T')[0];
        }
    }
}

/**
 * Inicializa todos los event listeners principales
 */
function initEventListeners() {
    // Listener para la selección de tabla
    document.getElementById("table-select").addEventListener("change", handleTableSelection);
    
    // Listener para el botón de redirección de tabla
    const goToTableBtn = document.getElementById("go-to-table");
    if (goToTableBtn) {
        goToTableBtn.addEventListener("click", navigateToTable);
    }
    
    // Listeners para los botones de análisis
    document.getElementById("show-kpis").addEventListener("click", showKPIAnalysis);
    document.getElementById("show-graph").addEventListener("click", showGraphAnalysis);
    document.getElementById("show-table").addEventListener("click", showTableData);
    document.getElementById("show-clustering").addEventListener("click", function() {
        alert("Funcionalidad de clustering en desarrollo");
    });
    document.getElementById("show-classification").addEventListener("click", function() {
        alert("Funcionalidad de clasificación en desarrollo");
    });
    document.getElementById("show-regression").addEventListener("click", function() {
        alert("Funcionalidad de regresión en desarrollo");
    });
}

/**
 * Maneja la descripción toggle
 */
function toggleDescription() {
    const description = document.getElementById('description');
    const toggleButton = document.getElementById('toggleButton');
    if (description.classList.contains('hidden')) {
        description.classList.remove('hidden');
        toggleButton.innerHTML = '<i class="fas fa-times-circle"></i>';
    } else {
        description.classList.add('hidden');
        toggleButton.innerHTML = '<i class="fas fa-info-circle"></i>';
    }
}

/**
 * Función para mostrar/ocultar la sección de selección
 */
function toggleSection() {
    const section = document.getElementById('selection-section');
    const icon = document.getElementById('toggle-icon');
    section.classList.toggle('hidden');
    icon.classList.toggle('fa-minus');
    icon.classList.toggle('fa-plus');
}

/**
 * Maneja la selección de tabla y carga columnas
 */
function handleTableSelection() {
    const tableName = this.value;
    const goToTableBtn = document.getElementById("go-to-table");
    
    if (goToTableBtn) {
        goToTableBtn.disabled = !tableName;
    }
    
    if (!tableName) return;

    // Cargar columnas para la tabla seleccionada
    fetchTableColumns(tableName).then(columnsData => {
        // Poblar selects con las columnas obtenidas
        populateColumnSelects(columnsData);
        
        // Actualizar filtros existentes
        updateExistingFilters(columnsData);
    });
}

/**
 * Obtiene las columnas de una tabla
 * @param {string} tableName - Nombre de la tabla
 * @returns {Promise} - Promesa con los datos de columnas
 */
async function fetchTableColumns(tableName) {
    try {
        const response = await fetch(`/analisis/columnas`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ table_name: tableName })
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("Error al obtener columnas:", error);
        showNotification("Error al obtener columnas: " + error.message, "error");
        return { columns: [] };
    }
}

/**
 * Rellena los selectores de columnas con los datos
 * @param {Object} columnsData - Datos de columnas recibidos
 */
function populateColumnSelects(columnsData) {
    // Poblar selector de columnas numéricas
    const columnSelect = document.getElementById("column-select");
    columnSelect.innerHTML = '<option value="" disabled selected>Selecciona una columna...</option>';
    columnsData.columns
        .filter(column => {
            const upperType = column.type.toUpperCase();
            return ['INTEGER', 'BIGINT', 'FLOAT', 'DECIMAL', 'NUMERIC', 'REAL', 'SMALLINT'].some(type => 
                upperType.includes(type));
        })
        .forEach(column => {
            columnSelect.innerHTML += `<option value="${column.name}">${column.name}</option>`;
        });

    // Poblar selector de campos de fecha
    const dateFieldSelect = document.getElementById("date_field");
    dateFieldSelect.innerHTML = '<option value="" disabled selected>Selecciona un campo de fecha...</option>';
    columnsData.columns
        .filter(column => {
            const upperType = column.type.toUpperCase();
            return ['DATE', 'DATETIME', 'TIMESTAMP', 'SMALLDATETIME'].some(type => 
                upperType.includes(type));
        })
        .forEach(column => {
            dateFieldSelect.innerHTML += `<option value="${column.name}">${column.name}</option>`;
        });

    // Actualizar selectores de campos adicionales existentes
    document.querySelectorAll('select[name="additional_fields[]"]').forEach(select => {
        const currentValue = select.value; // Guardar valor actual
        select.innerHTML = '<option value="" disabled selected>Selecciona un campo...</option>';
        columnsData.columns.forEach(column => {
            const option = document.createElement('option');
            option.value = column.name;
            option.textContent = column.name;
            if (column.name === currentValue) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    });
}

/**
 * Redirecciona a la página de la tabla seleccionada
 */
function navigateToTable() {
    const selectedTable = document.getElementById("table-select").value;
    if (selectedTable) {
        window.location.href = `/${selectedTable}/pagina`;
    }
}

/**
 * Agrega un nuevo campo adicional
 */
function addField() {
    const container = document.getElementById('additional-fields');
    const fieldIndex = Date.now();
    
    const fieldEl = document.createElement('div');
    fieldEl.className = 'bg-white p-3 rounded-lg shadow-sm';
    fieldEl.innerHTML = `
        <div class="flex items-center space-x-2">
            <select name="additional_fields[]" class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500">
                <option value="" disabled selected>Selecciona un campo...</option>
            </select>
            <button type="button" onclick="removeField(this)" class="bg-red-500 text-white p-2 rounded-md hover:bg-red-600 transition-colors">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    container.appendChild(fieldEl);

    // Llenar el select con las columnas disponibles
    const tableName = document.getElementById("table-select").value;
    if (tableName) {
        fetchTableColumns(tableName).then(columnsData => {
            const select = fieldEl.querySelector('select[name="additional_fields[]"]');
            select.innerHTML = '<option value="" disabled selected>Selecciona un campo...</option>';
            columnsData.columns.forEach(column => {
                select.innerHTML += `<option value="${column.name}">${column.name}</option>`;
            });
        });
    }
}

/**
 * Elimina un campo adicional
 * @param {HTMLElement} button - El botón que disparó el evento
 */
function removeField(button) {
    const field = button.closest('div.bg-white');
    field.remove();
}

/**
 * Agrega un filtro personalizado
 */
function addCustomFilter() {
    const container = document.getElementById('custom-filters');
    const filterIndex = container.children.length;
    
    const filter = document.createElement('div');
    filter.className = 'bg-white p-4 rounded-lg shadow-sm';
    filter.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Campo</label>
                <select name="filter_field[]" class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500">
                    <option value="" disabled selected>Selecciona un campo...</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Operador</label>
                <select name="filter_operator[]" class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500">
                    <option value="=" selected>=</option>
                    <option value="!=">≠</option>
                    <option value=">">&gt;</option>
                    <option value=">=">&ge;</option>
                    <option value="<">&lt;</option>
                    <option value="<=">&le;</option>
                    <option value="LIKE">Contiene</option>
                    <option value="NOT LIKE">No contiene</option>
                    <option value="IS NULL">Es nulo</option>
                    <option value="IS NOT NULL">No es nulo</option>
                </select>
            </div>
            <div id="value-container-${filterIndex}">
                <label class="block text-sm font-medium text-gray-700 mb-1">Valor</label>
                <div class="flex items-center">
                    <input type="text" name="filter_value[]" class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500">
                    <button type="button" onclick="removeFilter(this)" class="ml-2 bg-red-500 text-white p-2 rounded-md hover:bg-red-600 transition-colors">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(filter);

    // Actualizar el select con las columnas disponibles
    const tableName = document.getElementById("table-select").value;
    if (tableName) {
        fetchTableColumns(tableName).then(columnsData => {
            const filterField = filter.querySelector('select[name="filter_field[]"]');
            const operatorField = filter.querySelector('select[name="filter_operator[]"]');
            
            filterField.innerHTML = '<option value="" disabled selected>Selecciona un campo...</option>';
            columnsData.columns.forEach(column => {
                filterField.innerHTML += `<option value="${column.name}" data-type="${column.type}">${column.name}</option>`;
            });
            
            // Manejar cambio de operador para mostrar/ocultar campo de valor
            operatorField.addEventListener('change', function() {
                const valueContainer = document.getElementById(`value-container-${filterIndex}`);
                const needsValue = !['IS NULL', 'IS NOT NULL'].includes(this.value);
                valueContainer.style.display = needsValue ? 'block' : 'none';
            });
        });
    }
}

/**
 * Elimina un filtro personalizado
 * @param {HTMLElement} button - El botón que disparó el evento
 */
function removeFilter(button) {
    const filter = button.closest('div.bg-white');
    filter.remove();
}

/**
 * Actualiza los filtros existentes cuando se cambia la tabla
 * @param {Object} columnsData - Datos de columnas
 */
function updateExistingFilters(columnsData) {
    const filterFields = document.querySelectorAll('select[name="filter_field[]"]');
    filterFields.forEach(select => {
        const currentValue = select.value; // Guardar valor actual
        select.innerHTML = '<option value="" disabled selected>Selecciona un campo...</option>';
        columnsData.columns.forEach(column => {
            const option = document.createElement('option');
            option.value = column.name;
            option.setAttribute('data-type', column.type);
            option.textContent = column.name;
            if (column.name === currentValue) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    });
}

/**
 * Recopila los filtros personalizados
 * @returns {Array} - Array de objetos con los filtros
 */
function getCustomFilters() {
    const filters = [];
    const fields = document.querySelectorAll('select[name="filter_field[]"]');
    const operators = document.querySelectorAll('select[name="filter_operator[]"]');
    const values = document.querySelectorAll('input[name="filter_value[]"]');
    
    for (let i = 0; i < fields.length; i++) {
        if (fields[i].value) {
            const needsValue = !['IS NULL', 'IS NOT NULL'].includes(operators[i].value);
            filters.push({
                field: fields[i].value,
                operator: operators[i].value,
                value: needsValue ? values[i].value : null
            });
        }
    }
    
    return filters;
}

/**
 * Muestra una notificación en pantalla
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de notificación (success, error, warning, info)
 */
function showNotification(message, type = "info") {
    // Colores según el tipo
    const colors = {
        success: "bg-green-100 border-green-400 text-green-700",
        error: "bg-red-100 border-red-400 text-red-700",
        warning: "bg-yellow-100 border-yellow-400 text-yellow-700",
        info: "bg-blue-100 border-blue-400 text-blue-700"
    };
    
    // Iconos según el tipo
    const icons = {
        success: '<i class="fas fa-check-circle"></i>',
        error: '<i class="fas fa-exclamation-circle"></i>',
        warning: '<i class="fas fa-exclamation-triangle"></i>',
        info: '<i class="fas fa-info-circle"></i>'
    };
    
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 z-50 p-4 border-l-4 rounded shadow-lg ${colors[type] || colors.info}`;
    notification.innerHTML = `
        <div class="flex items-center">
            <div class="mr-3">
                ${icons[type] || icons.info}
            </div>
            <div>${message}</div>
            <button class="ml-6 text-sm" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.add('opacity-0');
            notification.style.transition = 'opacity 0.5s ease';
            setTimeout(() => notification.remove(), 500);
        }
    }, 5000);
}

/**
 * Formatea las fechas a un formato SQL Server compatible
 * @param {string} dateStr - Fecha en formato ISO
 * @returns {string} - Fecha formateada
 */
function formatDateForSqlServer(dateStr) {
    if (!dateStr) return null;
    
    try {
        // Convertir a objeto Date
        const date = new Date(dateStr);
        
        // Formato YYYYMMDD
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        return `${year}${month}${day}`;
    } catch (error) {
        console.error("Error al formatear fecha:", error);
        return dateStr; // Devolver la fecha original si hay error
    }
}

/**
 * Muestra el análisis de KPIs
 */
async function showKPIAnalysis() {
    try {
        // Validar entrada
        const formData = getFormData();
        if (!formData.tableName) {
            showNotification("Por favor selecciona una tabla", "warning");
            return;
        }
        
        // Mostrar indicador de carga
        document.getElementById("loading-indicator").classList.remove("hidden");
        
        // Formatear fechas para SQL Server si existen
        const startDate = formData.startDate ? formatDateForSqlServer(formData.startDate) : null;
        const endDate = formData.endDate ? formatDateForSqlServer(formData.endDate) : null;
        
        // Llamada a la API
        const response = await fetch("/analisis/analizar_kpis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                table_name: formData.tableName,
                column_name: formData.columnName,
                date_field: formData.dateField,
                start_date: formData.startDate,
                end_date: formData.endDate,
                additional_field: formData.additionalFields,
                custom_filters: getCustomFilters()
            })
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
    
        // Actualizar KPIs básicos
        updateBasicKPIs(data);

        // Actualizar el detalle de categorías
        updateCategoriesDetail(data);

        // Actualizar clusters temporales
        updateTemporalClusters(data);

        // Mostrar la sección de KPIs y ocultar las demás
        toggleSections("kpi-section");
        
        showNotification("Análisis KPI completado", "success");

    } catch (err) {
        console.error("Error al analizar KPIs:", err);
        showNotification("Error al analizar los KPIs: " + err.message, "error");
    } finally {
        document.getElementById("loading-indicator").classList.add("hidden");
    }
}

/**
 * Actualiza los KPIs básicos con los datos recibidos
 * @param {Object} data - Datos de KPIs 
 */
function updateBasicKPIs(data) {
    document.getElementById("total-records").textContent = data.total_registros ?? "-";
    document.getElementById("categories").textContent = data.categorias ?? "-";
    document.getElementById("last-date").textContent = data.last_date ?? "-";
    document.getElementById("first-date").textContent = data.first_date ?? "-";
    document.getElementById("max-value").textContent = data.max_value ?? "-";
    document.getElementById("min-value").textContent = data.min_value ?? "-";
}

/**
 * Actualiza el detalle de categorías
 * @param {Object} data - Datos de análisis
 */
function updateCategoriesDetail(data) {
    const categoriesDetailEl = document.getElementById("categories-detail");
    categoriesDetailEl.innerHTML = "";

    if (data.analisis_campos) {
        const limitValues = parseInt(document.getElementById('limit-values').value) || 10;
        
        Object.entries(data.analisis_campos)
            .filter(([_, analisis]) => analisis.campo) // Verificar que el campo existe
            .forEach(([tipo, analisis], index) => {
                // Crear ID único para este campo
                const fieldId = `field-grid-${index}-${Date.now()}`;
                
                // Crear contenedor para cada campo
                const fieldContainer = document.createElement("div");
                fieldContainer.className = "mb-4 bg-gray-50 p-3 rounded-lg";

                // Crear encabezado con botón de copiar
                const header = document.createElement("div");
                header.className = "font-bold text-lg text-indigo-600 mb-2 border-b pb-2 flex justify-between items-center";
                header.innerHTML = `
                    <span>${analisis.campo}</span>
                    <span class="copy-button" data-copy="${fieldId}" onclick="copiarContenido('${fieldId}', '${analisis.campo}')">
                        <i class="fas fa-copy"></i>
                    </span>
                `;
                fieldContainer.appendChild(header);

                // Grid para datos
                const distributionGrid = document.createElement("div");
                distributionGrid.className = "grid grid-cols-1 md:grid-cols-2 gap-2";
                distributionGrid.id = fieldId;

                // Agregar contenido si hay distribución
                if (analisis.distribucion && Object.keys(analisis.distribucion).length > 0) {
                    Object.entries(analisis.distribucion)
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, limitValues)
                        .forEach(([valor, cantidad]) => {
                            const item = document.createElement("div");
                            item.className = "flex justify-between items-center p-2 bg-white rounded shadow-sm";
                            item.innerHTML = `
                                <span class="font-medium text-gray-700">${valor || "Sin valor"}</span>
                                <span class="text-indigo-600 font-semibold">${cantidad}</span>
                            `;
                            distributionGrid.appendChild(item);
                        });
                    
                    // Información de resumen
                    const totalValues = Object.values(analisis.distribucion).reduce((a, b) => a + b, 0);
                    const uniqueValues = Object.keys(analisis.distribucion).length;
                    const totalValuesShown = Math.min(limitValues, uniqueValues);
                    
                    const summary = document.createElement("div");
                    summary.className = "mt-3 text-sm text-gray-600 flex flex-col border-t pt-2";
                    summary.innerHTML = `
                        <div class="flex justify-between">
                            <span>Valores únicos: ${uniqueValues}</span>
                            <span>Total registros: ${totalValues}</span>
                        </div>
                        <div class="text-xs text-gray-500 mt-1">
                            Mostrando ${totalValuesShown} de ${uniqueValues} valores únicos
                        </div>
                    `;
                    
                    fieldContainer.appendChild(distributionGrid);
                    fieldContainer.appendChild(summary);
                } else {
                    distributionGrid.innerHTML = `
                        <div class="col-span-2 p-3 text-center text-gray-500">
                            No hay datos de distribución disponibles para este campo
                        </div>
                    `;
                    fieldContainer.appendChild(distributionGrid);
                }

                categoriesDetailEl.appendChild(fieldContainer);
            });
    } else {
        categoriesDetailEl.innerHTML = `
            <div class="text-gray-500 text-center p-4">
                No hay datos de categorías para analizar
            </div>`;
    }
}

/**
 * Actualiza los clusters temporales
 * @param {Object} data - Datos de análisis
 */
function updateTemporalClusters(data) {
    const clusterResults = document.getElementById("cluster-results");
    clusterResults.innerHTML = "";

    if (data.clusters && data.clusters.temporal) {
        const temporal = data.clusters.temporal;
        
        // Función helper para crear una sección de cluster con botón de copia
        const createClusterSection = (title, data, icon) => {
            const clusterId = `cluster-${title.replace(/\s+/g, '-').toLowerCase()}-${Date.now()}`;
            const section = document.createElement("div");
            section.className = "bg-gray-50 p-3 rounded-lg";
            
            const header = document.createElement("div");
            header.className = "font-bold text-sm text-indigo-600 mb-2 border-b pb-2 flex justify-between items-center";
            header.innerHTML = `
                <div><i class="${icon} mr-2"></i>${title}</div>
                <span class="copy-button" data-copy="${clusterId}" onclick="copiarContenido('${clusterId}', '${title}')">
                    <i class="fas fa-copy"></i>
                </span>`;
            section.appendChild(header);

            const list = document.createElement("div");
            list.className = "space-y-1";
            list.id = clusterId;
            
            if (Object.keys(data).length > 0) {
                Object.entries(data)
                    .sort((a, b) => b[1] - a[1])
                    .forEach(([key, value]) => {
                        const item = document.createElement("div");
                        item.className = "flex justify-between items-center py-1";
                        item.innerHTML = `
                            <span class="text-sm font-medium text-gray-600">${key}</span>
                            <span class="text-sm text-indigo-600 font-semibold">${value}</span>
                        `;
                        list.appendChild(item);
                    });
            } else {
                list.innerHTML = `<div class="text-gray-500 text-center py-2">No hay datos disponibles</div>`;
            }
            
            section.appendChild(list);
            return section;
        };

        // Crear secciones para cada tipo de análisis temporal
        if (temporal.por_año) {
            clusterResults.appendChild(
                createClusterSection("Por Año", temporal.por_año, "fas fa-calendar-alt")
            );
        }

        if (temporal.por_mes) {
            const mesesNombres = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            };
            const dataPorMes = Object.fromEntries(
                Object.entries(temporal.por_mes).map(([mes, valor]) => [mesesNombres[mes] || mes, valor])
            );
            clusterResults.appendChild(
                createClusterSection("Por Mes", dataPorMes, "fas fa-calendar-day")
            );
        }

        if (temporal.por_dia_semana) {
            clusterResults.appendChild(
                createClusterSection("Por Día de Semana", temporal.por_dia_semana, "fas fa-calendar-week")
            );
        }

        if (temporal.por_trimestre) {
            const dataTrimestrales = Object.fromEntries(
                Object.entries(temporal.por_trimestre).map(([trim, valor]) => [`Q${trim}`, valor])
            );
            clusterResults.appendChild(
                createClusterSection("Por Trimestre", dataTrimestrales, "fas fa-chart-pie")
            );
        }

        if (temporal.tendencia_12_meses) {
            clusterResults.appendChild(
                createClusterSection("Últimos 12 Meses", temporal.tendencia_12_meses, "fas fa-chart-line")
            );
        }
    } else {
        clusterResults.innerHTML = `
            <div class="text-gray-500 text-center p-4 col-span-2">
                No hay datos temporales disponibles para analizar
            </div>`;
    }
}

/**
 * Muestra el análisis gráfico
 */
async function showGraphAnalysis() {
    try {
        // Validar entrada
        const formData = getFormData();
        if (!formData.tableName || !formData.dateField) {
            showNotification("Por favor, selecciona una tabla y un campo de fecha", "warning");
            return;
        }

        // Mostrar indicador de carga
        document.getElementById("loading-indicator").classList.remove("hidden");

        // Llamada a la API con formato de fecha corregido para SQL Server
        const response = await fetch("/analisis/analizar_grafico", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                table_name: formData.tableName,
                column_name: formData.columnName,
                date_field: formData.dateField,
                // Usar formato SQL Server compatible
                start_date: formData.startDate ? formatDateForSqlServer(formData.startDate) : null,
                end_date: formData.endDate ? formatDateForSqlServer(formData.endDate) : null,
                additional_field: formData.additionalFields,
                custom_filters: getCustomFilters()
            })
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        if (data.status === "success") {
            const container = document.getElementById("graficos-container");
            container.innerHTML = '';
            
            // Mostrar sección de gráficos y ocultar las demás
            toggleSections("graph-section");
            
            // Verificar si hay datos de series temporales
            if (data.data && data.data.series_temporales && Object.keys(data.data.series_temporales).length > 0) {
                // Crear gráficos de manera asíncrona
                await Promise.all(Object.entries(data.data.series_temporales).map(async ([campo, datos]) => {
                    await createChart(campo, datos, container);
                }));
                
                showNotification("Gráficos generados correctamente", "success");
            } else {
                container.innerHTML = `
                    <div class="col-span-2 bg-yellow-50 border border-yellow-200 p-4 rounded-lg text-yellow-700">
                        <h3 class="font-bold mb-2">No hay datos disponibles para graficar</h3>
                        <p>Prueba ajustando los filtros o seleccionando otro rango de fechas.</p>
                    </div>`;
                showNotification("No hay datos para mostrar en los gráficos", "warning");
            }
        } else {
            throw new Error(data.message || "Error desconocido al generar gráficos");
        }
    } catch (error) {
        console.error("Error al generar gráficos:", error);
        showNotification("Error al generar los gráficos: " + error.message, "error");
        
        // Mostrar mensaje en la sección de gráficos para más claridad
        const container = document.getElementById("graficos-container");
        container.innerHTML = `
            <div class="col-span-2 bg-red-50 border border-red-200 p-4 rounded-lg text-red-700">
                <h3 class="font-bold mb-2">Error al generar gráficos</h3>
                <p>${error.message}</p>
                <p class="mt-2 text-sm">
                    Sugerencias:
                    <ul class="list-disc ml-5 mt-1">
                        <li>Comprueba el formato de las fechas</li>
                        <li>Verifica que el campo fecha contiene datos válidos</li>
                        <li>Asegúrate de que existen datos para el período seleccionado</li>
                    </ul>
                </p>
            </div>`;
        
        // Mostrar la sección de gráficos para que el usuario vea el error
        toggleSections("graph-section");
    } finally {
        document.getElementById("loading-indicator").classList.add("hidden");
    }
}

/**
 * Crea un gráfico dinámico
 * @param {string} campo - Nombre del campo para el gráfico
 * @param {Object} datos - Datos para el gráfico
 * @param {HTMLElement} container - Contenedor donde insertar el gráfico
 */
async function createChart(campo, datos, container) {
    const canvasId = `chart-${campo.replace(/\s+/g, '-')}-${Date.now()}`;
    
    // Crear estructura del contenedor
    const chartStructure = `
        <div class="bg-white p-4 rounded shadow-md">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold text-gray-700">${campo}</h3>
                <select class="chart-type-selector ml-2 p-2 border rounded-md text-sm focus:ring-indigo-500 focus:border-indigo-500">
                    <option value="line">Línea</option>
                    <option value="bar">Barras</option>
                    <option value="pie">Circular</option>
                    <option value="doughnut">Dona</option>
                    <option value="radar">Radar</option>
                </select>
            </div>
            <div class="relative" style="height: 400px;">
                <canvas id="${canvasId}"></canvas>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', chartStructure);

    const canvas = document.getElementById(canvasId);
    const chartTypeSelector = canvas.closest('.bg-white').querySelector('.chart-type-selector');

    const updateChart = (chartType) => {
        if (canvas.chart) {
            canvas.chart.destroy();
        }

        const ctx = canvas.getContext('2d');
        const isCircularChart = chartType === 'pie' || chartType === 'doughnut';
        
        let chartConfig = {
            type: chartType,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${datos.tipo === "categorico" ? 'Distribución' : 'Análisis'} - ${campo}`
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: isCircularChart ? 'right' : 'top',
                        align: 'center'
                    }
                }
            }
        };

        if (datos.tipo === "categorico") {
            const totalsPorCategoria = Object.fromEntries(
                Object.entries(datos.valores).map(([categoria, valores]) => [
                    categoria,
                    Array.isArray(valores) ? valores.reduce((a, b) => a + b, 0) : valores
                ])
            );

            if (isCircularChart) {
                chartConfig.data = {
                    labels: Object.keys(totalsPorCategoria),
                    datasets: [{
                        data: Object.values(totalsPorCategoria),
                        backgroundColor: Object.keys(totalsPorCategoria)
                            .map((_, i) => getColor(i, 0.8))
                    }]
                };

                chartConfig.options.plugins.tooltip.callbacks = {
                    label: (context) => {
                        const value = context.raw;
                        const total = Object.values(totalsPorCategoria)
                            .reduce((a, b) => a + b, 0);
                        const percentage = ((value * 100) / total).toFixed(1);
                        return `${context.label}: ${value} (${percentage}%)`;
                    }
                };
            } else {
                // Asegurarnos de que tenemos datos válidos
                if (!datos.fechas || !datos.valores || Object.keys(datos.valores).length === 0) {
                    console.error("Datos insuficientes para crear gráfico:", datos);
                    return;
                }

                chartConfig.data = {
                    labels: datos.fechas,
                    datasets: Object.entries(datos.valores).map(([categoria, valores], index) => ({
                        label: categoria || "Sin valor",
                        data: valores,
                        borderColor: getColor(index),
                        backgroundColor: getColor(index, 0.5),
                        tension: 0.1,
                        fill: chartType === 'radar'
                    }))
                };
            }
        } else {
            // Asegurarnos de que tenemos datos válidos
            if (!datos.fechas || !datos.valores || 
                !datos.valores.promedio || !datos.valores.suma) {
                console.error("Datos insuficientes para crear gráfico:", datos);
                return;
            }

            chartConfig.data = {
                labels: datos.fechas,
                datasets: [
                    {
                        label: `${campo} - Promedio`,
                        data: datos.valores.promedio,
                        borderColor: getColor(0),
                        backgroundColor: getColor(0, 0.5),
                        tension: 0.1
                    },
                    {
                        label: `${campo} - Total`,
                        data: datos.valores.suma,
                        borderColor: getColor(1),
                        backgroundColor: getColor(1, 0.5),
                        tension: 0.1
                    }
                ]
            };
        }

        if (!isCircularChart) {
            chartConfig.options.scales = {
                x: {
                    display: true,
                    title: { display: true, text: 'Fecha' }
                },
                y: {
                    display: true,
                    title: { display: true, text: datos.tipo === "categorico" ? 'Cantidad' : 'Valor' },
                    beginAtZero: true
                }
            };
        }

        canvas.chart = new Chart(ctx, chartConfig);
    };

    chartTypeSelector.addEventListener('change', (e) => updateChart(e.target.value));
    
    // Timeout pequeño para asegurar que el DOM está listo
    setTimeout(() => {
        updateChart('line');
    }, 100);
}

/**
 * Obtiene un color para los gráficos
 * @param {number} index - Índice del color
 * @param {number} alpha - Transparencia (0-1)
 * @returns {string} - Color en formato rgba
 */
function getColor(index, alpha = 1) {
    const colors = [
        [75, 192, 192],    // Verde azulado
        [255, 99, 132],    // Rosa
        [255, 206, 86],    // Amarillo
        [54, 162, 235],    // Azul
        [153, 102, 255],   // Morado
        [255, 159, 64],    // Naranja
        [201, 203, 207],   // Gris
        [255, 99, 71],     // Rojo tomate
        [50, 205, 50],     // Lima
        [138, 43, 226],    // Azul violeta
        [255, 215, 0]      // Oro
    ];

    // Si se necesitan más colores, generar dinámicamente
    if (index >= colors.length) {
        // Generar un color aleatorio pero consistente basado en el índice
        const r = Math.sin(index * 1.666) * 127 + 128;
        const g = Math.sin(index * 3.333) * 127 + 128;
        const b = Math.sin(index * 5.0) * 127 + 128;
        return `rgba(${Math.floor(r)},${Math.floor(g)},${Math.floor(b)},${alpha})`;
    }

    return `rgba(${colors[index % colors.length].join(',')},${alpha})`;
}

/**
 * Función para copiar el contenido de un elemento al portapapeles
 * @param {string} elementId - ID del elemento a copiar
 * @param {string} elementName - Nombre para mostrar en el texto copiado
 */
function copiarContenido(elementId, elementName) {
    const elemento = document.getElementById(elementId);
    if (!elemento) return;
    
    // Obtener datos de los elementos dentro de la grid
    let textoCopiado = `** DATOS DE ${elementName} **\n\n`;
    
    // Para cada item en la grid
    const items = elemento.querySelectorAll('.flex.justify-between');
    items.forEach(item => {
        const clave = item.querySelector('span:first-child').textContent.trim();
        const valor = item.querySelector('span:last-child').textContent.trim();
        textoCopiado += `${clave}: ${valor}\n`;
    });
    
    // Información de resumen si existe
    const resumen = elemento.parentNode.querySelector('.text-sm.text-gray-600');
    if (resumen) {
        textoCopiado += "\n** RESUMEN **\n";
        resumen.querySelectorAll('.flex.justify-between').forEach(item => {
            textoCopiado += item.textContent.trim() + "\n";
        });
    }
    
    // Usar el API de Clipboard moderno
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textoCopiado)
            .then(() => {
                showCopySuccess(elementId);
            })
            .catch(err => {
                console.error('Error al copiar con Clipboard API:', err);
                fallbackCopyToClipboard(textoCopiado, elementId);
            });
    } else {
        fallbackCopyToClipboard(textoCopiado, elementId);
    }
}

/**
 * Método alternativo para copiar al portapapeles
 * @param {string} text - Texto a copiar
 * @param {string} elementId - ID del elemento asociado
 */
function fallbackCopyToClipboard(text, elementId) {
    try {
        const tempElement = document.createElement("textarea");
        tempElement.value = text;
        tempElement.setAttribute("readonly", "");
        tempElement.style.position = "absolute";
        tempElement.style.left = "-9999px";
        document.body.appendChild(tempElement);
        tempElement.select();
        document.execCommand("copy");
        document.body.removeChild(tempElement);
        showCopySuccess(elementId);
    } catch (err) {
        console.error('Error al copiar con fallback:', err);
        showNotification("No se pudo copiar al portapapeles", "error");
    }
}

/**
 * Muestra un mensaje de éxito al copiar
 * @param {string} elementId - ID del elemento copiado
 */
function showCopySuccess(elementId) {
    const button = document.querySelector(`[data-copy="${elementId}"]`);
    if (button) {
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        
        setTimeout(() => {
            button.innerHTML = originalIcon;
        }, 1500);
    }
    
    showNotification("Contenido copiado al portapapeles", "success");
}

/**
 * Muestra los datos en forma de tabla
 */
async function showTableData(event) {
    event.preventDefault();
    
    try {
        // Validar entrada
        const formData = getFormData();
        if (!formData.tableName) {
            showNotification("Por favor selecciona una tabla", "warning");
            return;
        }

        // Mostrar indicador de carga
        document.getElementById("loading-indicator").classList.remove("hidden");

        // Destruir instancia previa de DataTable
        if ($.fn.DataTable.isDataTable('#analisis-table')) {
            $('#analisis-table').DataTable().destroy();
        }

        // Limpia los encabezados y el cuerpo de la tabla
        $('#table-headers').empty();
        $('#table-data').empty();

        // Llamada a la API con fechas formateadas
        const response = await fetch("/analisis/analizar_detalle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                table_name: formData.tableName,
                column_name: formData.columnName,
                date_field: formData.dateField,
                start_date: formData.startDate,
                end_date: formData.endDate,
                custom_filters: getCustomFilters()
            })
        });

        if (response.status === 401) {
            window.location.href = "/loginpage";
            return;
        }

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        // Procesa la respuesta
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (!data || !Array.isArray(data.records) || data.records.length === 0) {
            showNotification("No hay registros que mostrar con los filtros actuales", "warning");
            
            document.getElementById("table-section").classList.remove("hidden");
            $('#table-headers').html('<th class="px-4 py-2">Sin datos</th>');
            $('#table-data').html('<tr><td class="px-4 py-2 text-center text-gray-500">No hay datos disponibles</td></tr>');
            
        } else {
            // Genera encabezados
            const headers = Object.keys(data.records[0]);
            headers.forEach(header => {
                $('#table-headers').append($('<th>').text(header).addClass('px-4 py-2 text-left text-gray-700 font-semibold'));
            });

            // Genera filas
            data.records.forEach(record => {
                const row = $('<tr>').addClass('border-t border-gray-200 hover:bg-gray-50');
                headers.forEach(header => {
                    row.append($('<td>').text(record[header] ?? '').addClass('px-4 py-2 text-sm text-gray-700'));
                });
                $('#table-data').append(row);
            });

            // Inicializa DataTables con configuración personalizada
            $('#analisis-table').DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
                },
                responsive: true,
                pageLength: 10,
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
                dom: 'Bfrtip',
                buttons: [
                    'copy', 'csv', 'excel', 'pdf'
                ]
            });
            
            showNotification(`Se cargaron ${data.records.length} registros`, "success");
        }
    } catch (error) {
        console.error("Error al obtener los datos de la tabla:", error);
        showNotification(`Error al obtener los datos: ${error.message}`, "error");
        
        // Mostrar mensaje de error en la tabla
        $('#table-headers').html('<th class="px-4 py-2">Error</th>');
        $('#table-data').html(`<tr><td class="px-4 py-2 text-center text-red-500">
            ${error.message}
        </td></tr>`);
    } finally {
        document.getElementById("loading-indicator").classList.add("hidden");
    }

    // Mostrar la sección de tabla y ocultar las demás
    toggleSections("table-section");
}

/**
 * Obtiene los datos del formulario
 * @returns {Object} - Objeto con los datos del formulario
 */
function getFormData() {
    return {
        tableName: document.getElementById("table-select").value || "",
        columnName: document.getElementById("column-select").value || "",
        dateField: document.getElementById("date_field").value || "",
        startDate: document.getElementById("start_date").value || "",
        endDate: document.getElementById("end_date").value || "",
        additionalFields: Array.from(document.querySelectorAll('select[name="additional_fields[]"]'))
            .map(select => select.value)
            .filter(Boolean)
            .join(',')
    };
}

/**
 * Muestra una sección específica y oculta las demás
 * @param {string} sectionToShow - ID de la sección a mostrar
 */
function toggleSections(sectionToShow) {
    const allSections = ["kpi-section", "graph-section", "table-section"];
    
    allSections.forEach(section => {
        const sectionElement = document.getElementById(section);
        if (sectionElement) {
            if (section === sectionToShow) {
                sectionElement.classList.remove("hidden");
            } else {
                sectionElement.classList.add("hidden");
            }
        }
    });
}

/**
 * Inicializa la aplicación
 */
document.addEventListener('DOMContentLoaded', function() {
    try {
        initProfileMenu();
        setDefaultDate();
        initEventListeners();
        
        console.log("Analizador de datos SQL App Studio inicializado correctamente");
    } catch (error) {
        console.error("Error al inicializar la aplicación:", error);
    }
});