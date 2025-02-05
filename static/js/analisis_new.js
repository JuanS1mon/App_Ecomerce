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

// Establecer la fecha actual por defecto en el campo end_date
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    const endDateField = document.getElementById('end_date');
    if (endDateField) {
        endDateField.value = today;
    }
});

// Función para mostrar/ocultar la sección de selección
function toggleSection() {
    const section = document.getElementById('selection-section');
    const icon = document.getElementById('toggle-icon');
    section.classList.toggle('hidden');
    icon.classList.toggle('fa-minus');
    icon.classList.toggle('fa-plus');
}

// Función para agregar un campo adicional
function addField() {
    const container = document.getElementById('additional-fields');
    const field = document.createElement('div');
    field.className = 'mb-4 flex items-center';
    field.innerHTML = `
        <div class="flex-1">
            <label for="additional_field" class="block text-gray-700 font-bold mb-2">Campo Adicional:</label>
            <select name="additional_fields[]" class="block w-full px-4 py-2 border border-gray-300 rounded-md">
                <!-- Opciones de campos adicionales se cargarán aquí -->
            </select>
        </div>
        <button type="button" onclick="removeField(this)" class="ml-4 bg-red-500 text-white px-4 py-2 rounded-md self-end">Eliminar</button>
    `;
    container.appendChild(field);

    // Llenar el nuevo select con las columnas
    const tableName = document.getElementById("table-select").value;
    if (tableName) {
        fetch(`/analisis/columnas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ table_name: tableName })
        })
        .then(response => response.json())
        .then(columnsData => {
            const select = field.querySelector('select[name="additional_fields[]"]');
            select.innerHTML = '<option value="" disabled selected>Selecciona un campo...</option>';
            columnsData.columns.forEach(column => {
                select.innerHTML += `<option value="${column.name}">${column.name}</option>`;
            });
        });
    }
}

// Función para eliminar un campo adicional
function removeField(button) {
    const field = button.parentElement;
    field.remove();
}

// Variables para las secciones de KPIs, gráficos y tabla
const kpiSection = document.getElementById("kpi-section");
const graphSection = document.getElementById("graph-section");
const tableSection = document.getElementById("table-section");

// Mostrar la sección de KPIs y cargar datos de /analizar_kpis
document.getElementById("show-kpis").addEventListener("click", async () => {
    try {
        // Obtener valores desde el formulario
        const tableName = document.getElementById("table-select").value;
        const columnName = document.getElementById("column-select").value;
        const dateField = document.getElementById("date_field").value;
        const startDate = document.getElementById("start_date").value;
        const endDate = document.getElementById("end_date").value;
        
        // (Ejemplo) Suponiendo que solo tomamos un campo adicional
        let additionalField = null;
        const additionalFieldsSelect = document.querySelector('select[name="additional_fields[]"]');
        if (additionalFieldsSelect) {
            additionalField = additionalFieldsSelect.value;
        }

        // Llamada a la API
        const response = await fetch("/analisis/analizar_kpis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                table_name: tableName,
                column_name: columnName,
                date_field: dateField,
                start_date: startDate,
                end_date: endDate,
                additional_field: additionalField
            })
        });

        const data = await response.json();

        // Actualizar KPIs en el HTML
        document.getElementById("total-records").textContent = data.total_registros ?? "-";
        document.getElementById("categories").textContent = data.categorias ?? "-";
        document.getElementById("last-date").textContent = data.last_date ?? "-";
        document.getElementById("first-date").textContent = data.first_date ?? "-";
        document.getElementById("max-value").textContent = data.max_value ?? "-";
        document.getElementById("min-value").textContent = data.min_value ?? "-";

        // Suponiendo que 'clusters' sea una lista
        const clusterUl = document.getElementById("cluster-results");
        clusterUl.innerHTML = "";
        if (data.clusters && Array.isArray(data.clusters)) {
            data.clusters.forEach(cluster => {
                const li = document.createElement("li");
                li.textContent = cluster;
                clusterUl.appendChild(li);
            });
        }
    } catch (err) {
        console.error("Error al analizar KPIs:", err);
    }

    // Mostrar la sección de KPIs y ocultar las demás
    kpiSection.classList.remove("hidden");
    graphSection.classList.add("hidden");
    tableSection.classList.add("hidden");
});

// Mostrar la sección de gráficos
document.getElementById("show-graph").addEventListener("click", () => {
    kpiSection.classList.add("hidden");
    graphSection.classList.remove("hidden");
    tableSection.classList.add("hidden");

    // Carga de gráfico dinámico
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Enero', 'Febrero', 'Marzo'],
            datasets: [{
                label: 'Ejemplo',
                data: [10, 20, 30],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        }
    });
});

// Mostrar la sección de tabla detallada
document.getElementById("show-table").addEventListener("click", () => {
    kpiSection.classList.add("hidden");
    graphSection.classList.add("hidden");
    tableSection.classList.remove("hidden");

    // Ejemplo de datos dinámicos
    const headers = ["Columna 1", "Columna 2", "Columna 3"];
    const data = [
        ["Dato 1", "Dato 2", "Dato 3"],
        ["Dato A", "Dato B", "Dato C"]
    ];

    const headerRow = document.getElementById("table-headers");
    headerRow.innerHTML = headers.map(header => `<th class="border px-4 py-2">${header}</th>`).join("");

    const tableBody = document.getElementById("table-data");
    tableBody.innerHTML = data.map(row => 
        `<tr>${row.map(cell => `<td class="border px-4 py-2">${cell}</td>`).join("")}</tr>`
    ).join("");
});

document.addEventListener("DOMContentLoaded", () => {
    inicializarFechaPorDefecto();
    asignarEventosBotones();
    asignarEventoCambioTabla();
});

function inicializarFechaPorDefecto() {
    const endDateField = document.getElementById("end_date");
    if (endDateField) {
        endDateField.value = new Date().toISOString().split('T')[0];
    }
}

function asignarEventosBotones() {
    const showKpisBtn = document.getElementById("show-kpis");
    const showGraphBtn = document.getElementById("show-graph");
    const showTableBtn = document.getElementById("show-table");
    const showClusteringBtn = document.getElementById("show-clustering");
    const showClassificationBtn = document.getElementById("show-classification");
    const showRegressionBtn = document.getElementById("show-regression");

    showKpisBtn.addEventListener("click", cargarKPIs);
    showGraphBtn.addEventListener("click", mostrarGrafico);
    showTableBtn.addEventListener("click", mostrarTabla);
    showClusteringBtn.addEventListener("click", () => ocultarSecciones("clustering"));
    showClassificationBtn.addEventListener("click", () => ocultarSecciones("classification"));
    showRegressionBtn.addEventListener("click", () => ocultarSecciones("regression"));
}

function asignarEventoCambioTabla() {
    const tableSelect = document.getElementById("table-select");
    tableSelect.addEventListener("change", async () => {
        const tableName = tableSelect.value;
        if (!tableName) return;
        const columnsData = await fetchColumns(tableName);
        poblarColumnSelect(columnsData);
        poblarDateField(columnsData);
        poblarCamposAdicionales(columnsData);
    });
}

async function fetchColumns(tableName) {
    const res = await fetch(`/analisis/columnas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table_name: tableName })
    });
    return res.json();
}

