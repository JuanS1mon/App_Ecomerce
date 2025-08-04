/**
 * TicketService - Capa de abstracción para gestionar operaciones relacionadas con tickets
 * Este servicio maneja las comunicaciones con el backend y proporciona métodos
 * para recuperar y manipular datos de tickets.
 */

class TicketService {
    /**
     * Constructor de la clase
     * @param {string} baseUrl - URL base para las peticiones API (opcional)
     */
    constructor(baseUrl = '/api/tickets') {
        this.baseUrl = baseUrl;
        this.cache = {};
    }
    
    /**
     * Obtiene estadísticas de tickets según el periodo especificado
     * @param {string} periodo - Periodo de tiempo ('hoy', 'semana', 'mes', 'anio')
     * @returns {Promise} Promesa con los datos de estadísticas
     */
    async obtenerEstadisticasPorPeriodo(periodo) {
        try {
            // Verificar si está en caché y no ha expirado
            if (this.cache[periodo] && this.cache[periodo].timestamp > Date.now() - 300000) { // 5 minutos
                return this.cache[periodo].data;
            }
            
            const respuesta = await fetch(`${this.baseUrl}/estadisticas?periodo=${periodo}`);
            if (!respuesta.ok) {
                throw new Error(`Error al obtener estadísticas: ${respuesta.statusText}`);
            }
            
            const datos = await respuesta.json();
            
            // Guardar en caché
            this.cache[periodo] = {
                data: datos,
                timestamp: Date.now()
            };
            
            return datos;
        } catch (error) {
            console.error('Error en obtenerEstadisticasPorPeriodo:', error);
            throw error;
        }
    }
    
    /**
     * Obtiene estadísticas de tickets para un rango de fechas personalizado
     * @param {string} fechaInicio - Fecha de inicio (formato YYYY-MM-DD)
     * @param {string} fechaFin - Fecha de fin (formato YYYY-MM-DD)
     * @returns {Promise} Promesa con los datos de estadísticas
     */
    async obtenerEstadisticasPorFechas(fechaInicio, fechaFin) {
        try {
            const cacheKey = `${fechaInicio}_${fechaFin}`;
            
            // Verificar si está en caché y no ha expirado
            if (this.cache[cacheKey] && this.cache[cacheKey].timestamp > Date.now() - 300000) {
                return this.cache[cacheKey].data;
            }
            
            const respuesta = await fetch(`${this.baseUrl}/estadisticas?fechaInicio=${fechaInicio}&fechaFin=${fechaFin}`);
            if (!respuesta.ok) {
                throw new Error(`Error al obtener estadísticas: ${respuesta.statusText}`);
            }
            
            const datos = await respuesta.json();
            
            // Guardar en caché
            this.cache[cacheKey] = {
                data: datos,
                timestamp: Date.now()
            };
            
            return datos;
        } catch (error) {
            console.error('Error en obtenerEstadisticasPorFechas:', error);
            throw error;
        }
    }
    
    /**
     * Obtiene un ticket por su ID
     * @param {number} id - ID del ticket
     * @returns {Promise} Promesa con los datos del ticket
     */
    async obtenerTicketPorId(id) {
        try {
            const respuesta = await fetch(`${this.baseUrl}/${id}`);
            if (!respuesta.ok) {
                throw new Error(`Error al obtener ticket: ${respuesta.statusText}`);
            }
            return await respuesta.json();
        } catch (error) {
            console.error(`Error al obtener ticket ${id}:`, error);
            throw error;
        }
    }
    
    /**
     * Obtiene tickets según criterios de filtrado
     * @param {Object} filtros - Criterios de filtrado
     * @returns {Promise} Promesa con la lista de tickets
     */
    async obtenerTickets(filtros = {}) {
        try {
            const params = new URLSearchParams();
            
            // Agregar filtros a los parámetros de consulta
            Object.entries(filtros).forEach(([clave, valor]) => {
                if (valor !== undefined && valor !== null) {
                    params.append(clave, valor);
                }
            });
            
            const url = `${this.baseUrl}?${params.toString()}`;
            const respuesta = await fetch(url);
            
            if (!respuesta.ok) {
                throw new Error(`Error al obtener tickets: ${respuesta.statusText}`);
            }
            
            return await respuesta.json();
        } catch (error) {
            console.error('Error en obtenerTickets:', error);
            throw error;
        }
    }
    
    /**
     * Exporta datos de tickets a Excel
     * @param {Object} filtros - Criterios de filtrado para la exportación
     * @returns {Promise} Promesa que se resuelve cuando se inicia la descarga
     */
    async exportarExcel(filtros = {}) {
        try {
            const params = new URLSearchParams();
            
            Object.entries(filtros).forEach(([clave, valor]) => {
                if (valor !== undefined && valor !== null) {
                    params.append(clave, valor);
                }
            });
            
            const url = `${this.baseUrl}/exportar/excel?${params.toString()}`;
            window.location.href = url;
            
            return true;
        } catch (error) {
            console.error('Error en exportarExcel:', error);
            throw error;
        }
    }
    
    /**
     * Genera un informe PDF de tickets
     * @param {Object} filtros - Criterios de filtrado para el informe
     * @returns {Promise} Promesa que se resuelve cuando se inicia la descarga
     */
    async generarInformePDF(filtros = {}) {
        try {
            const params = new URLSearchParams();
            
            Object.entries(filtros).forEach(([clave, valor]) => {
                if (valor !== undefined && valor !== null) {
                    params.append(clave, valor);
                }
            });
            
            const url = `${this.baseUrl}/exportar/pdf?${params.toString()}`;
            window.location.href = url;
            
            return true;
        } catch (error) {
            console.error('Error en generarInformePDF:', error);
            throw error;
        }
    }
    
    /**
     * Limpia la caché del servicio
     */
    limpiarCache() {
        this.cache = {};
    }
}

// Exportar la clase para su uso en otros archivos
export default TicketService;