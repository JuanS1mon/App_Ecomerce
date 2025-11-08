/**
 * JavaScript para la tienda pública de productos
 */

// Variables globales
let allData = [];
let allCategories = [];

// Cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar eventos
    document.getElementById('search-input').addEventListener('input', filterProducts);
    document.getElementById('category-filter').addEventListener('change', function() {
        filterProducts();
    });
    document.getElementById('reset-search').addEventListener('click', resetSearch);

    // Las funciones loadCategories y fetchData se llamarán desde el HTML inline después de verificar auth
});

// Función para inicializar la tienda para usuarios autenticados
function initAuthenticatedStore() {
    if (typeof loadCategories === 'function') loadCategories();
    if (typeof fetchData === 'function') fetchData();
    // Solo inicializar carrito si no está ya inicializado
    if (window.cart && typeof window.cart.initCart === 'function' && !window.cart.isInitialized) {
        window.cart.initCart();
    }
}

// Función para inicializar la tienda para usuarios no autenticados
function initUnauthenticatedStore() {
    if (typeof loadCategories === 'function') loadCategories();
    if (typeof fetchData === 'function') fetchData();
}

/**
 * Carga las categorías disponibles desde el servidor
 */
async function loadCategories() {
    try {
        const response = await fetch('/ecomerce/api/categorias/publicas');

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const categories = await response.json();

        // Verificar si la respuesta es un array
        if (!Array.isArray(categories)) {
            console.error("La respuesta de categorías no es un array:", categories);
            return;
        }

        // Guardar categorías para filtrado
        allCategories = categories;

        // Llenar el select de categorías
        const categoryFilter = document.getElementById('category-filter');
        categoryFilter.innerHTML = '<option value="">Todas las categorías</option>';

        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.nombre;
            categoryFilter.appendChild(option);
        });

        // Habilitar el select después de cargar
        categoryFilter.disabled = false;

    } catch (error) {
        console.error("Error al cargar categorías:", error);
        // En caso de error, mostrar opción por defecto y habilitar
        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter) {
            categoryFilter.innerHTML = '<option value="">Todas las categorías</option>';
            categoryFilter.disabled = false;
        }
        // No mostrar toast para categorías, solo loggear el error
    }
}
async function fetchData() {
    try {
        const response = await fetch('/ecomerce/api/productos/publicos');

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();

        // Verificar si la respuesta es un array
        if (!Array.isArray(data)) {
            console.error("La respuesta no es un array:", data);
            showToast('Error al cargar los productos. La respuesta no tiene el formato esperado.', 'error');
            return;
        }

        // Guardar datos para filtrado
        allData = data;

        // Actualizar la UI
        updateProductsGrid(data);
        updateRecordCount(data.length);

        // Si hay filtros activos, reaplicar después de cargar productos
        const currentSearch = document.getElementById('search-input').value;
        const currentCategory = document.getElementById('category-filter').value;
        if (currentSearch || currentCategory) {
            filterProducts();
        }

    } catch (error) {
        console.error("Error al cargar productos:", error);
        showToast(`Error al cargar los productos: ${error.message}`, 'error');

        const grid = document.getElementById('products-grid');
        grid.innerHTML = `
            <div class="col-span-full text-center py-12">
                <i class="fas fa-exclamation-circle text-red-500 text-4xl mb-4"></i>
                <p class="text-red-500 text-lg">Error al cargar productos. Intente recargar la página.</p>
            </div>
        `;
    }
}

/**
 * Actualiza el grid con los productos proporcionados
 */
