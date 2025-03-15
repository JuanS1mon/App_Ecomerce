/**
 * Sistema para cargar componentes dinámicamente
 * Este archivo se encarga de cargar los componentes HTML reutilizables
 * y gestionar su inicialización y actualización.
 */

// Estado global de componentes
const ComponentState = {
    // Indica si cada componente ha sido cargado
    loaded: {
        navbar: false,
        footer: false
    },
    // Datos del usuario actual (almacenados en caché)
    user: null
};

/**
 * Carga el componente navbar
 * @param {string} containerId - ID del contenedor donde insertar el navbar
 * @param {Object} options - Opciones de configuración
 * @returns {Promise<boolean>} - Promesa que se resuelve cuando el navbar ha sido cargado
 */
function loadNavbar(containerId = 'navbar-container', options = {}) {
    return new Promise((resolve, reject) => {
        const container = document.getElementById(containerId);
        if (!container) {
            resolve(false);
            return;
        }
        
        // Si ya está cargado, no hacer nada
        if (ComponentState.loaded.navbar) {
            resolve(true);
            return;
        }
        
        fetch('/static/components/navbar.html')
            .then(response => {
                if (!response.ok) throw new Error('Error cargando navbar');
                return response.text();
            })
            .then(html => {
                container.innerHTML = html;
                
                // Ejecutar scripts en el navbar
                executeComponentScripts(container);
                
                // Actualizar con datos del usuario si están disponibles
                updateUserInfo();
                
                // Marcar como cargado
                ComponentState.loaded.navbar = true;
                
                // Si navigation.js está disponible, llamar a sus funciones
                if (window.Navigation && typeof window.Navigation.init === 'function') {
                    window.Navigation.init();
                }
                
                resolve(true);
            })
            .catch(error => {
                console.error('Error cargando navbar:', error);
                reject(error);
            });
    });
}

/**
 * Carga el componente footer
 * @param {string} containerId - ID del contenedor donde insertar el footer
 * @returns {Promise<boolean>} - Promesa que se resuelve cuando el footer ha sido cargado
 */
function loadFooter(containerId = 'footer-container') {
    return new Promise((resolve, reject) => {
        const container = document.getElementById(containerId);
        if (!container) {
            resolve(false);
            return;
        }
        
        // Si ya está cargado, no hacer nada
        if (ComponentState.loaded.footer) {
            resolve(true);
            return;
        }
        
        fetch('/static/components/footer.html')
            .then(response => {
                if (!response.ok) throw new Error('Error cargando footer');
                return response.text();
            })
            .then(html => {
                container.innerHTML = html;
                
                // Ejecutar scripts en el footer
                executeComponentScripts(container);
                
                // Marcar como cargado
                ComponentState.loaded.footer = true;
                
                resolve(true);
            })
            .catch(error => {
                console.error('Error cargando footer:', error);
                reject(error);
            });
    });
}

/**
 * Ejecuta los scripts contenidos dentro de un componente
 * @param {HTMLElement} container - El contenedor del componente
 */
function executeComponentScripts(container) {
    const scripts = container.getElementsByTagName('script');
    for (let i = 0; i < scripts.length; i++) {
        const script = scripts[i];
        const scriptCode = script.innerText || script.textContent;
        try {
            eval(scriptCode);
        } catch (e) {
            console.error('Error ejecutando script en componente:', e);
        }
    }
}

/**
 * Carga y obtiene los datos del usuario actual
 * @returns {Promise<Object>} - Promesa que resuelve con los datos del usuario
 */
function getUserData() {
    return new Promise((resolve, reject) => {
        // Si ya tenemos datos en caché, devolverlos
        if (ComponentState.user) {
            resolve(ComponentState.user);
            return;
        }
        
        // Intentar obtener de localStorage
        const cachedUser = localStorage.getItem('user');
        if (cachedUser) {
            try {
                ComponentState.user = JSON.parse(cachedUser);
                resolve(ComponentState.user);
                return;
            } catch (e) {
                // Si hay un error al parsear, continuar con la solicitud
                localStorage.removeItem('user');
            }
        }
        
        // Solicitar al servidor
        fetch('/api/user/current')
            .then(response => {
                if (!response.ok) {
                    throw new Error('No se pudo obtener información del usuario');
                }
                return response.json();
            })
            .then(userData => {
                // Almacenar en caché
                ComponentState.user = userData;
                localStorage.setItem('user', JSON.stringify(userData));
                resolve(userData);
            })
            .catch(error => {
                console.error('Error obteniendo datos del usuario:', error);
                resolve(null); // Resolver con null en lugar de rechazar
            });
    });
}

