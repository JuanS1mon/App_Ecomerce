// Script para cargar los componentes navbar y footer
document.addEventListener('DOMContentLoaded', function() {
    // Cargar el componente navbar
    const navbarPlaceholder = document.getElementById('navbar-placeholder');
    if (navbarPlaceholder) {
        fetch('/static/components/navbar.html')
            .then(response => response.text())
            .then(data => {
                navbarPlaceholder.innerHTML = data;
                
                // Ejecutar cualquier script que esté dentro del componente navbar
                const scripts = navbarPlaceholder.querySelectorAll('script');
                scripts.forEach(script => {
                    const newScript = document.createElement('script');
                    Array.from(script.attributes).forEach(attr => 
                        newScript.setAttribute(attr.name, attr.value));
                    newScript.textContent = script.textContent;
                    script.parentNode.replaceChild(newScript, script);
                });
                
                // Inicializar eventos específicos del navbar
                initNavbarEvents();
                
                // NOTA: El sistema de mensajes ahora se inicializa desde el navbar.html
                // No inicializar desde aquí para evitar conflictos
                
                // Disparar evento para que otros scripts sepan que el navbar se ha cargado
                document.dispatchEvent(new Event('navbarLoaded'));
            })
            .catch(error => console.error('Error cargando el navbar:', error));
    }

    // Cargar el componente footer
    const footerPlaceholder = document.getElementById('footer-placeholder');
    if (footerPlaceholder) {
        fetch('/static/components/footer.html')
            .then(response => response.text())
            .then(data => {
                footerPlaceholder.innerHTML = data;
                
                // Ejecutar cualquier script que esté dentro del componente footer
                const scripts = footerPlaceholder.querySelectorAll('script');
                scripts.forEach(script => {
                    const newScript = document.createElement('script');
                    Array.from(script.attributes).forEach(attr => 
                        newScript.setAttribute(attr.name, attr.value));
                    newScript.textContent = script.textContent;
                    script.parentNode.replaceChild(newScript, script);
                });
                
                // Disparar evento para que otros scripts sepan que el footer se ha cargado
                document.dispatchEvent(new Event('footerLoaded'));
            })
            .catch(error => console.error('Error cargando el footer:', error));
    }

    // Verificación para configurar temas y preferencias globales
    setupThemeAndPreferences();
});

// Función para inicializar eventos del navbar
function initNavbarEvents() {
    // Manejar el menú móvil si existe
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Manejar el menú de perfil si existe y no tiene ya listeners
    const perfilBtn = document.getElementById('perfil');
    const perfilMenu = document.getElementById('menu-perfil');
    
    if (perfilBtn && perfilMenu && !perfilBtn.hasAttribute('data-event-attached')) {
        perfilBtn.setAttribute('data-event-attached', 'true');
        
        perfilBtn.addEventListener('click', function(event) {
            event.preventDefault();
            perfilMenu.classList.toggle('hidden');
        });
        
        // Cerrar menú al hacer clic fuera
        document.addEventListener('click', function(event) {
            if (perfilBtn && perfilMenu) {
                if (!perfilBtn.contains(event.target) && !perfilMenu.contains(event.target)) {
                    perfilMenu.classList.add('hidden');
                }
            }
        });
    }
}

// Configuración de temas y preferencias globales
function setupThemeAndPreferences() {
    // Verificar preferencia de tema oscuro/claro del usuario
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    const storedTheme = localStorage.getItem("theme");
    
    if (storedTheme === "dark" || (!storedTheme && prefersDarkScheme.matches)) {
        document.body.classList.add("dark-theme");
    }
    
    // Configurar fecha actual para elementos que lo necesiten
    const dateElements = document.querySelectorAll('[data-display-date]');
    if (dateElements.length > 0) {
        const now = new Date();
        const options = { day: 'numeric', month: 'short', year: 'numeric' };
        const formattedDate = now.toLocaleDateString('es-ES', options);
        
        dateElements.forEach(el => {
            el.textContent = formattedDate;
        });
    }
}

// Exponer funciones útiles para los componentes cargados
window.componentUtils = {
    updateNavigation: function() {
        // Esta función será reemplazada por la versión en el navbar cuando se cargue
        console.log('La navegación aún no está disponible');
    },
    showToast: function(message, type = 'info', duration = 3000) {
        // Función para mostrar notificaciones Toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade-in fixed top-4 right-4 z-50 p-3 rounded-lg shadow-lg text-white text-sm`;
        
        // Establecer color de fondo según el tipo
        switch(type) {
            case 'success': 
                toast.style.backgroundColor = '#10B981'; 
                break;
            case 'error': 
                toast.style.backgroundColor = '#EF4444'; 
                break;
            case 'warning': 
                toast.style.backgroundColor = '#F59E0B'; 
                break;
            default: 
                toast.style.backgroundColor = '#3B82F6'; 
        }
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, duration);
    }
};

