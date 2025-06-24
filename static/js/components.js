/**
 * Sistema para cargar componentes dinámicamente
 * Este archivo se encarga de cargar los componentes HTML reutilizables
 * y gestionar su inicialización y actualización.
 */

// Estructura de la navegación - Define todas las rutas de la aplicación
const navigationItems = [
    { 
        path: '/index', 
        title: 'Inicio', 
        visible: true, 
        parent: null,
        icon: 'fa-home' 
    },
    {
        path: '/admin', 
        title: 'Panel Admin',
        visible: false,
        parent: '/index',
        redirect: '/admin',
        icon: 'fa-tachometer-alt'
    },
    {
        path: '/admin',
        title: 'Panel Admin', 
        visible: true,
        parent: '/index',
        icon: 'fa-tachometer-alt'
    },
    {
        path: '/usuarios_admin',
        title: 'Gestión de Usuarios',
        visible: true,
        parent: '/admin/page',
        icon: 'fa-users'
    },
    {
        path: '/usuarios_admin/page',
        title: 'Gestión de Usuarios',
        visible: true,
        parent: '/admin',
        icon: 'fa-users'
    },
    { 
        path: '/configdb', 
        title: 'Configuración DB', 
        visible: true, 
        parent: '/admin',
        icon: 'fa-database'
    },
    { 
        path: '/migraciones/admin_migraciones', 
        title: 'Migraciones', 
        visible: true, 
        parent: '/admin',
        icon: 'fa-exchange-alt'
    },
    { 
        path: '/generar', 
        title: 'Generar API', 
        visible: true, 
        parent: '/admin',
        icon: 'fa-code'
    },
    { 
        path: '/admin/perfil', 
        title: 'Perfil de Usuario', 
        visible: false,
        parent: '/admin/page',
        icon: 'fa-user'
    },
    { 
        path: '/docs', 
        title: 'Documentación API', 
        visible: true, 
        parent: null,
        icon: 'fa-book'
    },
    { 
        path: '/privacidad', 
        title: 'Política de Privacidad', 
        visible: false,
        parent: null,
        icon: 'fa-shield-alt'
    },
    { 
        path: '/terminos', 
        title: 'Términos y Condiciones', 
        visible: false,
        parent: null,
        icon: 'fa-file-contract'
    }
];

// Exponer globalmente para otras funciones
window.navigationItems = navigationItems;

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
 * Encuentra un elemento de navegación por su ruta
 * @param {string} path - La ruta a buscar
 * @returns {Object|null} - El elemento de navegación o null
 */
function findNavigationItem(path) {
    return navigationItems.find(item => item.path === path) || null;
}

/**
 * Función principal para cargar todos los componentes
 * Esta es la función que se llama desde las páginas HTML
 */
function loadComponents() {
    console.log("Iniciando carga de componentes...");
    
    // Cargar navbar si existe el contenedor
    if (document.getElementById('navbar-container')) {
        loadNavbar('navbar-container')
            .catch(error => console.error("Error cargando navbar:", error));
    }
    
    // Cargar footer si existe el contenedor
    if (document.getElementById('footer-container')) {
        loadFooter('footer-container')
            .catch(error => console.error("Error cargando footer:", error));
    }
}

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
            console.warn("Contenedor no encontrado:", containerId);
            resolve(false);
            return;
        }
        
        // Si ya está cargado, no hacer nada
        if (ComponentState.loaded.navbar) {
            console.log("Navbar ya cargado, omitiendo carga");
            resolve(true);
            return;
        }
        
        console.log("Intentando cargar navbar desde:", '/static/components/navbar.html');
        
        fetch('/static/components/navbar.html')
            .then(response => {
                if (!response.ok) throw new Error(`Error cargando navbar: ${response.status}`);
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
                
                console.log("Navbar cargado correctamente desde HTML");
                resolve(true);
            })
            .catch(error => {
                console.warn('Error cargando navbar desde HTML, generando en línea:', error);
                
                // Generar navbar en línea cuando falla la carga del archivo HTML
                generateInlineNavbar(container)
                    .then(() => {
                        ComponentState.loaded.navbar = true;
                        console.log("Navbar generado en línea correctamente");
                        resolve(true);
                    })
                    .catch(inlineError => {
                        console.error('Error generando navbar en línea:', inlineError);
                        reject(inlineError);
                    });
            });
    });
}

