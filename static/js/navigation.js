/**
 * Sistema de navegación dinámica
 * Este archivo maneja la lógica de navegación y la actualización de componentes
 * basados en la ruta actual del usuario.
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
        title: 'Admin', 
        visible: true, 
        parent: '/index',
        icon: 'fa-cogs'
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
        visible: false,  // No se muestra en menú principal
        parent: '/admin',
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
        visible: false,  // No se muestra en menú principal
        parent: null,
        icon: 'fa-shield-alt'
    },
    { 
        path: '/terminos', 
        title: 'Términos y Condiciones', 
        visible: false,  // No se muestra en menú principal
        parent: null,
        icon: 'fa-file-contract'
    }
    // Puedes añadir más rutas aquí conforme las vayas creando
];

/**
 * Inicializa la navegación cuando se carga la página
 */
function initNavigation() {
    // Asegurarse de que el DOM está completamente cargado
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupNavigation);
    } else {
        setupNavigation();
    }
}

/**
 * Configura todos los elementos de navegación
 */
function setupNavigation() {
    updateBreadcrumb();
    highlightActiveLink();
    updatePageTitle();
    setupDropdownMenus();
}

/**
 * Actualiza la ruta de migas de pan basada en la URL actual
 */
function updateBreadcrumb() {
    const currentPath = window.location.pathname;
    const breadcrumbContainer = document.getElementById('breadcrumb-container');
    
    if (!breadcrumbContainer) return;

    // Encontrar el ítem de navegación actual
    const currentItem = findNavigationItem(currentPath);
    if (!currentItem) return;
    
    // Construir la cadena de migas de pan
    const breadcrumbs = [];
    let item = currentItem;
    
    // Agregar el ítem actual primero
    breadcrumbs.push(item);
    
    // Luego buscar todos los padres recursivamente
    while (item.parent) {
        const parentItem = findNavigationItem(item.parent);
        if (parentItem) {
            breadcrumbs.push(parentItem);
            item = parentItem;
        } else {
            break;
        }
    }
    
    // Invertir el array para mostrar desde el más general al más específico
    breadcrumbs.reverse();
    
    // Construir el HTML
    let breadcrumbHtml = '';
    breadcrumbs.forEach((item, index) => {
        if (index === breadcrumbs.length - 1) {
            // Último elemento (actual) - sin enlace
            breadcrumbHtml += `<span class="text-white font-semibold">${item.title}</span>`;
        } else {
            // Elementos anteriores - con enlace
            breadcrumbHtml += `<a href="${item.path}" class="text-gray-300 hover:text-white">${item.title}</a>`;
            breadcrumbHtml += `<span class="text-gray-500 mx-2">/</span>`;
        }
    });
    
    breadcrumbContainer.innerHTML = breadcrumbHtml;
}

/**
 * Encuentra un ítem de navegación basado en la ruta
 */
function findNavigationItem(path) {
    // Buscar coincidencia exacta
    let item = navigationItems.find(item => item.path === path);
    
    // Si no hay coincidencia exacta, buscar coincidencia parcial
    if (!item) {
        for (const navItem of navigationItems) {
            if (path.startsWith(navItem.path) && navItem.path !== '/index') {
                item = navItem;
                break;
            }
        }
    }
    
    // Si aún no hay coincidencia y no estamos en la raíz, usar la página de inicio
    if (!item && path !== '/') {
        item = navigationItems.find(item => item.path === '/index');
    }
    
    return item;
}

/**
 * Resalta el enlace activo en la barra de navegación
 */
function highlightActiveLink() {
    const currentPath = window.location.pathname;
    
    document.querySelectorAll('nav a').forEach(link => {
        const href = link.getAttribute('href');
        if (!href) return;
        
        // Resetear estilos primero
        link.classList.remove('active-link', 'border-b-2', 'border-white', 'font-bold');
        
        // Comprobar si la ruta actual coincide con este enlace
        if ((currentPath === href) || 
            (href !== '/index' && currentPath.startsWith(href))) {
            link.classList.add('active-link', 'border-b-2', 'border-white', 'font-bold');
        }
    });
}

/**
 * Actualiza el título de la página basado en la ruta actual
 */