function updateProductsGrid(data) {
    const grid = document.getElementById('products-grid');
    grid.innerHTML = '';

    if (data.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full empty-state">
                <i class="fas fa-box-open empty-icon"></i>
                <p class="text-lg">No se encontraron productos disponibles</p>
            </div>
        `;
        return;
    }

    data.forEach((item) => {
        const card = document.createElement('div');
        card.className = 'product-card fade-in';

    const imageUrl = item.imagen_url || '/static/img/logo.png';
        const price = item.precio ? `$${item.precio.toLocaleString()}` : 'Precio no disponible';

        card.innerHTML = `
            <div class="product-image-container">
                <img src="${imageUrl}" alt="${item.nombre}" class="product-image" onerror="this.onerror=null; this.src='/static/img/logo.png'">
            </div>
            <div class="product-info">
                <h3 class="product-title">${item.nombre}</h3>
                <p class="product-description">${item.descripcion || 'Sin descripción'}</p>
                <div class="product-price">${price}</div>
                <div class="product-code">Código: ${item.codigo}</div>
                <div class="product-actions">
                    <button class="action-btn action-btn-primary" onclick="viewProduct(${item.id})">
                        <i class="fas fa-eye mr-1"></i> Ver Detalles
                    </button>
                    <button class="action-btn action-btn-secondary" onclick="addToCart(${item.id}, 1, ${item.precio || 0})">
                        <i class="fas fa-cart-plus mr-1"></i> Agregar al Carrito
                    </button>
                </div>
            </div>
        `;

        grid.appendChild(card);
    });
}

/**
 * Actualiza el contador de productos
 */
function updateRecordCount(count) {
    const recordCount = document.getElementById('record-count');
    recordCount.textContent = count === 1
        ? '1 producto disponible'
        : `${count} productos disponibles`;
}

/**
 * Actualiza el card de descripción de categoría
 */
function updateCategoryDescription(selectedCategoryId, filteredCount, totalCount) {
    const card = document.getElementById('category-description-card');
    const title = document.getElementById('category-title');
    const description = document.getElementById('category-description');
    const count = document.getElementById('category-product-count');

    if (!card || !title || !description || !count) {
        console.error('Elementos del card de categoría no encontrados');
        return;
    }

    if (!selectedCategoryId) {
        // Sin categoría seleccionada, ocultar el card
        card.classList.remove('show');
        card.classList.add('hidden');
        return;
    }

    // Buscar la categoría seleccionada
    if (!allCategories || allCategories.length === 0) {
        console.warn('allCategories no está disponible aún');
        card.classList.remove('show');
        card.classList.add('hidden');
        return;
    }

    const category = allCategories.find(cat => String(cat.id) === selectedCategoryId);
    if (!category) {
        card.classList.remove('show');
        card.classList.add('hidden');
        return;
    }

    // Actualizar contenido
    title.textContent = category.nombre;
    description.textContent = category.descripcion || 'Descubre nuestros productos de esta categoría.';

    // Actualizar contador
    if (filteredCount !== totalCount) {
        count.textContent = `Mostrando ${filteredCount} de ${totalCount} productos`;
    } else {
        count.textContent = `Mostrando ${totalCount} productos`;
    }

    // Mostrar el card
    card.classList.remove('hidden');
    card.classList.add('show');
}

/**
 * Filtra los productos según el texto de búsqueda y la categoría seleccionada
 */
function filterProducts() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const selectedCategoryId = document.getElementById('category-filter').value;

    // Verificar si los datos están cargados
    if (!allData || allData.length === 0) {
        return;
    }

    if (!searchTerm && !selectedCategoryId) {
        updateProductsGrid(allData);
        updateRecordCount(allData.length);
        updateCategoryDescription(selectedCategoryId, allData.length, allData.length);
        return;
    }

    const filteredData = allData.filter(item => {
        // Filtrar por texto de búsqueda
        const matchesSearch = !searchTerm ||
            String(item.nombre).toLowerCase().includes(searchTerm) ||
            String(item.descripcion).toLowerCase().includes(searchTerm) ||
            String(item.codigo).toLowerCase().includes(searchTerm);

        // Filtrar por categoría
        const matchesCategory = !selectedCategoryId ||
            (item.id_categoria !== null && item.id_categoria !== undefined && String(item.id_categoria) === selectedCategoryId);

        return matchesSearch && matchesCategory;
    });

    updateProductsGrid(filteredData);
    updateRecordCount(filteredData.length);
    updateCategoryDescription(selectedCategoryId, filteredData.length, allData.length);
}

/**
 * Restablece la búsqueda y el filtro de categorías
 */
function resetSearch() {
    document.getElementById('search-input').value = '';
    document.getElementById('category-filter').value = '';
    updateProductsGrid(allData);
    updateRecordCount(allData.length);
    updateCategoryDescription('', allData.length, allData.length);
}

/**
 * Muestra los detalles de un producto
 */
function viewProduct(id) {
    window.location.href = `/ecomerce/productos/detalle/${id}`;
}

/**
 * Agrega un producto al carrito
 */
function addToCart(productId, quantity = 1, price = 0) {
    if (window.addToCart) {
        window.addToCart(productId, quantity, price);
    } else {
        showToast('Cargando carrito...', 'info');
        // Reintentar después de un breve delay
        setTimeout(() => {
            if (window.addToCart) {
                window.addToCart(productId, quantity, price);
            } else {
                showToast('Error: Carrito no disponible. Recarga la página.', 'error');
            }
        }, 1000);
    }
}

/**
 * Muestra una notificación toast
 */
function showToast(message, type = 'success') {
    // Crear el elemento toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} slide-in`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="${type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;

    // Añadir al contenedor
    const container = document.getElementById('toast-container');
    container.appendChild(toast);

    // Eliminar después de 5 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 5000);
}

// Hacer showToast global para que otros scripts puedan usarla
window.showToast = showToast;

// Hacer las funciones globales para que el HTML inline pueda llamarlas
window.loadCategories = loadCategories;
window.fetchData = fetchData;
window.initAuthenticatedStore = initAuthenticatedStore;
window.initUnauthenticatedStore = initUnauthenticatedStore;

// Función de utilidad para verificar si las funciones están listas
window.checkFunctionsReady = function() {
  return typeof loadCategories === 'function' &&
         typeof fetchData === 'function' &&
         typeof updateProductsGrid === 'function' &&
         typeof updateRecordCount === 'function';
};