/**
 * Genera una barra de navegación en línea basada en navigationItems
 * @param {HTMLElement} container - Contenedor donde insertar el navbar
 * @returns {Promise<boolean>} - Promesa que se resuelve cuando se completa
 */
function generateInlineNavbar(container) {
    return new Promise((resolve, reject) => {
        try {
            getUserData().then(userData => {
                const currentPath = window.location.pathname;
                console.log("Generando navbar en línea para ruta:", currentPath);
                
                // Obtener el nombre e inicial del usuario
                const userName = userData ? (userData.nombre || userData.usuario || 'Usuario') : 'Usuario';
                const userInitial = userName.charAt(0).toUpperCase();
                
                // Comprobar si hay configuración explícita en la página
                const configNavItems = getPageNavConfig();
                const navItems = configNavItems || buildNavigationPath(currentPath);

                // Generar HTML de la barra de navegación
                let navigationHTML = '';
                navItems.forEach((item, index) => {
                    if (index > 0) {
                        navigationHTML += `<span class="text-gray-400">/</span>`;
                    }
                    
                    if (item.isLink) {
                        navigationHTML += `<a href="${item.path}" class="text-white text-lg font-semibold hover:text-gray-300">${item.title}</a>`;
                    } else {
                        navigationHTML += `<span class="text-white text-lg font-semibold">${item.title}</span>`;
                    }
                });
                
                // Determinar enlaces para la barra superior
                let topLinks = '';
                
                // Si estamos en una sección admin, mostrar enlaces admin
                if (currentPath.includes('/admin') || 
                    currentPath.includes('/usuarios_admin') || 
                    currentPath.includes('/configdb') || 
                    currentPath.includes('/migraciones') || 
                    currentPath.includes('/generar')) {
                    
                    topLinks = `
                        <a href="/docs" class="text-white hover:text-gray-300"><i class="fas fa-book mr-2"></i>Documentación</a>
                        <a href="/generar" class="text-white hover:text-gray-300"><i class="fas fa-code mr-2"></i>Generar API</a>
                        <a href="/migraciones/admin_migraciones" class="text-white hover:text-gray-300"><i class="fas fa-exchange-alt mr-2"></i>Migraciones</a>
                    `;
                } else {
                    topLinks = `
                        <a href="/docs" class="text-white hover:text-gray-300"><i class="fas fa-book mr-2"></i>Documentación</a>
                        <a href="/admin" class="text-white hover:text-gray-300"><i class="fas fa-tachometer-alt mr-2"></i>Panel Admin</a>
                    `;
                }
                
                // Generar HTML completo de la navbar
                const navbarHTML = `
                    <nav class="bg-gray-800 p-4 relative z-30">
                        <div class="container mx-auto flex justify-between items-center">
                            <div class="flex items-center space-x-4">
                                <a href="/index">
                                    <img src="/static/img/logo_mapache.gif" alt="Logo" class="h-8 w-auto" onerror="this.onerror=null; this.src='/static/img/logo.png';">
                                </a>
                                ${navigationHTML}
                            </div>
                            <div class="flex items-center space-x-4 relative">
                                ${topLinks}
                                <div class="relative">
                                    <button id="perfil" class="flex items-center focus:outline-none">
                                        <div class="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center text-white">
                                            ${userInitial}
                                        </div>
                                        <svg class="ml-2 w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.586l3.71-4.354a.75.75 0 011.14.976l-4.25 5A.75.75 0 0110 13a.75.75 0 01-.6-.3l-4.25-5a.75.75 0 01.08-1.06z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                    <div id="menu-perfil" class="hidden absolute right-0 mt-2 w-48 bg-gray-800 rounded-md shadow-lg z-50">
                                        <a href="/admin/perfil" class="block px-4 py-2 text-sm text-white hover:bg-gray-700">Perfil de usuario</a>
                                        <form action="/logout" method="post">
                                            <button type="submit" class="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-700">Logout</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </nav>
                `;
                
                container.innerHTML = navbarHTML;
                
                // Configurar interactividad del menú de perfil
                setTimeout(() => {
                    const perfilButton = document.getElementById('perfil');
                    const menuPerfil = document.getElementById('menu-perfil');
                    
                    if (perfilButton && menuPerfil) {
                        perfilButton.addEventListener('click', (e) => {
                            e.stopPropagation();
                            menuPerfil.classList.toggle('hidden');
                        });
                        
                        // Cerrar el menú al hacer clic en cualquier otra parte
                        document.addEventListener('click', () => {
                            menuPerfil.classList.add('hidden');
                        });
                    }
                }, 100);
                
                resolve(true);
            }).catch(error => {
                console.error("Error obteniendo datos de usuario para la navbar:", error);
                // Generar una navbar simple cuando hay error en los datos de usuario
                container.innerHTML = `
                    <nav class="bg-gray-800 p-4">
                        <div class="container mx-auto">
                            <a href="/index" class="text-white text-lg font-semibold">Inicio</a>
                        </div>
                    </nav>
                `;
                resolve(true);
            });
        } catch (error) {
            console.error("Error crítico generando navbar:", error);
            container.innerHTML = `
                <nav class="bg-gray-800 p-4">
                    <div class="container mx-auto">
                        <a href="/index" class="text-white text-lg font-semibold">Inicio</a>
                    </div>
                </nav>
            `;
            resolve(false);
        }
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
            eval(scriptCode); // Evaluar el código del script
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
        
        // Para desarrollo, usar un usuario simulado
        ComponentState.user = {
            id: 1,
            nombre: "Usuario",
            usuario: "admin",
            rol: "Administrador"
        };
        
        // Almacenar en localStorage para futuras referencias
        localStorage.setItem('user', JSON.stringify(ComponentState.user));
        
        resolve(ComponentState.user);
        
        // Descomenta el siguiente código para usar en producción
        /*
        // Solicitar al servidor usando la ruta correcta
        fetch('/usuarios/current') 
            .then(response => {
                if (!response.ok) {
                    if (response.status === 401 || response.status === 403) {
                        console.log('Usuario no autenticado o sin permisos');
                        return null;
                    }
                    throw new Error(`Error ${response.status}: No se pudo obtener información del usuario`);
                }
                return response.json();
            })
            .then(userData => {
                if (!userData) {
                    resolve(null);
                    return;
                }
                
                ComponentState.user = userData;
                localStorage.setItem('user', JSON.stringify(userData));
                console.log('Datos de usuario obtenidos:', userData);
                
                resolve(userData);
            })
            .catch(error => {
                console.error('Error obteniendo datos del usuario:', error);
                const cachedUser = localStorage.getItem('user');
                if (cachedUser) {
                    try {
                        const userData = JSON.parse(cachedUser);
                        console.log('Usando datos de usuario almacenados en caché');
                        resolve(userData);
                    } catch (e) {
                        localStorage.removeItem('user');
                        resolve(null);
                    }
                } else {
                    resolve(null);
                }
            });
        */
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
        
        // También actualizar elementos de visualización condicional basados en el rol
        const adminElements = document.querySelectorAll('[data-role="admin"]');
        const userElements = document.querySelectorAll('[data-role="user"]');
        
        // Mostrar/ocultar según el rol
        if (userData.rol === 'Administrador') {
            adminElements.forEach(el => el.classList.remove('hidden'));
            userElements.forEach(el => el.classList.add('hidden'));
        } else {
            adminElements.forEach(el => el.classList.add('hidden'));
            userElements.forEach(el => el.classList.remove('hidden'));
        }
    }).catch(err => {
        console.error('Error actualizando información de usuario:', err);
    });
}

