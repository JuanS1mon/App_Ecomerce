// Actualización de fecha y hora
function updateDateTime() {
    const now = new Date();
    
    // Formatear la fecha en español
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateFormatted = now.toLocaleDateString('es-ES', options);
    
    // Formatear la hora
    const timeFormatted = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    
    // Actualizar elementos DOM
    document.getElementById('currentDate').textContent = dateFormatted;
    document.getElementById('currentTime').textContent = timeFormatted;
}

// Inicializar gráfico de actividad
function initActivityChart() {
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    // Datos de ejemplo para el gráfico
    const labels = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'];
    const entradas = [65, 59, 80, 81, 56, 55];
    const salidas = [28, 48, 40, 19, 86, 27];
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Entradas',
                    data: entradas,
                    borderColor: '#4F46E5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Salidas',
                    data: salidas,
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                },
                x: {
                    grid: {
                        drawBorder: false,
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Cargar componentes
function loadComponents() {
    // Cargar navbar
    const navbarContainer = document.getElementById('navbar-container');
    if (navbarContainer) {
        loadComponent('navbar', navbarContainer);
    }
    
    // Cargar footer
    const footerContainer = document.getElementById('footer-container');
    if (footerContainer) {
        loadComponent('footer', footerContainer);
    }
}

// Función para cargar componentes (simulada)
function loadComponent(componentName, container) {
    // Esta función normalmente utilizaría fetch o XMLHttpRequest
    // para cargar componentes desde el servidor
    console.log(`Componente ${componentName} cargado`);
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 60000); // Actualizar cada minuto
    initActivityChart();
    loadComponents();
});