// Sistema de Mensajes/Notificaciones - Inicialización para carga dinámica
function initMensajesSystem() {
    var mensajesBtn = document.getElementById('mensajes-btn');
    var mensajesDropdown = document.getElementById('mensajes-dropdown');
    var mensajesBadge = document.getElementById('mensajes-badge');
    var mensajesLista = document.getElementById('mensajes-lista');
    var marcarTodosBtn = document.getElementById('marcar-todos-leidos');
    
    if (!mensajesBtn || !mensajesDropdown) {
        console.log('Sistema de mensajes: Elementos no encontrados en el DOM');
        return;
    }
    
    console.log('✅ Inicializando sistema de mensajes...');
    
    // Toggle dropdown
    mensajesBtn.addEventListener('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        mensajesDropdown.classList.toggle('hidden');
        
        // Si se abre el dropdown, cargar mensajes
        if (!mensajesDropdown.classList.contains('hidden')) {
            cargarMensajes();
        }
    });
    
    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', function(event) {
        if (!mensajesBtn.contains(event.target) && !mensajesDropdown.contains(event.target)) {
            mensajesDropdown.classList.add('hidden');
        }
    });
    
    // Marcar todos como leídos
    if (marcarTodosBtn) {
        marcarTodosBtn.addEventListener('click', function() {
            marcarTodosComoLeidos();
        });
    }
    
    // Cargar contador inicial
    actualizarContadorMensajes();
    
    // Actualizar cada 30 segundos
    setInterval(actualizarContadorMensajes, 30000);
}

function actualizarContadorMensajes() {
    var badge = document.getElementById('mensajes-badge');
    if (!badge) return;
    
    // Intentar obtener el contador desde la API
    fetch('/api/mensajes/count', {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(function(response) {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Error en la respuesta: ' + response.status);
    })
    .then(function(data) {
        var count = data.no_leidos || 0;
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.classList.remove('hidden');
            console.log('📊 Mensajes no leídos desde API:', count);
        } else {
            badge.classList.add('hidden');
        }
    })
    .catch(function(error) {
        console.warn('Error al obtener contador de mensajes, usando datos de prueba:', error);
        // Fallback: usar datos ficticios para testing
        var count = 3;
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.classList.remove('hidden');
            console.log('📊 Mensajes no leídos (fallback):', count);
        } else {
            badge.classList.add('hidden');
        }
    });
}

