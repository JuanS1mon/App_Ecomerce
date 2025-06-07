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