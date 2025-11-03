/**
 * JavaScript para la gestión del perfil de usuario
 * Incluye cambio de contraseña, pedidos, carrito y presupuestos
 */

// Variables globales
let currentUser = null;
let currentTab = 'perfil';

// Función para obtener token de autenticación
function getToken() {
    // Primero intentar desde cookies (prioridad para cross-tab sharing)
    let token = getCookie('ecommerce_token');
    if (token) return token;
    
    // Luego intentar desde sessionStorage
    token = sessionStorage.getItem('ecommerce_token');
    if (token) return token;
    
    // Fallback a localStorage y query params
    token = localStorage.getItem('access_token');
    if (token) return token;
    
    const urlParams = new URLSearchParams(window.location.search);
    token = urlParams.get('token');
    
    return token;
}

// Función helper para obtener cookies
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Headers para las peticiones
function getHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

// Inicialización cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Configurar navegación por tabs
    setupTabNavigation();

    // Configurar event listeners
    setupEventListeners();

    // Cargar datos iniciales
    loadProfileData();
});

/**
 * Configura la navegación por tabs
 */
function setupTabNavigation() {
    const tabs = ['perfil', 'password', 'pedidos', 'carrito', 'presupuestos'];

    tabs.forEach(tab => {
        const tabButton = document.getElementById(`tab-${tab}`);
        tabButton.addEventListener('click', () => switchTab(tab));
    });
}

/**
 * Cambia entre tabs
 */
function switchTab(tabName) {
    // Ocultar todos los contenidos
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.add('hidden'));

    // Remover clase activa de todos los tabs
    const tabs = document.querySelectorAll('[id^="tab-"]');
    tabs.forEach(tab => {
        tab.classList.remove('tab-active');
        tab.classList.add('tab-inactive');
    });

    // Mostrar contenido activo
    document.getElementById(`content-${tabName}`).classList.remove('hidden');

    // Activar tab seleccionado
    document.getElementById(`tab-${tabName}`).classList.remove('tab-inactive');
    document.getElementById(`tab-${tabName}`).classList.add('tab-active');

    currentTab = tabName;

    // Cargar datos específicos del tab si es necesario
    switch(tabName) {
        case 'pedidos':
            loadOrders();
            break;
        case 'carrito':
            loadCart();
            break;
        case 'presupuestos':
            loadBudgets();
            break;
    }
}

/**
 * Configura los event listeners
 */
function setupEventListeners() {
    // Formulario de perfil
    document.getElementById('profile-form').addEventListener('submit', updateProfile);

    // Formulario de cambio de contraseña
    document.getElementById('password-form').addEventListener('submit', changePassword);
}

/**
 * Carga los datos del perfil del usuario
 */
