// Repositorio para manejar operaciones con tickets
window.ticketRepository = {
    create: function(formData) {
        return fetch('/tickets/crear', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en el servidor: ' + response.status);
            }
            return response.json();
        });
    },
    
    getById: function(id) {
        return fetch(`/tickets/id/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al obtener el ticket: ' + response.status);
            }
            return response.json();
        });
    },
    
    update: function(id, data) {
        return fetch(`/tickets/id/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al actualizar el ticket: ' + response.status);
            }
            return response.json();
        });
    }
};

// Actualizar fecha y hora
function updateDateTime() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = now.toLocaleDateString('es-ES', options);
    document.getElementById('currentTime').textContent = now.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit'
    });
}

// Función para mostrar notificaciones
function showNotification(title, message, type = 'info') {
    // Crear el contenedor si no existe
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed right-0 top-0 p-4 space-y-4 z-50';
        document.body.appendChild(container);
    }
    
    // Crear la notificación
    const notification = document.createElement('div');
    notification.className = `max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto border-l-4 ${
        type === 'success' ? 'border-green-500' : 
        type === 'error' ? 'border-red-500' : 
        'border-blue-500'
    } overflow-hidden transform transition-all duration-300 ease-out opacity-0 translate-x-8`;
    
    notification.innerHTML = `
        <div class="p-4">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="fas ${
                        type === 'success' ? 'fa-check-circle text-green-500' : 
                        type === 'error' ? 'fa-exclamation-circle text-red-500' : 
                        'fa-info-circle text-blue-500'
                    } text-lg"></i>
                </div>
                <div class="ml-3 w-0 flex-1">
                    <p class="text-sm font-medium text-gray-900">${title}</p>
                    <p class="mt-1 text-sm text-gray-500">${message}</p>
                </div>
                <div class="ml-4 flex-shrink-0 flex">
                    <button class="inline-flex text-gray-400 hover:text-gray-500">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Añadir al contenedor
    container.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.classList.remove('opacity-0', 'translate-x-8');
    }, 10);
    
    // Configurar cierre
    const closeBtn = notification.querySelector('button');
    closeBtn.addEventListener('click', () => removeNotification(notification));
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        removeNotification(notification);
    }, 5000);
}

function removeNotification(notification) {
    notification.classList.add('opacity-0', '-translate-y-2');
    setTimeout(() => {
        notification.remove();
    }, 300);
}

// Inicializar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Ejecutar al cargar y actualizar cada minuto
    updateDateTime();
    setInterval(updateDateTime, 60000);
    
    // Lógica para el formulario de tickets
    const form = document.getElementById('ticketForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Mostrar indicador de carga
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Enviando...';
            
            // Crear objeto FormData con los datos del formulario
            const formData = new FormData(form);
            
            // Usar el repositorio para crear el ticket
            window.ticketRepository.create(formData)
                .then(data => {
                    // Mostrar notificación de éxito
                    showNotification('¡Ticket creado con éxito!', 'Su solicitud ha sido registrada y será atendida a la brevedad.', 'success');
                    
                    // Redirigir después de un breve retraso
                    setTimeout(() => {
                        window.location.href = '/tickets/listar';
                    }, 2000);
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Error', 'No se pudo crear el ticket. Por favor, inténtelo de nuevo.', 'error');
                })
                .finally(() => {
                    // Restaurar el botón
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalButtonText;
                });
        });
    }
    
    // Preview de archivos seleccionados
    const inputAdjuntos = document.getElementById('adjuntos');
    if (inputAdjuntos) {
        inputAdjuntos.addEventListener('change', function(e) {
            const numFiles = e.target.files.length;
            const fileInfo = numFiles > 0 
                ? `${numFiles} archivo${numFiles > 1 ? 's' : ''} seleccionado${numFiles > 1 ? 's' : ''}`
                : 'Ningún archivo seleccionado';
                
            const parent = this.parentElement;
            const infoTextElement = parent.querySelector('p.mb-2');
            if (infoTextElement) {
                infoTextElement.textContent = fileInfo;
            }
        });
    }
});