/**
 * Actualiza la información del usuario en los componentes
 */
function updateUserInfo() {
    getUserData().then(userData => {
        if (!userData) return;
        
        // Actualizar elementos de la UI que muestran información del usuario
        const userInitialElements = document.querySelectorAll('.user-initial, #user-initial');
        userInitialElements.forEach(element => {
            if (userData.nombre) {
                element.textContent = userData.nombre[0].toUpperCase();
            }
        });
        
        const userNameElements = document.querySelectorAll('.user-name, #user-name');
        userNameElements.forEach(element => {
            if (userData.nombre) {
                element.textContent = userData.nombre;
            }
        });
        
        const userRoleElements = document.querySelectorAll('.user-role, #user-role');
        userRoleElements.forEach(element => {
            if (userData.rol) {
                element.textContent = userData.rol;
            }
        });
    });
}

/**
 * Carga un componente personalizado desde una URL específica
 * @param {string} url - URL del componente a cargar
 * @param {string} containerId - ID del contenedor donde insertar el componente
 * @param {Object} data - Datos para pasar al componente
 * @returns {Promise<boolean>} - Promesa que se resuelve cuando el componente ha sido cargado
 */
function loadCustomComponent(url, containerId, data = null) {
    return new Promise((resolve, reject) => {
        const container = document.getElementById(containerId);
        if (!container) {
            resolve(false);
            return;
        }
        
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`Error cargando componente desde ${url}`);
                return response.text();
            })
            .then(html => {
                // Reemplazar marcadores de posición si hay datos
                if (data) {
                    Object.keys(data).forEach(key => {
                        const placeholder = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
                        html = html.replace(placeholder, data[key]);
                    });
                }
                
                container.innerHTML = html;
                
                // Ejecutar scripts en el componente
                executeComponentScripts(container);
                
                resolve(true);
            })
            .catch(error => {
                console.error(`Error cargando componente desde ${url}:`, error);
                reject(error);
            });
    });
}

/**
 * Muestra una notificación temporal
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de notificación (success, error, warning, info)
 * @param {number} duration - Duración en milisegundos
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Crear contenedor de notificaciones si no existe
    let container = document.getElementById('notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notifications-container';
        container.className = 'fixed top-4 right-4 z-50 flex flex-col space-y-2';
        document.body.appendChild(container);
    }
    
    // Crear la notificación
    const notification = document.createElement('div');
    notification.className = 'notification p-4 rounded shadow-lg transform transition-all duration-300 opacity-0 translate-x-full';
    
    // Añadir clases según el tipo
    switch (type) {
        case 'success':
            notification.classList.add('bg-green-500', 'text-white');
            break;
        case 'error':
            notification.classList.add('bg-red-500', 'text-white');
            break;
        case 'warning':
            notification.classList.add('bg-yellow-500', 'text-white');
            break;
        default:
            notification.classList.add('bg-blue-500', 'text-white');
    }
    
    // Añadir contenido
    notification.innerHTML = `
        <div class="flex items-center">
            <span class="mr-2">
                ${type === 'success' ? '✓' : type === 'error' ? '✗' : type === 'warning' ? '⚠' : 'ℹ'}
            </span>
            <span>${message}</span>
            <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Añadir al DOM
    container.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.classList.remove('opacity-0', 'translate-x-full');
    }, 10);
    
    // Configurar desaparición
    setTimeout(() => {
        notification.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

/**
 * Inicializa todos los componentes comunes de la página
 */
function initializeComponents() {
    // Cargar datos del usuario primero
    getUserData().then(() => {
        // Luego cargar componentes principales
        loadNavbar();
        loadFooter();
    });
}

// Inicializar componentes cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initializeComponents);

// Exportar funciones para uso desde otros scripts
window.Components = {
    loadNavbar,
    loadFooter,
    loadCustomComponent,
    getUserData,
    updateUserInfo,
    showNotification
};