function updatePageTitle() {
    const currentPath = window.location.pathname;
    const pageTitleElement = document.getElementById('page-title');
    
    if (!pageTitleElement) return;
    
    const currentItem = findNavigationItem(currentPath);
    if (currentItem) {
        pageTitleElement.textContent = currentItem.title;
        
        // También actualizar el título del documento
        document.title = `${currentItem.title} | SQL App`;
    }
}

/**
 * Configura los menús desplegables en la navegación
 */
function setupDropdownMenus() {
    const dropdownButtons = document.querySelectorAll('[data-dropdown]');
    
    dropdownButtons.forEach(button => {
        const targetId = button.getAttribute('data-dropdown');
        const dropdownMenu = document.getElementById(targetId);
        
        if (dropdownMenu) {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdownMenu.classList.toggle('hidden');
            });
        }
    });
    
    // Cerrar todos los dropdown al hacer clic en otra parte del documento
    document.addEventListener('click', () => {
        document.querySelectorAll('[id$="-dropdown"]').forEach(menu => {
            menu.classList.add('hidden');
        });
    });
}

/**
 * Genera un menú dinámico basado en la estructura de navegación
 * @param {string} containerId - ID del contenedor donde se insertará el menú
 * @param {string|null} parent - Ruta padre para filtrar ítems (null para raíz)
 */
function generateMenu(containerId, parent = null) {
    const menuContainer = document.getElementById(containerId);
    if (!menuContainer) return;
    
    const visibleItems = navigationItems.filter(item => 
        item.visible && item.parent === parent
    );
    
    if (visibleItems.length === 0) return;
    
    let menuHtml = '<ul class="menu-list">';
    
    visibleItems.forEach(item => {
        const hasChildren = navigationItems.some(child => child.parent === item.path);
        const iconHtml = item.icon ? `<i class="fas ${item.icon} mr-2"></i>` : '';
        
        if (hasChildren) {
            menuHtml += `
                <li class="menu-item has-submenu">
                    <a href="${item.path}" class="menu-link">
                        ${iconHtml}${item.title}
                        <i class="fas fa-chevron-down ml-2"></i>
                    </a>
                    <div class="submenu hidden">
                        <ul>`;
            
            // Añadir ítems hijos
            navigationItems.filter(child => child.visible && child.parent === item.path)
                .forEach(child => {
                    const childIconHtml = child.icon ? `<i class="fas ${child.icon} mr-2"></i>` : '';
                    menuHtml += `
                        <li>
                            <a href="${child.path}" class="submenu-link">
                                ${childIconHtml}${child.title}
                            </a>
                        </li>`;
                });
            
            menuHtml += `
                        </ul>
                    </div>
                </li>`;
        } else {
            menuHtml += `
                <li class="menu-item">
                    <a href="${item.path}" class="menu-link">
                        ${iconHtml}${item.title}
                    </a>
                </li>`;
        }
    });
    
    menuHtml += '</ul>';
    menuContainer.innerHTML = menuHtml;
    
    // Configurar interactividad para submenús
    document.querySelectorAll('.has-submenu').forEach(item => {
        const link = item.querySelector('.menu-link');
        const submenu = item.querySelector('.submenu');
        
        link.addEventListener('click', (e) => {
            if (window.innerWidth < 1024) {  // Solo en móvil/tablet
                e.preventDefault();
                submenu.classList.toggle('hidden');
            }
        });
    });
}

/**
 * Verifica los permisos del usuario para la página actual
 * @returns {boolean} true si tiene permisos, false en caso contrario
 */
function checkPagePermissions() {
    const currentPath = window.location.pathname;
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    
    // Si no hay datos de usuario, redirigir al login
    if (!userData.id) {
        // Solo redirigir si no estamos ya en la página de login
        if (!currentPath.includes('/login')) {
            window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
            return false;
        }
    }
    
    // Implementar aquí la lógica de verificación de permisos basada en roles
    // Por ahora devolvemos true para simplificar
    return true;
}

// Inicializar navegación al cargar la página
initNavigation();

// Exportar funciones para uso en otros archivos
window.Navigation = {
    init: initNavigation,
    updateBreadcrumb,
    highlightActiveLink,
    generateMenu,
    checkPagePermissions
};