/**
 * Construye la ruta de navegación basada en navigationItems
 * @param {string} currentPath - La ruta actual
 * @returns {Array} - Array de objetos de navegación
 */
function buildNavigationPath(currentPath) {
    console.log("Construyendo navegación para ruta:", currentPath);
    
    // Normalizar la ruta (eliminar barra final si existe)
    if (currentPath.endsWith('/') && currentPath.length > 1) {
        currentPath = currentPath.slice(0, -1);
    }
    
    // Array para los elementos de navegación
    let navItems = [];
    
    // Buscar coincidencia exacta en navigationItems
    let currentItem = findNavigationItem(currentPath);
    
    // Si no hay coincidencia exacta, buscar alternativas
    if (!currentItem) {
        // Probar sin /page
        const basePath = currentPath.replace(/\/page$/, '');
        currentItem = findNavigationItem(basePath);
        
        // Si aún no hay coincidencia, buscar por inicio de ruta
        if (!currentItem) {
            for (const item of navigationItems) {
                if (currentPath.startsWith(item.path + '/')) {
                    currentItem = item;
                    break;
                }
            }
        }
    }
    
    // Si encontramos el elemento, construir la navegación
    if (currentItem) {
        // Añadir Inicio como primer elemento
        navItems.push({
            title: 'Inicio',
            path: '/index',
            isLink: true
        });
        
        // Construir la cadena de padres
        let parents = [];
        let parent = currentItem;
        
        while (parent && parent.parent) {
            const parentItem = findNavigationItem(parent.parent);
            if (parentItem && parentItem.path !== '/index') { // No añadir 'Inicio' dos veces
                parents.unshift(parentItem); // Añadir al principio
            }
            parent = parentItem;
        }
        
        // Añadir todos los padres como enlaces
        parents.forEach(item => {
            navItems.push({
                title: item.title,
                path: item.path,
                isLink: true
            });
        });
        
        // Añadir el elemento actual como no enlace
        navItems.push({
            title: currentItem.title,
            path: currentPath, // Usar la ruta original para preservar el estado exacto
            isLink: false
        });
    } 
    // Si no se encontró coincidencia, usar el mecanismo de respaldo
    else {
        return detectNavigationPath(currentPath);
    }
    
    return navItems;
}

