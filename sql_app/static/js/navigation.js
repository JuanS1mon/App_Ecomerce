// Estructura de la navegación - Define todas las rutas de la aplicación
// navigationItems se define en components.js para evitar conflictos
// Se accede a la variable global definida en components.js

/**
 * Encuentra un ítem de navegación basado en la ruta
 */
function findNavigationItem(path) {
    console.log("Buscando ítem de navegación para:", path);
    
    // Mapeo de rutas especiales
    const specialPathMapping = {
        '/admin': '/admin/page'
    };
    
    // Si es una ruta especial, usar su equivalente
    if (specialPathMapping[path]) {
        path = specialPathMapping[path];
        console.log("Ruta reasignada a:", path);
    }
    
    // 1. Buscar coincidencia exacta primero
    let item = navigationItems.find(item => item.path === path);
    if (item) {
        console.log("Encontrada coincidencia exacta:", item.title);
        return item;
    }
    
    // 2. Para rutas que comienzan con usuarios_admin, configurar manualmente
    if (path.startsWith('/usuarios_admin')) {
        item = navigationItems.find(item => item.path === '/usuarios_admin/page');
        if (item) {
            console.log("Ruta de usuarios_admin encontrada manualmente:", item.title);
            return item;
        }
    }
    
    // 3. Si es una subsección admin, intentar mapear a una subsección conocida
    if (path.includes('/admin/') || 
        path.includes('/configdb') || 
        path.includes('/migraciones') || 
        path.includes('/generar')) {
        
        // Ordenar los items por longitud de path para encontrar la coincidencia más específica
        const sortedItems = [...navigationItems]
            .filter(item => item.parent === '/admin/page')
            .sort((a, b) => b.path.length - a.path.length);
        
        for (const navItem of sortedItems) {
            if (path.includes(navItem.path)) {
                console.log("Encontrada coincidencia para subsección admin:", navItem.title);
                return navItem;
            }
        }
    }
    
    // 4. Buscar coincidencia parcial por longitud de ruta (más específica primero)
    const sortedItems = [...navigationItems].sort((a, b) => b.path.length - a.path.length);
    
    for (const navItem of sortedItems) {
        if (path.startsWith(navItem.path) && 
            navItem.path !== '/' && 
            navItem.path !== '/index') {
            
            console.log("Encontrada coincidencia parcial:", navItem.title);
            return navItem;
        }
    }
    
    // 5. Fallback a página de inicio
    item = navigationItems.find(item => item.path === '/index');
    if (item) {
        console.log("Usando página de inicio como fallback");
        return item;
    }
    
    console.warn("No se encontró ningún ítem de navegación para:", path);
    return null;
}

/**
 * Carga la barra de navegación
 */
function loadNavbar(containerId = 'navbar-container') {
    const navbarContainer = document.getElementById(containerId);
    if (!navbarContainer) return;
    
    // Obtener datos del usuario actual
    getUserData().then(userData => {
        const userName = userData ? (userData.nombre || userData.usuario || 'U') : 'U';
        const userInitial = userName.charAt(0).toUpperCase();
        
        // Determinar la ruta actual
        const currentPath = window.location.pathname;
        console.log("Cargando navbar para ruta:", currentPath);
        
        // Construir navegación jerárquica
        let navItems = [];
        
        // Añadir siempre Inicio
        navItems.push({
            title: 'Inicio',
            path: '/index',
            isLink: true
        });
        
        // Obtener el ítem actual
        let currentItem = findNavigationItem(currentPath);
        
        // Si es un ítem de la sección admin...
        if (currentItem && (
            currentPath.includes('/admin') || 
            currentPath.includes('/usuarios_admin') || 
            currentPath.includes('/configdb') || 
            currentPath.includes('/migraciones') || 
            currentPath.includes('/generar'))) {
            
            // Si no es la página principal de admin, mostrar "Panel Admin" como enlace intermedio
            if (currentPath !== '/admin' && currentPath !== '/admin/page') {
                const adminItem = navigationItems.find(item => item.path === '/admin/page');
                
                // Añadir Panel Admin como enlace intermedio
                if (adminItem) {
                    navItems.push({
                        title: adminItem.title,
                        path: adminItem.path,
                        isLink: true
                    });
                }
                
                // Añadir la página actual como texto (no enlace)
                navItems.push({
                    title: currentItem.title,
                    path: currentItem.path,
                    isLink: false
                });
            } 
            // Si es la página principal de admin, mostrarla como destino final
            else {
                navItems.push({
                    title: 'Panel Admin',
                    path: '/admin/page',
                    isLink: false
                });
            }
        }
        // Para otras secciones que no son admin
        else if (currentItem && currentItem.path !== '/index') {
            navItems.push({
                title: currentItem.title,
                path: currentItem.path,
                isLink: false
            });
        }
        
        // Generar HTML de navegación
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
        
        // Filtrar elementos para la barra superior (sección derecha)
        let topNavHTML = '';
        
        // Para las páginas de admin y subsecciones, mostrar los enlaces de subsecciones de admin
        if (currentPath.includes('/admin') || 
            currentPath.includes('/usuarios_admin') || 
            currentPath.includes('/configdb') || 
            currentPath.includes('/migraciones') || 
            currentPath.includes('/generar')) {
            
            // Mostrar enlaces a módulos admin
            const adminModules = navigationItems.filter(item => 
                item.visible && item.parent === '/admin/page'
            );
            
            adminModules.forEach(item => {
                const path = item.redirect || item.path;
                const icon = item.icon ? `<i class="fas ${item.icon} mr-2"></i>` : '';
                topNavHTML += `<a href="${path}" class="text-white hover:text-gray-300">${icon}${item.title}</a>`;
            });
        } 
        // Para otras páginas, mostrar enlaces de primer nivel
        else {
            const topItems = navigationItems.filter(item => 
                item.visible && item.parent === null && item.path !== '/index'
            );
            
            topItems.forEach(item => {
                const path = item.redirect || item.path;
                const icon = item.icon ? `<i class="fas ${item.icon} mr-2"></i>` : '';
                topNavHTML += `<a href="${path}" class="text-white hover:text-gray-300">${icon}${item.title}</a>`;
            });
        }
        
        // Asegurar que la documentación API siempre esté visible
        const docsItem = navigationItems.find(item => item.path === '/docs');
        if (docsItem && docsItem.visible && !topNavHTML.includes('/docs')) {
            const icon = docsItem.icon ? `<i class="fas ${docsItem.icon} mr-2"></i>` : '';
            // Insertar al principio
            topNavHTML = `<a href="/docs" class="text-white hover:text-gray-300">${icon}${docsItem.title}</a> ` + topNavHTML;
        }
        
        // HTML completo de la navbar
        const navbarHTML = `
            <nav class="bg-gray-800 p-4 relative z-30">
                <div class="container mx-auto flex justify-between items-center">
                    <div class="flex items-center space-x-4">
                        <a href="/index">
                            <img src="/static/img/logo_mapache.gif" alt="Logo" class="h-8 w-auto">
                        </a>
                        ${navigationHTML}
                    </div>
                    <div class="flex items-center space-x-4 relative">
                        ${topNavHTML}
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
        
        navbarContainer.innerHTML = navbarHTML;
        
        // Configurar interactividad del menú de perfil
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
    }).catch(error => {
        console.error('Error al cargar la navbar:', error);
        navbarContainer.innerHTML = `
            <nav class="bg-gray-800 p-4">
                <div class="container mx-auto">
                    <a href="/index" class="text-white text-lg font-semibold">Inicio</a>
                </div>
            </nav>
        `;
    });
}