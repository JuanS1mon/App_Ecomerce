// Manejo del menú de perfil
document.addEventListener('DOMContentLoaded', function() {
    const perfilBtn = document.getElementById('perfil');
    const perfilMenu = document.getElementById('menu-perfil');

    // Verificar que los elementos existan antes de agregar event listeners
    if (perfilBtn && perfilMenu) {
        perfilBtn.addEventListener('click', function(event) {
            event.preventDefault();
            perfilMenu.classList.toggle('hidden');
        });

        document.addEventListener('click', function(event) {
            const isClickInside = perfilBtn.contains(event.target) || perfilMenu.contains(event.target);
            if (!isClickInside) {
                perfilMenu.classList.add('hidden');
            }
        });
    }

    // Inicialización del gráfico de actividad de scraping
    const ctx = document.getElementById('scrapingChart');
    
    if (ctx) {
        // Intentar usar datos dinámicos si están disponibles
        let chartData;
        
        try {
            // Intentar obtener datos desde el backend si están disponibles
            chartData = JSON.parse('{{ chart_data | tojson | safe }}');
        } catch (error) {
            // Si no hay datos dinámicos disponibles, usar datos predeterminados
            chartData = {
                labels: [
                    '2025-01-01', '2025-01-08', '2025-01-15', '2025-01-22', '2025-02-01',
                    '2025-02-08', '2025-02-15', '2025-02-22', '2025-03-01', '2025-03-08'
                ],
                datasets: [{
                    label: 'Ejecuciones de Scraping',
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 2,
                    data: [4, 7, 5, 8, 6, 9, 12, 8, 10, 7],
                    tension: 0.4
                }]
            };
        }

        // Configuración del gráfico
        const config = {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            tooltipFormat: 'YYYY-MM-DD'
                        },
                        title: {
                            display: true,
                            text: 'Fecha'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cantidad de Scraping'
                        },
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        };

        // Crear el gráfico
        new Chart(ctx, config);
    }

    // Añadir listeners para los botones de acción de scraping
    const actionButtons = document.querySelectorAll('[data-scraping-action]');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const action = this.getAttribute('data-scraping-action');
            const scraperId = this.getAttribute('data-scraper-id');
            
            console.log(`Acción '${action}' solicitada para scraper ID: ${scraperId}`);
            
            // Aquí puedes implementar la lógica específica para cada acción
            // como ejecutar, editar o ver resultados
        });
    });
});