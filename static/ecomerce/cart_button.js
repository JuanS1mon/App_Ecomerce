/**
 * Componente de botón genérico para agregar al carrito
 * Versión integrada con la clase Cart POO
 */

// Función global simplificada para agregar al carrito usando la clase Cart
window.addToCart = async function(productId, quantity = 1, price = 0) {
    // Usar la instancia global de Cart si existe
    if (window.cart && typeof window.cart.addProduct === 'function') {
        return await window.cart.addProduct(productId, quantity, price);
    }

    // Fallback: implementación directa si la clase Cart no está disponible
    try {
        // Obtener token JWT
        const token = getCookie('ecommerce_token') || sessionStorage.getItem('ecommerce_token') || localStorage.getItem('token') || localStorage.getItem('access_token');

        if (!token) {
            showToast('Debes iniciar sesión para agregar productos', 'error');
            return false;
        }

        // POST directo a la ruta simplificada
        const response = await fetch(`/ecomerce/carrito_items/simple?product_id=${productId}&quantity=${quantity}&price=${price}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            // Mensaje removido para experiencia más dinámica

            // Recargar el carrito si está visible
            if (window.cart && typeof window.cart.loadCart === 'function') {
                await window.cart.loadCart();
            }

            return true;
        } else if (response.status === 401) {
            showToast('Sesión expirada. Inicia sesión nuevamente.', 'error');
            document.cookie = 'ecommerce_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            sessionStorage.removeItem('ecommerce_token');
            localStorage.removeItem('token');
            localStorage.removeItem('access_token');
            return false;
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error al agregar producto', 'error');
            return false;
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showToast('Error de conexión', 'error');
        return false;
    }
};

// Función para crear botones de carrito
window.createCartButton = function(productId, quantity = 1, price = 0, buttonText = 'Agregar al Carrito', cssClass = 'btn-cart') {
    const button = document.createElement('button');
    button.className = cssClass;
    button.innerHTML = `<i class="fas fa-cart-plus mr-1"></i> ${buttonText}`;
    button.onclick = function() {
        addToCart(productId, quantity, price);
    };
    return button;
};

// Función para agregar botón de carrito a un elemento existente
window.addCartButtonToElement = function(elementId, productId, quantity = 1, price = 0, buttonText = 'Agregar al Carrito', cssClass = 'btn-cart') {
    const element = document.getElementById(elementId);
    if (element) {
        const button = createCartButton(productId, quantity, price, buttonText, cssClass);
        element.appendChild(button);
    }
};

// Función para inicializar botones de carrito en una página
window.initCartButtons = function() {
    // Buscar todos los elementos con data-cart-button
    const cartButtons = document.querySelectorAll('[data-cart-button]');

    cartButtons.forEach(element => {
        const productId = parseInt(element.dataset.productId);
        const quantity = parseInt(element.dataset.quantity) || 1;
        const price = parseFloat(element.dataset.price) || 0;

        if (productId && !element.onclick) {
            element.onclick = function() {
                addToCart(productId, quantity, price);
            };
        }
    });
};

// Función auxiliar para mostrar toast
function showToast(message, type = 'success') {
    // Usar la función global showToast si existe, sino alert
    if (typeof window.showToast === 'function' && window.showToast !== showToast) {
        window.showToast(message, type);
    } else {
        alert(message);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initCartButtons();
});