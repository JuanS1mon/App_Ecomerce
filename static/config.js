// Configuración de la tienda
const STORE_CONFIG = {
    name: 'Ecommerce Store',
    description: 'Tu tienda online de Puta Madre',
    logo: '/static/logo.svg',
    primaryColor: '#3B82F6',
    secondaryColor: '#1E40AF'
};

// Función para obtener el nombre de la tienda
function getStoreName() {
    return STORE_CONFIG.name;
}

// Función para actualizar el nombre de la tienda (útil para cambios dinámicos)
function setStoreName(newName) {
    STORE_CONFIG.name = newName;
    // Actualizar elementos DOM que usan el nombre de la tienda
    updateStoreNameInDOM();
}

// Función para actualizar elementos DOM con el nombre de la tienda
function updateStoreNameInDOM() {
    const storeNameElements = document.querySelectorAll('[data-store-name]');
    storeNameElements.forEach(element => {
        element.textContent = getStoreName();
    });

    // Actualizar títulos de página
    const titleElements = document.querySelectorAll('[data-store-title]');
    titleElements.forEach(element => {
        const baseTitle = element.getAttribute('data-store-title');
        document.title = `${baseTitle} - ${getStoreName()}`;
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    updateStoreNameInDOM();
});

// Ejemplo de uso:
// Para cambiar el nombre de la tienda desde la consola del navegador:
// setStoreName('Mi Tienda Online');
// O directamente modificando STORE_CONFIG.name = 'Nuevo Nombre';