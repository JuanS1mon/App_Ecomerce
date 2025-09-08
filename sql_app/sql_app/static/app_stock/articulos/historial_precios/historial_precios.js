/**
 * Historial de Precios - Script principal
 * 
 * Este script maneja las funcionalidades del historial de precios:
 * - Interacciones con la tabla de historial
 * - Visualización de gráficos de evolución de precios
 * - Gestión del menú de usuario y otros elementos UI
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar menú de usuario
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');

    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', function() {
            userMenu.classList.toggle('hidden');
        });

        // Cerrar menú al hacer clic fuera
        document.addEventListener('click', function(event) {
            if (!userMenuButton.contains(event.target) && !userMenu.contains(event.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }

    // Funcionalidad para exportar a Excel
    const btnExportarExcel = document.getElementById('btn-exportar-excel');
    if (btnExportarExcel) {
        btnExportarExcel.addEventListener('click', exportarExcel);
    }

    // Funcionalidad para exportar a PDF
    const btnExportarPDF = document.getElementById('btn-exportar-pdf');
    if (btnExportarPDF) {
        btnExportarPDF.addEventListener('click', exportarPDF);
    }

    // Inicializar evento de entrada en filtro de artículo para autocompletar
    const filtroArticulo = document.getElementById('filtro-articulo');
    if (filtroArticulo) {
        let typingTimer;
        const doneTypingInterval = 500;

        filtroArticulo.addEventListener('keyup', function() {
            clearTimeout(typingTimer);
            if (filtroArticulo.value) {
                typingTimer = setTimeout(buscarArticulos, doneTypingInterval);
            }
        });
    }
});

/**
 * Busca artículos para autocompletado
 */
async function buscarArticulos() {
    const filtroArticulo = document.getElementById('filtro-articulo');
    const query = filtroArticulo.value.trim();
    
    if (query.length < 3) return;
    
    try {
        // En implementación real, esto sería una llamada a la API
        console.log(`Buscando artículos con: ${query}`);
        // Implementar autocomplete aquí cuando la API esté disponible
    } catch (error) {
        console.error('Error al buscar artículos:', error);
    }
}

/**
 * Exporta la tabla de historial a Excel
 */
async function exportarExcel() {
    try {
        // En implementación real, esto podría ser una llamada a la API que genera un Excel
        // o usar una librería JS para generar el archivo directamente en el navegador
        console.log('Exportando a Excel...');
        
        const fechaDesde = document.getElementById('fecha-desde').value;
        const fechaHasta = document.getElementById('fecha-hasta').value;
        const tipoPrecio = document.getElementById('tipo-precio').value;
        const filtroArticulo = document.getElementById('filtro-articulo').value;
        
        // Simulación de la llamada a la API
        setTimeout(() => {
            alert('El archivo Excel se está generando y se descargará en breve.');
            // Aquí iría la lógica real para descargar el archivo
        }, 1000);
        
    } catch (error) {
        console.error('Error al exportar a Excel:', error);
        alert('Ha ocurrido un error al generar el archivo Excel. Por favor, inténtelo de nuevo.');
    }
}

/**
 * Exporta la tabla de historial a PDF
 */
async function exportarPDF() {
    try {
        // En implementación real, esto podría ser una llamada a la API que genera un PDF
        // o usar una librería JS para generar el archivo directamente en el navegador
        console.log('Exportando a PDF...');
        
        const fechaDesde = document.getElementById('fecha-desde').value;
        const fechaHasta = document.getElementById('fecha-hasta').value;
        const tipoPrecio = document.getElementById('tipo-precio').value;
        const filtroArticulo = document.getElementById('filtro-articulo').value;
        
        // Simulación de la llamada a la API
        setTimeout(() => {
            alert('El archivo PDF se está generando y se descargará en breve.');
            // Aquí iría la lógica real para descargar el archivo
        }, 1000);
        
    } catch (error) {
        console.error('Error al exportar a PDF:', error);
        alert('Ha ocurrido un error al generar el archivo PDF. Por favor, inténtelo de nuevo.');
    }
}

/**
 * Actualiza el gráfico de evolución de precios para un artículo específico
 */
async function actualizarGraficoEvolucion(codigoArticulo) {
    if (!codigoArticulo) return;
    
    try {
        // En implementación real, esto sería una llamada a la API para obtener los datos
        console.log(`Obteniendo evolución de precios para: ${codigoArticulo}`);
        
        // La lógica del gráfico está en el script embebido en el HTML por ahora
        // Se moverá aquí cuando la API esté disponible
    } catch (error) {
        console.error('Error al actualizar gráfico:', error);
    }
}

/**
 * Formatea un valor monetario para mostrar en la UI
 * @param {number} valor - El valor a formatear
 * @returns {string} - El valor formateado como moneda argentina
 */
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS'
    }).format(valor);
}

/**
 * Calcula la variación porcentual entre dos valores
 * @param {number} valorAnterior - Valor anterior
 * @param {number} valorNuevo - Valor nuevo
 * @returns {number} - Porcentaje de variación
 */
function calcularVariacionPorcentual(valorAnterior, valorNuevo) {
    if (valorAnterior === 0) return 0;
    return ((valorNuevo - valorAnterior) / valorAnterior) * 100;
}

/**
 * Formatea una fecha para mostrar en la UI
 * @param {string|Date} fecha - La fecha a formatear
 * @returns {string} - La fecha formateada
 */
function formatearFecha(fecha) {
    if (!fecha) return '';
    const date = fecha instanceof Date ? fecha : new Date(fecha);
    return date.toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

/**
 * Formatea una fecha y hora para mostrar en la UI
 * @param {string|Date} fecha - La fecha a formatear
 * @returns {string} - La fecha y hora formateada
 */
function formatearFechaHora(fecha) {
    if (!fecha) return '';
    const date = fecha instanceof Date ? fecha : new Date(fecha);
    return `${date.toLocaleDateString('es-AR')} ${date.toLocaleTimeString('es-AR', {
        hour: '2-digit',
        minute: '2-digit'
    })}`;
}