async function loadProfileData() {
    try {
        const response = await fetch('/ecomerce/usuarios/profile', {
            headers: getHeaders()
        });

        if (!response.ok) {
            if (response.status === 401) {
                showToast('Sesión expirada. Por favor, inicia sesión nuevamente.', 'error');
                // Redirigir al login si es necesario
                setTimeout(() => window.location.href = '/login', 2000);
                return;
            }
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        currentUser = data.user;

        // Poblar formulario de perfil
        populateProfileForm(data.user);

        // Actualizar contadores
        updateCounters(data);

        showToast('Perfil cargado correctamente', 'success');

    } catch (error) {
        console.error('Error al cargar perfil:', error);
        showToast(`Error al cargar perfil: ${error.message}`, 'error');
    }
}

/**
 * Pobla el formulario de perfil con los datos del usuario
 */
function populateProfileForm(user) {
    document.getElementById('nombre').value = user.nombre || '';
    document.getElementById('apellido').value = user.apellido || '';
    document.getElementById('email').value = user.email || '';
    document.getElementById('telefono').value = user.telefono || '';
    document.getElementById('direccion').value = user.direccion || '';
    document.getElementById('ciudad').value = user.ciudad || '';
    document.getElementById('provincia').value = user.provincia || '';
    document.getElementById('pais').value = user.pais || '';
    document.getElementById('cuit').value = user.cuit || '';
}

/**
 * Actualiza los contadores en los tabs
 */
function updateCounters(data) {
    if (data.orders_count !== undefined) {
        document.getElementById('pedidos-count').textContent =
            `${data.orders_count} ${data.orders_count === 1 ? 'pedido' : 'pedidos'}`;
    }

    if (data.budgets_count !== undefined) {
        document.getElementById('presupuestos-count').textContent =
            `${data.budgets_count} ${data.budgets_count === 1 ? 'presupuesto' : 'presupuestos'}`;
    }
}

/**
 * Actualiza el perfil del usuario
 */
async function updateProfile(event) {
    event.preventDefault();

    const submitBtn = document.getElementById('update-profile-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Actualizando...';

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch('/ecomerce/usuarios/profile', {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al actualizar perfil');
        }

        const result = await response.json();
        showToast('Perfil actualizado correctamente', 'success');

        // Actualizar datos locales
        currentUser = { ...currentUser, ...data };

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

/**
 * Cambia la contraseña del usuario
 */
async function changePassword(event) {
    event.preventDefault();

    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Validar que las contraseñas coincidan
    if (newPassword !== confirmPassword) {
        showToast('Las contraseñas no coinciden', 'error');
        return;
    }

    // Validar longitud mínima
    if (newPassword.length < 8) {
        showToast('La contraseña debe tener al menos 8 caracteres', 'error');
        return;
    }

    const submitBtn = document.getElementById('change-password-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Cambiando...';

    const data = {
        current_password: document.getElementById('current-password').value,
        new_password: newPassword
    };

    try {
        const response = await fetch('/ecomerce/usuarios/change-password', {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al cambiar contraseña');
        }

        // Limpiar formulario
        document.getElementById('password-form').reset();

        showToast('Contraseña cambiada correctamente', 'success');

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

/**
 * Carga los pedidos del usuario
 */
async function loadOrders() {
    try {
        const response = await fetch('/ecomerce/usuarios/pedidos/user', {
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const orders = await response.json();
        populateOrdersTable(orders);

    } catch (error) {
        console.error('Error al cargar pedidos:', error);
        showToast(`Error al cargar pedidos: ${error.message}`, 'error');
    }
}

/**
 * Pobla la tabla de pedidos
 */
function populateOrdersTable(orders) {
    const tbody = document.getElementById('pedidos-table-body');
    tbody.innerHTML = '';

    if (orders.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                    <i class="fas fa-shopping-bag mr-2"></i>
                    No tienes pedidos registrados
                </td>
            </tr>
        `;
        return;
    }

    orders.forEach(order => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';

        const statusClass = getStatusClass(order.estado);
        const formattedDate = new Date(order.fecha_pedido).toLocaleDateString('es-ES');

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                #${order.id}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formattedDate}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                $${parseFloat(order.total).toFixed(2)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusClass}">
                    ${order.estado}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${order.items_count || 0} items
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="viewOrderDetails(${order.id})" class="text-blue-600 hover:text-blue-900 mr-3">
                    <i class="fas fa-eye mr-1"></i>Ver Detalles
                </button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

/**
 * Carga el carrito activo del usuario
 */
async function loadCart() {
    try {
        const response = await fetch('/ecomerce/usuarios/carritos/active', {
            headers: getHeaders()
        });

        if (!response.ok) {
            if (response.status === 404) {
                showEmptyCart();
                return;
            }
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const cart = await response.json();
        populateCartContent(cart);

    } catch (error) {
        console.error('Error al cargar carrito:', error);
        showToast(`Error al cargar carrito: ${error.message}`, 'error');
    }
}

/**
 * Pobla el contenido del carrito
 */
function populateCartContent(cart) {
    const cartContent = document.getElementById('carrito-content');

    if (!cart || !cart.items || cart.items.length === 0) {
        showEmptyCart();
        return;
    }

    let html = `
        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-lg font-medium text-gray-900">Carrito #${cart.id}</h3>
                <span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusClass(cart.estado)}">
                    ${cart.estado}
                </span>
            </div>

            <div class="space-y-4 mb-6">
    `;

    cart.items.forEach(item => {
        html += `
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div class="flex items-center">
                    <img src="${item.producto.imagen_url || '/static/images/placeholder.png'}" alt="${item.producto.nombre}"
                         class="w-16 h-16 object-cover rounded-lg mr-4">
                    <div>
                        <h4 class="text-sm font-medium text-gray-900">${item.producto.nombre}</h4>
                        <p class="text-sm text-gray-500">Cantidad: ${item.cantidad}</p>
                        <p class="text-sm text-gray-500">Precio unitario: $${parseFloat(item.precio_unitario).toFixed(2)}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-sm font-medium text-gray-900">$${(item.cantidad * item.precio_unitario).toFixed(2)}</p>
                </div>
            </div>
        `;
    });

    html += `
            </div>

            <div class="border-t border-gray-200 pt-4">
                <div class="flex justify-between items-center text-lg font-semibold">
                    <span>Total:</span>
                    <span class="text-blue-600">$${parseFloat(cart.total).toFixed(2)}</span>
                </div>
                <div class="mt-4 flex justify-end space-x-3">
                    <a href="/carrito" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        <i class="fas fa-shopping-cart mr-2"></i>Ir al Carrito
                    </a>
                    <button onclick="checkoutCart(${cart.id})" class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                        <i class="fas fa-credit-card mr-2"></i>Proceder al Pago
                    </button>
                </div>
            </div>
        </div>
    `;

    cartContent.innerHTML = html;
}

/**
 * Muestra mensaje de carrito vacío
 */
function showEmptyCart() {
    const cartContent = document.getElementById('carrito-content');
    cartContent.innerHTML = `
        <div class="text-center py-12">
            <i class="fas fa-shopping-cart text-gray-300 text-6xl mb-4"></i>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Tu carrito está vacío</h3>
            <p class="text-gray-500 mb-6">¡Agrega algunos productos para comenzar!</p>
            <a href="/productos" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                <i class="fas fa-store mr-2"></i>Ir a Comprar
            </a>
        </div>
    `;
}

/**
 * Carga los presupuestos del usuario
 */
async function loadBudgets() {
    try {
        const response = await fetch('/ecomerce/usuarios/presupuestos/user', {
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const budgets = await response.json();
        populateBudgetsTable(budgets);

    } catch (error) {
        console.error('Error al cargar presupuestos:', error);
        showToast(`Error al cargar presupuestos: ${error.message}`, 'error');
    }
}

/**
 * Pobla la tabla de presupuestos
 */
function populateBudgetsTable(budgets) {
    const tbody = document.getElementById('presupuestos-table-body');
    tbody.innerHTML = '';

    if (budgets.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    <i class="fas fa-file-invoice-dollar mr-2"></i>
                    No tienes presupuestos registrados
                </td>
            </tr>
        `;
        return;
    }

    budgets.forEach(budget => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';

        const statusClass = getStatusClass(budget.estado);
        const formattedDate = new Date(budget.fecha_creacion).toLocaleDateString('es-ES');

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                #${budget.id}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${budget.nombre}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${budget.email}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${budget.telefono}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusClass}">
                    ${budget.estado}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formattedDate}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title="${budget.mensaje}">
                ${budget.mensaje}
            </td>
        `;

        tbody.appendChild(row);
    });
}

/**
 * Obtiene la clase CSS para el estado
 */
function getStatusClass(status) {
    const statusMap = {
        'pendiente': 'bg-yellow-100 text-yellow-800',
        'procesando': 'bg-blue-100 text-blue-800',
        'completado': 'bg-green-100 text-green-800',
        'cancelado': 'bg-red-100 text-red-800',
        'activo': 'bg-green-100 text-green-800',
        'inactivo': 'bg-gray-100 text-gray-800'
    };

    return statusMap[status.toLowerCase()] || 'bg-gray-100 text-gray-800';
}

/**
 * Muestra detalles de un pedido (placeholder)
 */
function viewOrderDetails(orderId) {
    showToast(`Funcionalidad de detalles del pedido #${orderId} próximamente`, 'success');
}

/**
 * Procede al checkout del carrito (placeholder)
 */
function checkoutCart(cartId) {
    showToast(`Redirigiendo al checkout del carrito #${cartId}...`, 'success');
    // Aquí iría la lógica para redirigir al checkout
    // window.location.href = `/checkout/${cartId}`;
}

/**
 * Muestra una notificación toast
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} slide-in`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="${type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;

    const container = document.getElementById('toast-container');
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 5000);
}