function poblarColumnSelect(columnsData) {
    const columnSelect = document.getElementById("column-select");
    columnSelect.innerHTML = '<option value="" disabled selected>Selecciona una columna...</option>';
    columnsData.columns
        .filter(col => ['INTEGER','BIGINT'].includes(col.type.toUpperCase()))
        .forEach(col => {
            columnSelect.innerHTML += `<option value="${col.name}">${col.name}</option>`;
        });
}

function poblarDateField(columnsData) {
    const dateFieldSelect = document.getElementById("date_field");
    dateFieldSelect.innerHTML = '<option value="" disabled selected>Selecciona un campo de fecha...</option>';
    columnsData.columns
        .filter(col => ['DATE','DATETIME','SMALLDATETIME'].includes(col.type.toUpperCase()))
        .forEach(col => {
            dateFieldSelect.innerHTML += `<option value="${col.name}">${col.name}</option>`;
        });
}

function poblarCamposAdicionales(columnsData) {
    const additionalFieldsSelects = document.querySelectorAll('select[name="additional_fields[]"]');
    additionalFieldsSelects.forEach(select => {
        select.innerHTML = '<option value="" disabled selected>Selecciona un campo...</option>';
        columnsData.columns.forEach(col => {
            select.innerHTML += `<option value="${col.name}">${col.name}</option>`;
        });
    });
}