/**
 * Método de respaldo para detectar navegación cuando no hay coincidencia en navigationItems
 * @param {string} currentPath - La ruta actual
 * @returns {Array} - Array de objetos con la información de navegación
 */
function detectNavigationPath(currentPath) {
    console.log("Usando detección de navegación de respaldo para:", currentPath);
    
    // Array que contendrá los elementos de navegación
    let navItems = [];
    
    // Siempre añadir Inicio como primer elemento
    navItems.push({
        title: 'Inicio',
        path: '/index',
        isLink: true
    });
    
    // Mapa de rutas específicas con sus títulos
    const specificRoutes = {
        '/admin': 'Panel Admin',
        '/usuarios_admin': 'Gestión de Usuarios',
        '/usuarios_admin/page': 'Gestión de Usuarios',
        '/configdb': 'Configuración DB',
        '/migraciones/admin_migraciones': 'Migraciones',
        '/generar': 'Generar API',
        '/admin/perfil': 'Perfil de Usuario',
        '/docs': 'Documentación API'
    };
    
    // Mapa de subsecciones con sus padres
    const subsections = {
        '/usuarios_admin': '/admin',
        '/configdb': '/admin',
        '/migraciones/admin_migraciones': '/admin',
        '/generar': '/admin',
        '/admin/perfil': '/admin'
    };
    
    // Comprobar si es una ruta específica conocida
    if (specificRoutes[currentPath]) {
        // Si es una subsección, añadir su padre primero
        if (subsections[currentPath]) {
            const parentPath = subsections[currentPath];
            navItems.push({
                title: specificRoutes[parentPath],
                path: parentPath,
                isLink: true
            });
        }
        
        // Añadir la página actual
        navItems.push({
            title: specificRoutes[currentPath],
            path: currentPath,
            isLink: false
        });
    }
    // Si no está en rutas específicas, verificar por coincidencia parcial
    else {
        // Intentar encontrar coincidencias parciales (sin /page al final)
        const basePath = currentPath.replace(/\/page$/, '');
        const pagePath = basePath + '/page';
        
        if (specificRoutes[basePath]) {
            // Si existe la ruta base, usarla
            if (subsections[basePath]) {
                const parentPath = subsections[basePath];
                navItems.push({
                    title: specificRoutes[parentPath],
                    path: parentPath,
                    isLink: true
                });
            }
            
            navItems.push({
                title: specificRoutes[basePath],
                path: currentPath,
                isLink: false
            });
        }
        else if (specificRoutes[pagePath]) {
            // Si existe la versión con /page, usarla
            if (subsections[pagePath]) {
                const parentPath = subsections[pagePath];
                navItems.push({
                    title: specificRoutes[parentPath],
                    path: parentPath,
                    isLink: true
                });
            }
            
            navItems.push({
                title: specificRoutes[pagePath],
                path: currentPath,
                isLink: false
            });
        }
        // Detectar secciones comunes basadas en la URL
        else if (currentPath.includes('/admin') || 
            currentPath.includes('/usuarios_admin') ||
            currentPath.startsWith('/configdb') || 
            currentPath.startsWith('/migraciones/') || 
            currentPath.startsWith('/generar')) {
            
            navItems.push({
                title: 'Panel Admin',
                path: '/admin',
                isLink: true
            });
            
            // Identificar título específico según la URL
            let pageTitle = "Página Admin";
            
            if (currentPath.includes('/usuarios_admin')) {
                pageTitle = "Gestión de Usuarios";
            } else if (currentPath.includes('/configdb')) {
                pageTitle = "Configuración DB";
            } else if (currentPath.includes('/migraciones')) {
                pageTitle = "Migraciones";
            } else if (currentPath.includes('/generar')) {
                pageTitle = "Generar API";
            }
            
            navItems.push({
                title: pageTitle,
                path: currentPath,
                isLink: false
            });
        }
        // Otras páginas
        else {
            // Generar título a partir de la ruta
            const pathParts = currentPath.split('/').filter(part => part);
            let pageTitle = "Página";
            
            if (pathParts.length > 0) {
                const lastPart = pathParts[pathParts.length - 1];
                pageTitle = lastPart.charAt(0).toUpperCase() + 
                           lastPart.slice(1).replace(/_/g, ' ');
            }
            
            navItems.push({
                title: pageTitle,
                path: currentPath,
                isLink: false
            });
        }
    }
    
    return navItems;
}