function cargarMensajes() {
    var mensajesLista = document.getElementById('mensajes-lista');
    if (!mensajesLista) return;
    
    // Mostrar loading
    mensajesLista.innerHTML = '<div class="flex items-center justify-center py-4"><i class="fas fa-spinner fa-spin mr-2"></i><span class="text-sm text-gray-500">Cargando...</span></div>';
    
    // Intentar cargar desde la API
    fetch('/api/mensajes', {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(function(response) {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Error en la respuesta: ' + response.status);
    })
    .then(function(data) {
        var mensajes = data.data || data || [];
        console.log('✅ Mensajes cargados desde API:', mensajes.length);
        mostrarMensajes(mensajes);
    })
    .catch(function(error) {
        console.warn('Error al cargar mensajes desde API, usando datos de prueba:', error);
        // Fallback: usar datos ficticios que simulan los mensajes del usuario
        setTimeout(function() {
            var mensajes = [
                {
                    "id": 22,
                    "titulo": "Bienvenido al Sistema de Mensajes",
                    "contenido": "Este es tu primer mensaje en el sistema",
                    "tipo": "sistema",
                    "prioridad": "normal",
                    "leido": false,
                    "fecha_creacion": "2025-07-21T20:00:00Z",
                    "nombre_emisor": "Sistema"
                },
                {
                    "id": 23,
                    "titulo": "Nueva función disponible",
                    "contenido": "Se ha añadido la función de chat en tiempo real",
                    "tipo": "notificacion",
                    "prioridad": "alta",
                    "leido": false,
                    "fecha_creacion": "2025-07-21T19:30:00Z",
                    "nombre_emisor": "Admin"
                },
                {
                    "id": 24,
                    "titulo": "Mantenimiento programado",
                    "contenido": "El sistema tendrá mantenimiento el fin de semana",
                    "tipo": "alerta",
                    "prioridad": "urgente",
                    "leido": false,
                    "fecha_creacion": "2025-07-21T19:00:00Z",
                    "nombre_emisor": "Sistema"
                }
            ];
            console.log('📊 Usando mensajes de fallback:', mensajes.length);
            mostrarMensajes(mensajes);
        }, 500);
    });
}

function mostrarMensajes(mensajes) {
    var mensajesLista = document.getElementById('mensajes-lista');
    if (!mensajesLista) return;
    
    if (mensajes.length === 0) {
        mensajesLista.innerHTML = '<div class="flex items-center justify-center py-8 text-gray-500"><i class="fas fa-inbox mr-2"></i><span class="text-sm">No hay mensajes</span></div>';
        return;
    }
    
    var html = '';
    mensajes.forEach(function(mensaje) {
        var fechaRelativa = formatearFechaRelativa(mensaje.fecha_creacion);
        var iconoTipo = getIconoTipoMensaje(mensaje.tipo);
        var colorPrioridad = getColorPrioridad(mensaje.prioridad);
        var fondoClase = mensaje.leido ? 'bg-white' : 'bg-blue-50 border-l-4 border-blue-400';
        
        html += '<div class="' + fondoClase + ' p-4 hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-100" onclick="abrirMensaje(' + mensaje.id + ')">';
        html += '<div class="flex items-start space-x-3">';
        html += '<div class="flex-shrink-0">';
        html += '<i class="' + iconoTipo + ' ' + colorPrioridad + ' text-sm"></i>';
        html += '</div>';
        html += '<div class="flex-1 min-w-0">';
        html += '<div class="flex items-center justify-between">';
        html += '<p class="text-sm font-medium text-gray-900 truncate" style="font-family: \'Inter\', -apple-system, BlinkMacSystemFont, sans-serif;">' + (mensaje.titulo || 'Sin título') + '</p>';
        if (!mensaje.leido) {
            html += '<span class="ml-2 inline-block w-2 h-2 bg-blue-500 rounded-full"></span>';
        }
        html += '</div>';
        html += '<p class="text-xs text-gray-500 mt-1" style="font-family: \'Inter\', -apple-system, BlinkMacSystemFont, sans-serif;">';
        html += (mensaje.nombre_emisor || 'Sistema') + ' • ' + fechaRelativa;
        html += '</p>';
        html += '</div>';
        html += '</div>';
        html += '</div>';
    });
    
    mensajesLista.innerHTML = html;
}

function getIconoTipoMensaje(tipo) {
    switch(tipo) {
        case 'sistema': return 'fas fa-cog';
        case 'alerta': return 'fas fa-exclamation-triangle';
        case 'notificacion': return 'fas fa-info-circle';
        default: return 'fas fa-envelope';
    }
}

function getColorPrioridad(prioridad) {
    switch(prioridad) {
        case 'urgente': return 'text-red-600';
        case 'alta': return 'text-orange-600';
        case 'normal': return 'text-blue-600';
        case 'baja': return 'text-gray-600';
        default: return 'text-blue-600';
    }
}

function formatearFechaRelativa(fechaStr) {
    var fecha = new Date(fechaStr);
    var ahora = new Date();
    var diff = Math.floor((ahora - fecha) / 1000);
    
    if (diff < 60) return 'ahora';
    if (diff < 3600) return Math.floor(diff / 60) + 'm';
    if (diff < 86400) return Math.floor(diff / 3600) + 'h';
    if (diff < 2592000) return Math.floor(diff / 86400) + 'd';
    return fecha.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
}

function abrirMensaje(mensajeId) {
    // Marcar como leído al abrir
    fetch('/api/mensajes/' + mensajeId + '/leido', {
        method: 'PATCH',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(function(response) {
        if (response.ok) {
            // Actualizar contador
            actualizarContadorMensajes();
            // Recargar mensajes
            cargarMensajes();
        }
    })
    .catch(function(error) {
        console.warn('Error al marcar mensaje como leído:', error);
    });
    
    // Redirigir a la página de mensajes (implementar más tarde)
    // window.location.href = '/admin/mensajes/' + mensajeId;
}

// Hacer la función global para que sea accesible desde el HTML
window.abrirMensaje = abrirMensaje;

function marcarTodosComoLeidos() {
    fetch('/api/mensajes/todos/leido', {
        method: 'PATCH',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(function(response) {
        if (response.ok) {
            actualizarContadorMensajes();
            cargarMensajes();
        }
    })
    .catch(function(error) {
        console.error('Error al marcar todos como leídos:', error);
    });
}