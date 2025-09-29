/**
 * Dashboard de Obras de Arte - Scripts JavaScript
 * Sistema de gestión de obras de arte
 */

class ObrasDashboard {
    constructor() {
        this.chartInstance = null;
        this.init();
    }

    /**
     * Inicializar el dashboard
     */
    init() {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeComponents();
            });
        } else {
            this.initializeComponents();
        }
    }

    /**
     * Inicializar todos los componentes del dashboard
     */
    initializeComponents() {
        this.loadDashboardData();
        this.initializeChart();
        this.startTimeUpdater();
    }

    /**
     * Cargar datos del dashboard desde la API
     */
    async loadDashboardData() {
        try {
            const response = await fetch('/app_obras/dashboard/api/stats');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            
            if (result.success) {
                this.updateChartWithData(result.data);
            } else {
                console.error('Error al cargar datos:', result);
            }
        } catch (error) {
            console.error('Error al cargar datos del dashboard:', error);
            // Usar datos por defecto si hay error
            this.initializeChartWithDefaults();
        }
    }

    /**
     * Inicializar el gráfico de disponibilidad
     */
    initializeChart() {
        const canvas = document.getElementById('availabilityChart');
        if (!canvas) {
            console.warn('Canvas availabilityChart no encontrado');
            return;
        }

        // Si ya existe un gráfico, destruirlo
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        const ctx = canvas.getContext('2d');
        this.chartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Disponibles', 'Vendidas', 'No Disponibles'],
                datasets: [{
                    data: [0, 0, 0], // Datos iniciales
                    backgroundColor: [
                        '#10B981', // verde - disponibles
                        '#EF4444', // rojo - vendidas
                        '#F59E0B'  // amarillo - no disponibles
                    ],
                    borderColor: [
                        '#059669',
                        '#DC2626', 
                        '#D97706'
                    ],
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    /**
     * Actualizar el gráfico con datos reales
     */
    updateChartWithData(data) {
        if (!this.chartInstance) {
            this.initializeChart();
        }

        if (this.chartInstance && data) {
            const availableArtworks = data.available_artworks || 0;
            const soldArtworks = data.sold_artworks || 0;
            const totalArtworks = data.artworks_count || 0;
            const notAvailableArtworks = Math.max(0, totalArtworks - availableArtworks - soldArtworks);

            this.chartInstance.data.datasets[0].data = [
                availableArtworks,
                soldArtworks,
                notAvailableArtworks
            ];

            this.chartInstance.update('active');
        }
    }

    /**
     * Inicializar gráfico con datos por defecto en caso de error
     */
    initializeChartWithDefaults() {
        if (this.chartInstance) {
            this.chartInstance.data.datasets[0].data = [1, 0, 0];
            this.chartInstance.update();
        }
    }

    /**
     * Iniciar actualizador de tiempo
     */
    startTimeUpdater() {
        // Actualizar tiempo cada minuto
        this.updateTime();
        setInterval(() => {
            this.updateTime();
        }, 60000); // Cada minuto
    }

    /**
     * Actualizar la hora actual en la interfaz
     */
    updateTime() {
        const timeElements = document.querySelectorAll('[data-time="current"]');
        if (timeElements.length > 0) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('es-ES', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            timeElements.forEach(element => {
                element.textContent = timeString;
            });
        }
    }

    /**
     * Recargar estadísticas del dashboard
     */
    async refreshStats() {
        try {
            const response = await fetch('/app_obras/dashboard/api/stats');
            const result = await response.json();
            
            if (result.success) {
                this.updateStatsDisplay(result.data);
                this.updateChartWithData(result.data);
            }
        } catch (error) {
            console.error('Error al recargar estadísticas:', error);
        }
    }

    /**
     * Actualizar la visualización de estadísticas
     */
    updateStatsDisplay(data) {
        // Actualizar contadores en las tarjetas
        const updates = {
            'artworks-count': data.artworks_count,
            'artists-count': data.artists_count,
            'available-artworks': data.available_artworks,
            'exhibitions-count': data.exhibitions_count,
            'current-exhibitions': data.current_exhibitions,
            'sales-count': data.sales_count,
            'pending-payments': data.pending_payments,
            'availability-rate': data.availability_rate + '%',
            'sales-rate': data.sales_rate + '%'
        };

        Object.entries(updates).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    /**
     * Mostrar notificación
     */
    showNotification(message, type = 'info') {
        // Crear notificación temporal
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transition-all duration-300 ${
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'success' ? 'bg-green-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Inicializar el dashboard cuando se carga la página
const dashboard = new ObrasDashboard();

// Exponer funciones globales si es necesario
window.ObrasDashboard = {
    refresh: () => dashboard.refreshStats(),
    notify: (message, type) => dashboard.showNotification(message, type)
};