/**
 * Genera navegación basada en un elemento de configuración en la página
 */
function getPageNavConfig() {
    const configElement = document.getElementById('page-config');
    if (configElement && configElement.dataset.navbarPath) {
        const pathString = configElement.dataset.navbarPath;
        const pathParts = pathString.split(' / ');
        
        const navItems = [];
        pathParts.forEach((part, index) => {
            const isLast = index === pathParts.length - 1;
            let path = '/';
            
            // Determinar la ruta según el título
            switch(part) {
                case 'Inicio': path = '/index'; break;
                case 'Panel Admin': path = '/admin'; break;
                case 'Gestión de Usuarios': path = '/usuarios_admin'; break;
                case 'Configuración DB': path = '/configdb'; break;
                case 'Migraciones': path = '/migraciones/admin_migraciones'; break;
                case 'Generar API': path = '/generar'; break;
                default: path = '#'; break;
            }
            
            navItems.push({
                title: part,
                path: path,
                isLink: !isLast
            });
        });
        
        return navItems;
    }
    
    return null;
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
            console.warn("Contenedor de footer no encontrado:", containerId);
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
                console.error('Error cargando footer, generando footer en línea:', error);
                
                // Generar un footer simple en línea
                container.innerHTML = `
                    <footer class="bg-gray-800 text-white py-6 mt-12">
                        <div class="container mx-auto px-4">
                            <div class="flex flex-col md:flex-row justify-between">
                                <div class="mb-4 md:mb-0">
                                    <h3 class="text-lg font-semibold mb-2">FastAPI Admin</h3>
                                    <p class="text-gray-400">Plataforma de administración para APIs</p>
                                </div>
                                <div>
                                    <h4 class="text-md font-semibold mb-2">Enlaces rápidos</h4>
                                    <ul class="space-y-1">
                                        <li><a href="/docs" class="text-gray-400 hover:text-white">Documentación API</a></li>
                                        <li><a href="/privacidad" class="text-gray-400 hover:text-white">Política de privacidad</a></li>
                                        <li><a href="/terminos" class="text-gray-400 hover:text-white">Términos y condiciones</a></li>
                                    </ul>
                                </div>
                            </div>
                            <div class="border-t border-gray-700 mt-6 pt-6 text-center text-gray-400 text-sm">
                                &copy; ${new Date().getFullYear()} FastAPI Admin. Todos los derechos reservados.
                            </div>
                        </div>
                    </footer>
                `;
                
                ComponentState.loaded.footer = true;
                resolve(true);
            });
    });
}

// Asegurarse de que la función loadComponents está disponible globalmente
window.loadComponents = loadComponents;

// Ejecutar loadComponents automáticamente cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    loadComponents();
});