async function cargarKPIs() {
    try {
        const tableName = document.getElementById("table-select").value;
        const columnName = document.getElementById("column-select").value;
        const dateField = document.getElementById("date_field").value;
        const startDate = document.getElementById("start_date").value;
        const endDate = document.getElementById("end_date").value;
        const additionalField = obtenerCampoAdicional();

        const response = await fetch("/analisis/analizar_kpis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                table_name: tableName, 
                column_name: columnName, 
                date_field: dateField, 
                start_date: startDate, 
                end_date: endDate, 
                additional_field: additionalField 
            })
        });
        const data = await response.json();

        document.getElementById("total-records").textContent = data.total_registros ?? "-";
        document.getElementById("categories").textContent = data.categorias ?? "-";
        document.getElementById("last-date").textContent = data.last_date ?? "-";
        document.getElementById("first-date").textContent = data.first_date ?? "-";
        document.getElementById("max-value").textContent = data.max_value ?? "-";
        document.getElementById("min-value").textContent = data.min_value ?? "-";

        const clusterUl = document.getElementById("cluster-results");
        clusterUl.innerHTML = "";
        if (data.clusters && Array.isArray(data.clusters)) {
            data.clusters.forEach(cluster => {
                const li = document.createElement("li");
                li.textContent = cluster;
                clusterUl.appendChild(li);
            });
        }
    } catch (err) {
        console.error("Error al cargar KPIs:", err);
    }
    ocultarSecciones("kpi");
}

function mostrarGrafico() {
    ocultarSecciones("graph");
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Enero', 'Febrero', 'Marzo'],
            datasets: [{
                label: 'Ejemplo',
                data: [10, 20, 30],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        }
    });
}

function mostrarTabla() {
    ocultarSecciones("table");
    const headers = ["Columna 1", "Columna 2", "Columna 3"];
    const data = [
        ["Dato 1", "Dato 2", "Dato 3"],
        ["Dato A", "Dato B", "Dato C"]
    ];
    const headerRow = document.getElementById("table-headers");
    headerRow.innerHTML = headers.map(h => `<th class="border px-4 py-2">${h}</th>`).join("");
    const tableBody = document.getElementById("table-data");
    tableBody.innerHTML = data.map(row =>
        `<tr>${row.map(cell => `<td class="border px-4 py-2">${cell}</td>`).join("")}</tr>`
    ).join("");
}

function ocultarSecciones(sectionToShow) {
    const kpiSection = document.getElementById("kpi-section");
    const graphSection = document.getElementById("graph-section");
    const tableSection = document.getElementById("table-section");

    kpiSection.classList.toggle("hidden", sectionToShow !== "kpi");
    graphSection.classList.toggle("hidden", sectionToShow !== "graph");
    tableSection.classList.toggle("hidden", sectionToShow !== "table");
    // Aquí podrías manejar las demás secciones (clustering, clasificación, regresión) si existieran paneles de UI separados.
}

function obtenerCampoAdicional() {
    const additionalFieldsSelect = document.querySelector('select[name="additional_fields[]"]');
    return additionalFieldsSelect ? additionalFieldsSelect.value : null;
}

function addField() {
    const container = document.getElementById('additional-fields');
    const field = document.createElement('div');
    field.className = 'mb-4 flex items-center';
    field.innerHTML = `
        <div class="flex-1">
            <label for="additional_field" class="block text-gray-700 font-bold mb-2">Campo Adicional:</label>
            <select name="additional_fields[]" class="block w-full px-4 py-2 border border-gray-300 rounded-md">
                <!-- Opciones de campos adicionales se cargarán aquí -->
            </select>
        </div>
        <button type="button" onclick="removeField(this)" class="ml-4 bg-red-500 text-white px-4 py-2 rounded-md self-end">Eliminar</button>
    `;
    container.appendChild(field);

    const tableName = document.getElementById("table-select").value;
    if (tableName) {
        fetch(`/analisis/columnas`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ table_name: tableName })
        })
        .then(response => response.json())
        .then(columnsData => {
            const select = field.querySelector('select[name="additional_fields[]"]');
            select.innerHTML = '<option value="" disabled selected>Selecciona un campo...</option>';
            columnsData.columns.forEach(column => {
                select.innerHTML += `<option value="${column.name}">${column.name}</option>`;
            });
        });
    }
}

function removeField(button) {
    const field = button.parentElement;
    field.remove();
}

function toggleSection() {
    const section = document.getElementById('selection-section');
    const icon = document.getElementById('toggle-icon');
    section.classList.toggle('hidden');
    icon.classList.toggle('fa-minus');
    icon.classList.toggle('fa-plus');
}