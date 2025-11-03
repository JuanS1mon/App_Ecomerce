/**
 * Clase Cart - Programación Orientada a Objetos para manejar el carrito de compras
 */
class Cart {
    constructor() {
        this.currentCart = null;
        this.cartItems = [];
        this.userId = null;
        this.isLoading = false;
        this.isInitialized = false; // Bandera para evitar inicializaciones múltiples
        this.localCartKey = 'ecommerce_local_cart'; // Clave para localStorage

        // Elementos DOM
        this.elements = {
            sidebar: null,
            overlay: null,
            cartItems: null,
            emptyCart: null,
            cartFooter: null,
            cartTotal: null,
            cartCount: null
        };

        this.init();
    }

    /**
     * Inicializa la clase Cart
     */
    init() {
        // No cachear elementos DOM aquí - esperar a que estén disponibles
        this.bindEvents();

        // Cargar carrito local si existe (para usuarios no autenticados)
        this.loadLocalCart();

        // Inicializar carrito automáticamente
        this.initCart();
    }

    /**
     * Cachea los elementos del DOM para mejor rendimiento
     */
    cacheDOMElements() {
        this.elements.sidebar = document.getElementById('cart-sidebar');
        this.elements.overlay = document.getElementById('cart-overlay');
        this.elements.cartItems = document.getElementById('cart-items');
        this.elements.emptyCart = document.getElementById('empty-cart');
        this.elements.cartFooter = document.getElementById('cart-footer');
        this.elements.cartTotal = document.getElementById('cart-total');
        this.elements.cartCount = document.getElementById('cart-count');
    }

    /**
     * Vincula los eventos necesarios
     */
    bindEvents() {
        // No inicializar automáticamente - esperar a que se complete la autenticación
        // La inicialización se hará desde el script inline de la página
    }

    /**
     * Inicializa el carrito manualmente (llamado desde el script inline o automáticamente)
     */
    initCart() {
        if (this.isInitialized) {
            console.log('Carrito ya inicializado, omitiendo initCart()');
            return;
        }
        this.isInitialized = true;

        console.log('🛒 Inicializando carrito...');

        // Cachear elementos DOM ahora que deberían estar disponibles
        this.cacheDOMElements();
        console.log('Elementos DOM cacheados:', {
            sidebar: !!this.elements.sidebar,
            overlay: !!this.elements.overlay,
            cartItems: !!this.elements.cartItems
        });

        // Solo intentar cargar usuario y carrito si hay token disponible
        const token = this.getCookie('ecommerce_token') || sessionStorage.getItem('ecommerce_token');
        if (token) {
            console.log('Usuario tiene token, cargando carrito del servidor');
            // Usuario podría estar autenticado, intentar cargar carrito
            this.loadUserAndCart().catch(error => {
                console.warn('Error inicializando carrito:', error);
                this.renderEmptyCart();
            });
        } else {
            console.log('Usuario no autenticado - mostrando carrito vacío');
            // Usuario no autenticado - mostrar carrito vacío
            this.renderEmptyCart();
        }
    }

    /**
     * Carga el carrito y el carrito al inicializar
     */
    async loadUserAndCart() {
        if (this.isInitialized && this.userId) {
            // Si ya está inicializado y tenemos userId, no recargar
            return;
        }

        try {
            const currentUserId = await this.getCurrentUserId();
            if (currentUserId) {
                this.userId = currentUserId;
                // Usuario autenticado - cargar carrito del servidor
                await this.loadCart();
            } else {
                // Usuario no autenticado - mostrar carrito vacío
                console.log('Usuario no autenticado, mostrando carrito vacío');
                this.renderEmptyCart();
            }
        } catch (error) {
            console.error('Error loading user and cart:', error);
            // En caso de error, mostrar carrito vacío
            this.renderEmptyCart();
        }
    }

    /**
     * Alterna la visibilidad del carrito
     */
    toggle() {
        console.log('🛒 Toggle del carrito llamado');

        // Asegurar que los elementos DOM estén cacheados
        if (!this.elements.sidebar || !this.elements.overlay) {
            console.log('Elementos no cacheados, intentando cachearlos...');
            this.cacheDOMElements();
        }

        if (!this.elements.sidebar || !this.elements.overlay) {
            console.error('❌ Cart elements not found after caching attempt');
            console.log('Elementos disponibles:', {
                sidebar: this.elements.sidebar,
                overlay: this.elements.overlay
            });
            return;
        }

        const isOpen = !this.elements.sidebar.classList.contains('translate-x-full');
        console.log(`Carrito está ${isOpen ? 'abierto' : 'cerrado'}`);

        if (isOpen) {
            console.log('Cerrando carrito');
            // Cerrar carrito
            this.elements.sidebar.classList.add('translate-x-full');
            this.elements.overlay.classList.add('hidden');
        } else {
            console.log('Abriendo carrito');
            // Abrir carrito - siempre recargar para asegurar datos actualizados
            this.elements.sidebar.classList.remove('translate-x-full');
            this.elements.overlay.classList.remove('hidden');

            // Forzar recarga cuando se abre el carrito para asegurar datos actualizados
            this.loadCart(true);
        }
    }

    /**
     * Carga el carrito del usuario
     */
    async loadCart(forceReload = false) {
        if (this.isLoading) return;

        // Si ya tenemos datos del carrito y no ha pasado mucho tiempo, evitar recarga
        // Pero permitir recarga forzada (útil después de agregar productos)
        if (!forceReload && this.currentCart && this.cartItems.length >= 0) {
            // Opcional: podríamos agregar un timestamp para recargar después de cierto tiempo
            // console.log('Carrito ya cargado, usando datos en caché');
            return;
        }

        // Si no hay usuario autenticado, no intentar cargar del servidor
        if (!this.userId) {
            console.log('No hay usuario autenticado, mostrando carrito vacío');
            this.renderEmptyCart();
            return;
        }

        try {
            this.isLoading = true;
            console.log(`Cargando carrito para usuario ${this.userId}...`);

            // Obtener carrito activo
            const token = this.getCookie('ecommerce_token') || sessionStorage.getItem('ecommerce_token');
            const cartResponse = await fetch(`/ecomerce/carritos/activo/${this.userId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                }
            });

            console.log(`Respuesta del carrito: ${cartResponse.status}`);

            if (cartResponse.ok) {
                this.currentCart = await cartResponse.json();
                console.log(`✅ Carrito activo cargado: ID ${this.currentCart.id} para usuario ${this.userId}`);

                // Obtener items del carrito
                const itemsResponse = await fetch(`/ecomerce/carrito_items/carrito/${this.currentCart.id}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                console.log(`Respuesta de items del carrito: ${itemsResponse.status}`);

                if (itemsResponse.ok) {
                    this.cartItems = await itemsResponse.json();
                    console.log(`✅ Items del carrito cargados: ${this.cartItems.length} items en carrito ${this.currentCart.id}`);

                    // Cargar información completa de los productos
                    await this.loadProductDetails();

                    this.render();
                } else {
                    const errorText = await itemsResponse.text();
                    console.error('❌ Error cargando items del carrito:', errorText);
                    throw new Error('Error al cargar los items del carrito');
                }
            } else if (cartResponse.status === 404) {
                // No hay carrito activo, crear uno nuevo
                console.log('No hay carrito activo, creando uno nuevo...');
                this.currentCart = null;
                this.cartItems = [];
                this.renderEmptyCart();
            } else {
                const errorText = await cartResponse.text();
                console.error('❌ Error cargando carrito:', cartResponse.status, errorText);
                throw new Error('Error al cargar el carrito');
            }
        } catch (error) {
            console.error('❌ Error en loadCart:', error);
            this.renderEmptyCart();
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Renderiza el carrito completo
     */
    render() {
        // console.log(`Renderizando carrito con ${this.cartItems.length} items`);

        // Verificar que todos los elementos necesarios existan
        if (!this.elements.cartItems || !this.elements.emptyCart || !this.elements.cartFooter ||
            !this.elements.cartTotal || !this.elements.cartCount) {
            // console.warn('Algunos elementos del DOM del carrito no están disponibles, intentando cachearlos nuevamente');
            this.cacheDOMElements();

            // Si aún no existen, salir
            if (!this.elements.cartItems || !this.elements.emptyCart || !this.elements.cartFooter ||
                !this.elements.cartTotal || !this.elements.cartCount) {
                // console.error('No se pueden renderizar los elementos del carrito - DOM no disponible');
                return;
            }
        }

        if (this.cartItems.length === 0) {
            // console.log('Carrito vacío, renderizando estado vacío');
            this.renderEmptyCart();
            return;
        }

        // Mostrar items del carrito
        this.elements.emptyCart.style.display = 'none';
        this.elements.cartFooter.style.display = 'block';

        let total = 0;
        let itemCount = 0;

        this.elements.cartItems.innerHTML = this.cartItems.map(item => {
            const itemTotal = item.cantidad * item.precio_unitario;
            total += itemTotal;
            itemCount += item.cantidad;

            // Construir información de variante
            let variantDisplay = '';
            if (item.variant_info) {
                const variantParts = [];
                if (item.variant_info.color) variantParts.push(`Color: ${item.variant_info.color}`);
                if (item.variant_info.tipo) variantParts.push(`Tipo: ${item.variant_info.tipo}`);
                if (variantParts.length > 0) {
                    variantDisplay = `<p class="text-xs text-blue-600 font-medium">${variantParts.join(' • ')}</p>`;
                }
            }

            // Usar imagen normal pero optimizada para el carrito (tamaño pequeño)
            const cartImage = item.product_image || '/static/img/logo.png';

            return `
                <div class="flex items-center space-x-4 bg-white p-4 rounded-lg shadow-sm mb-4" data-item-id="${item.id}">
                    <img src="${cartImage}" alt="${item.product_name}" class="w-12 h-12 object-cover rounded" onerror="this.src='/static/img/logo.png'">
                    <div class="flex-1">
                        <h3 class="font-semibold text-gray-800 text-sm">${item.product_name}</h3>
                        ${variantDisplay}
                        <p class="text-xs text-gray-500">${item.product_codigo}</p>
                        <p class="text-sm text-gray-600">Precio: $${this.formatPrice(item.precio_unitario)}</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button class="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-sm" onclick="updateQuantity(${item.id}, ${item.cantidad - 1})">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span class="font-semibold text-sm">${item.cantidad}</span>
                        <button class="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-sm" onclick="updateQuantity(${item.id}, ${item.cantidad + 1})">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <div class="text-right">
                        <p class="font-semibold text-sm">$${this.formatPrice(itemTotal)}</p>
                        <button class="text-red-500 hover:text-red-700 text-sm" onclick="removeItem(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        this.elements.cartTotal.textContent = `$${this.formatPrice(total)}`;
        this.elements.cartCount.textContent = itemCount;

        // Actualizar también el contador global del carrito
        this.updateGlobalCartCount(itemCount);

        // console.log(`Carrito renderizado: ${itemCount} items, total $${total}`);
    }

    /**
     * Renderiza el carrito vacío
     */
    renderEmptyCart() {
        // console.log('Renderizando carrito vacío');

        if (!this.elements.emptyCart || !this.elements.cartFooter || !this.elements.cartCount) {
            // console.warn('Elementos del DOM para carrito vacío no disponibles, intentando cachearlos nuevamente');
            this.cacheDOMElements();

            if (!this.elements.emptyCart || !this.elements.cartFooter || !this.elements.cartCount) {
                // console.error('No se puede renderizar carrito vacío - DOM no disponible');
                return;
            }
        }

        this.elements.emptyCart.style.display = 'block';
        this.elements.cartFooter.style.display = 'none';
        this.elements.cartCount.textContent = '0';

        // Limpiar el contenido de items del carrito
        if (this.elements.cartItems) {
            this.elements.cartItems.innerHTML = '';
        }

        this.updateGlobalCartCount(0);
        // console.log('Carrito vacío renderizado correctamente');
    }

    /**
     * Agrega un producto al carrito
     */
    async addProduct(productId, quantity = 1, price = 0, variantData = null) {
        // Verificar si hay token disponible
        const token = this.getCookie('ecommerce_token') || sessionStorage.getItem('ecommerce_token');
        if (!token) {
            // Usuario no autenticado - redirigir al login
            console.log('Usuario no autenticado, redirigiendo al login');
            window.location.href = '/ecommerce/login?next=' + encodeURIComponent(window.location.pathname);
            return false;
        }

        try {
            if (!this.userId) {
                this.userId = await this.getCurrentUserId();
                if (!this.userId) {
                    // Si aún no hay userId después de intentar obtenerlo, redirigir al login
                    window.location.href = '/ecommerce/login?next=' + encodeURIComponent(window.location.pathname);
                    return false;
                }
            }

            // Usar la ruta simple que crea carrito automáticamente si no existe
            const response = await fetch(`/ecomerce/carrito_items/simple`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getCookie('ecommerce_token') || sessionStorage.getItem('ecommerce_token')}`,
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity,
                    price: price,
                    variant_data: variantData
                })
            });

            if (response.ok) {
                const result = await response.json();

                // Actualización optimizada: solo incrementar contador sin recargar todo el carrito
                // La recarga completa se hará cuando el usuario abra el carrito
                const currentCount = parseInt((this.elements.cartCount || document.getElementById('cart-count'))?.textContent || '0');
                this.updateGlobalCartCount(currentCount + quantity);

                return true;
            } else if (response.status === 401) {
                sessionStorage.removeItem('ecommerce_token');
                sessionStorage.removeItem('ecommerce_user_id');
                this.deleteCookie('ecommerce_token');
                // Redirigir al login
                window.location.href = '/ecommerce/login?next=' + encodeURIComponent(window.location.pathname);
                return false;
            } else {
                const error = await response.json();
                console.error('Error agregando producto al carrito:', error);
                return false;
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            // En caso de error de red, redirigir al login
            window.location.href = '/ecommerce/login?next=' + encodeURIComponent(window.location.pathname);
            return false;
        }
    }

    /**
     * Agrega un producto al carrito local (localStorage)
     */
    addToLocalCart(productId, quantity = 1, price = 0, variantData = null) {
        try {
            // Cargar carrito local actual
            let localCart = this.loadLocalCart();

            // Buscar si el producto ya existe
            const existingItem = localCart.find(item =>
                item.product_id === productId &&
                JSON.stringify(item.variant_data) === JSON.stringify(variantData)
            );

            if (existingItem) {
                // Incrementar cantidad si ya existe
                existingItem.quantity += quantity;
            } else {
                // Agregar nuevo item
                localCart.push({
                    product_id: productId,
                    quantity: quantity,
                    price: price,
                    variant_data: variantData,
                    added_at: new Date().toISOString()
                });
            }

            // Guardar carrito local
            this.saveLocalCart(localCart);

            // Actualizar contador global
            const totalQuantity = localCart.reduce((sum, item) => sum + item.quantity, 0);
            this.updateGlobalCartCount(totalQuantity);

            return true;
        } catch (error) {
            console.error('Error agregando al carrito local:', error);
            return false;
        }
    }

    /**
     * Actualiza la cantidad de un item del carrito
     */
    async updateQuantity(itemId, newQuantity) {
        if (this.isLoading) return;

        try {
            if (newQuantity <= 0) {
                await this.removeItem(itemId);
                return;
            }

            // Verificar si es un item local
            if (itemId.toString().startsWith('local_')) {
                this.updateLocalQuantity(itemId, newQuantity);
                return;
            }

            this.isLoading = true;
            console.log(`Actualizando cantidad del item ${itemId} a ${newQuantity}`);

            const token = this.getCookie('ecommerce_token') || sessionStorage.getItem('ecommerce_token');
            const response = await fetch(`/ecomerce/carrito_items/id/${itemId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    cantidad: newQuantity
                })
            });

            if (response.ok) {
                const updatedItem = await response.json();
                console.log(`✅ Item ${itemId} actualizado a cantidad ${newQuantity}`);

                // Actualizar el item en la lista local
                const itemIndex = this.cartItems.findIndex(item => item.id === itemId);
                if (itemIndex !== -1) {
                    this.cartItems[itemIndex].cantidad = newQuantity;
                    this.render();
                }

                // Mostrar mensaje de éxito
                console.log('Cantidad actualizada exitosamente');
            } else {
                const errorText = await response.text();
                console.error('❌ Error actualizando cantidad:', response.status, errorText);
                throw new Error('Error al actualizar la cantidad');
            }
        } catch (error) {
            console.error('❌ Error en updateQuantity:', error);
            throw error;
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Remueve un item del carrito
     */
    async removeItem(itemId) {
        // Verificar si es un item local
        if (itemId.toString().startsWith('local_')) {
            this.removeLocalItem(itemId);
            return;
        }

        try {
            // console.log(`Intentando eliminar item ${itemId}`);

            const response = await fetch(`/ecomerce/carrito_items/id/${itemId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.getCookie('ecommerce_token') || sessionStorage.getItem('ecommerce_token')}`,
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                // console.log(`Item ${itemId} eliminado exitosamente del backend`);

                // Remover el item de la lista local inmediatamente
                const itemIndex = this.cartItems.findIndex(item => item.id === itemId);
                if (itemIndex !== -1) {
                    this.cartItems.splice(itemIndex, 1);
                    // console.log(`Item ${itemId} removido de la lista local`);
                }

                // Re-renderizar el carrito con los items actualizados
                this.render();

                // Mensaje removido para experiencia más dinámica
                // console.log('Carrito re-renderizado después de eliminar item');
            } else {
                // console.error(`Error en respuesta del servidor: ${response.status}`);
                throw new Error('Error al remover producto');
            }
        } catch (error) {
            console.error('Error removing item:', error);
        }
    }

    /**
     * Actualiza la cantidad de un item local del carrito
     */
    updateLocalQuantity(itemId, newQuantity) {
        try {
            // Cargar carrito local
            let localCart = this.loadLocalCart();

            // Encontrar el item por ID temporal
            const itemIndex = this.cartItems.findIndex(item => item.id === itemId);
            if (itemIndex !== -1) {
                const productId = this.cartItems[itemIndex].id_producto;

                // Encontrar en localCart
                const localItemIndex = localCart.findIndex(item => item.product_id === productId);
                if (localItemIndex !== -1) {
                    if (newQuantity <= 0) {
                        // Remover si cantidad es 0 o menor
                        localCart.splice(localItemIndex, 1);
                        this.cartItems.splice(itemIndex, 1);
                    } else {
                        // Actualizar cantidad
                        localCart[localItemIndex].quantity = newQuantity;
                        this.cartItems[itemIndex].cantidad = newQuantity;
                    }

                    this.saveLocalCart(localCart);
                    this.render();
                }
            }
        } catch (error) {
            console.error('Error actualizando cantidad local:', error);
        }
    }

    /**
     * Remueve un item local del carrito
     */
    removeLocalItem(itemId) {
        try {
            // Cargar carrito local
            let localCart = this.loadLocalCart();

            // Encontrar el item por ID temporal
            const itemIndex = this.cartItems.findIndex(item => item.id === itemId);
            if (itemIndex !== -1) {
                const productId = this.cartItems[itemIndex].id_producto;

                // Remover de localCart
                const localItemIndex = localCart.findIndex(item => item.product_id === productId);
                if (localItemIndex !== -1) {
                    localCart.splice(localItemIndex, 1);
                    this.saveLocalCart(localCart);

                    // Remover de cartItems
                    this.cartItems.splice(itemIndex, 1);
                    this.render();
                }
            }
        } catch (error) {
            console.error('Error removiendo item local:', error);
        }
    }

    /**
     * Obtiene el ID del usuario actual
     */
    async getCurrentUserId() {
        // Primero intentar obtener del sessionStorage (cache)
        const storedUserId = sessionStorage.getItem('ecommerce_user_id');
        if (storedUserId) {
            return parseInt(storedUserId);
        }

        // Si no está en sessionStorage, hacer petición al backend para obtener usuario actual
        const token = this.getCookie('ecommerce_token') || sessionStorage.getItem('ecommerce_token');

        if (!token) {
            // console.log('No hay token disponible - usuario no autenticado');
            return null;
        }

        try {
            // Hacer petición a /ecommerce/auth/me para obtener información del usuario
            const response = await fetch('/ecommerce/auth/me', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                const userData = await response.json();

                // Guardar el userId en sessionStorage y cookies para futuras peticiones
                if (userData.id) {
                    sessionStorage.setItem('ecommerce_user_id', userData.id.toString());
                    // También guardar en cookies para consistencia cross-tab
                    document.cookie = `ecommerce_user_id=${userData.id}; path=/; max-age=86400`; // 24 horas
                    return userData.id;
                } else {
                    console.error('Respuesta de /ecommerce/auth/me no contiene campo "id"');
                    return null;
                }
            } else if (response.status === 401) {
                console.warn('Token ecommerce inválido o expirado');
                // Limpiar token inválido de ambos storage
                sessionStorage.removeItem('ecommerce_token');
                sessionStorage.removeItem('ecommerce_user_id');
                this.deleteCookie('ecommerce_token');
                this.deleteCookie('ecommerce_user_id');
                return null;
            } else {
                console.error(`Error en petición a /ecommerce/auth/me: ${response.status}`);
                return null;
            }

        } catch (error) {
            console.error('Error obteniendo usuario ecommerce actual:', error);
            return null;
        }
    }

    /**
     * Actualiza el contador global del carrito
     */
    updateGlobalCartCount(count) {
        // Buscar el contador de la navbar (prioridad alta)
        const navbarCartCount = document.getElementById('cart-count');
        if (navbarCartCount) {
            navbarCartCount.textContent = count;
        }

        // También actualizar el contador del sidebar si existe
        if (this.elements.cartCount && this.elements.cartCount !== navbarCartCount) {
            this.elements.cartCount.textContent = count;
        }
    }

    /**
     * Formatea un precio con decimales
     */
    formatPrice(price) {
        return parseFloat(price).toFixed(2);
    }

    /**
     * Carga la información completa de los productos en el carrito
     */
    async loadProductDetails() {
        if (!this.cartItems || this.cartItems.length === 0) return;

        try {
            // Obtener información de todos los productos en paralelo
            const productPromises = this.cartItems.map(async (item) => {
                try {
                    const response = await fetch(`/ecomerce/productos/publico/${item.id_producto}`);
                    if (response.ok) {
                        const product = await response.json();
                        // Agregar información del producto al item del carrito
                        item.product_name = product.nombre || `Producto ${item.id_producto}`;
                        item.product_image = product.imagen_url || '/static/img/logo.png';
                        item.product_codigo = product.codigo || '';

                        // Cargar información de variantes si existe
                        item.variant_info = null;
                        if (item.variant_data && typeof item.variant_data === 'object') {
                            item.variant_info = item.variant_data;
                        } else if (product.variants && product.variants.length > 0) {
                            // Si no hay variant_data pero el producto tiene variantes,
                            // intentar encontrar la variante por defecto o la primera disponible
                            const defaultVariant = product.variants.find(v => v.stock > 0) || product.variants[0];
                            if (defaultVariant) {
                                item.variant_info = {
                                    color: defaultVariant.color,
                                    tipo: defaultVariant.tipo,
                                    precio_adicional: defaultVariant.precio_adicional || 0
                                };
                            }
                        }
                    } else {
                        // Si falla la carga del producto, usar valores por defecto
                        item.product_name = `Producto ${item.id_producto}`;
                        item.product_image = '/static/img/logo.png';
                        item.product_codigo = '';
                        item.variant_info = null;
                    }
                } catch (error) {
                    console.warn(`Error cargando producto ${item.id_producto}:`, error);
                    item.product_name = `Producto ${item.id_producto}`;
                    item.product_image = '/static/img/logo.png';
                    item.product_codigo = '';
                    item.variant_info = null;
                }
            });

            await Promise.all(productPromises);
        } catch (error) {
            console.error('Error cargando detalles de productos:', error);
        }
    }

    /**
     * Obtiene el número total de items
     */
    getItemCount() {
        return this.cartItems.reduce((count, item) => count + item.cantidad, 0);
    }

    /**
     * Obtiene el total del carrito
     */
    getTotal() {
        return this.cartItems.reduce((total, item) => total + (item.cantidad * item.precio_unitario), 0);
    }

    /**
     * Verifica si el carrito está vacío
     */
    isEmpty() {
        return this.cartItems.length === 0;
    }

    /**
     * Sincroniza el carrito con el servidor (útil para asegurar consistencia)
     */
    async syncWithServer() {
        try {
            // console.log('Sincronizando carrito con servidor...');
            await this.loadCart();
        } catch (error) {
            console.error('Error sincronizando con servidor:', error);
        }
    }

    /**
     * Debug detallado: muestra información completa del carrito
     */
    debugDetailed() {
        console.log('=== 🛒 DETALLES COMPLETOS DEL CARRITO ===');
        console.log(`👤 User ID: ${this.userId}`);
        console.log(`🛒 Current Cart ID: ${this.currentCart ? this.currentCart.id : 'Ninguno'}`);

        if (this.currentCart) {
            console.log(`� Cart Details:`, {
                id: this.currentCart.id,
                user_id: this.currentCart.id_usuario,
                estado: this.currentCart.estado,
                created_at: this.currentCart.created_at
            });
        }

        console.log(`� Cart Items (${this.cartItems.length}):`);
        this.cartItems.forEach((item, index) => {
            console.log(`  ${index + 1}. Producto ID: ${item.id_producto}, Cantidad: ${item.cantidad}, Precio: $${this.formatPrice(item.precio_unitario)}, Subtotal: $${this.formatPrice(item.cantidad * item.precio_unitario)}`);
        });

        console.log(`💰 Total: $${this.formatPrice(this.getTotal())}`);
        console.log(`🔢 Item Count: ${this.getItemCount()}`);
        console.log(`📭 Is Empty: ${this.isEmpty()}`);
        console.log(`🔄 Is Loading: ${this.isLoading}`);
        console.log(`✅ Is Initialized: ${this.isInitialized}`);

        console.log(`🌐 DOM Elements:`, {
            sidebar: !!this.elements.sidebar,
            overlay: !!this.elements.overlay,
            cartItems: !!this.elements.cartItems,
            emptyCart: !!this.elements.emptyCart,
            cartFooter: !!this.elements.cartFooter,
            cartTotal: !!this.elements.cartTotal,
            cartCount: !!this.elements.cartCount
        });
        console.log('=======================================');
    }

    /**
     * Obtiene el valor de una cookie por nombre
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    /**
     * Elimina una cookie
     */
    deleteCookie(name) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    }

    /**
     * Guarda el carrito local en localStorage
     */
    saveLocalCart(localCartItems) {
        try {
            const localCartData = {
                items: localCartItems,
                timestamp: Date.now()
            };
            localStorage.setItem(this.localCartKey, JSON.stringify(localCartData));
        } catch (error) {
            console.error('Error guardando carrito local:', error);
        }
    }

    /**
     * Carga el carrito local desde localStorage
     */
    loadLocalCart() {
        try {
            const localCartData = localStorage.getItem(this.localCartKey);
            if (localCartData) {
                const parsed = JSON.parse(localCartData);
                // Solo cargar si no es muy antiguo (24 horas)
                if (parsed.timestamp && (Date.now() - parsed.timestamp) < 24 * 60 * 60 * 1000) {
                    return parsed.items || [];
                } else {
                    // Carrito expirado, limpiar
                    localStorage.removeItem(this.localCartKey);
                    return [];
                }
            }
            return [];
        } catch (error) {
            console.error('Error cargando carrito local:', error);
            return [];
        }
    }

    /**
     * Renderiza el carrito local (para usuarios no autenticados)
     */
    renderLocalCart() {
        const localCart = this.loadLocalCart();
        console.log(`Renderizando carrito local con ${localCart.length} items`);

        if (localCart.length > 0) {
            // Convertir items locales al formato del carrito del servidor para renderizar
            this.cartItems = localCart.map(item => ({
                id: `local_${item.product_id}_${Date.now()}`, // ID temporal para local
                id_producto: item.product_id,
                cantidad: item.quantity,
                precio_unitario: item.price,
                variant_data: item.variant_data,
                variant_info: item.variant_data,
                product_name: `Producto ${item.product_id}`, // Placeholder, se cargará después
                product_image: '/static/img/logo.png',
                product_codigo: ''
            }));

            // Calcular total de items para actualizar contador
            const totalItems = localCart.reduce((sum, item) => sum + item.quantity, 0);
            console.log(`Total de items en carrito local: ${totalItems}`);
            this.updateGlobalCartCount(totalItems);

            // Cargar detalles de productos para mostrar nombres correctos
            this.loadProductDetails().then(() => {
                this.render();
            });
        } else {
            console.log('Carrito local vacío');
            this.cartItems = [];
            this.renderEmptyCart();
            this.updateGlobalCartCount(0);
        }
    }

    /**
     * Sincroniza el carrito local con el servidor cuando el usuario se autentica
     * Nota: Este método ya no se usa ya que ahora requerimos autenticación para agregar productos
     */
    async syncLocalCartWithServer() {
        // Este método se mantiene por compatibilidad pero ya no debería ser necesario
        console.log('syncLocalCartWithServer: Método obsoleto, ya no se usa carrito local');
        return;
    }
}

// Crear instancia global del carrito
const cart = new Cart();

// ============================================================================
// FUNCIONES DE UTILIDADES PARA TOAST
// ============================================================================

/**
 * Muestra un mensaje toast de notificación
 */
function showToast(message, type = 'success') {
    // Si ya existe una función showToast global, úsala
    if (typeof window.showToast === 'function' && window.showToast !== showToast) {
        return window.showToast(message, type);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type} slide-in`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} mr-2"></i>
        ${message}
    `;
    document.getElementById('toast-container').appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Funciones globales para compatibilidad con HTML
function toggleCart() {
    cart.toggle();
}

function addToCart(productId, quantity = 1, price = 0, variantData = null) {
    return cart.addProduct(productId, quantity, price, variantData);
}

function updateQuantity(itemId, newQuantity) {
    cart.updateQuantity(itemId, newQuantity);
}

function removeItem(itemId) {
    cart.removeItem(itemId);
}

function reloadCart() {
    cart.loadCart(true);
}

function syncCart() {
    cart.syncWithServer();
}

function debugCart() {
    cart.debug();
}

function debugCartDetailed() {
    cart.debugDetailed();
}

// Alias para facilitar el debug desde consola
window.debugCart = debugCart;
window.cartDebug = () => cart.debug();
window.showCartDebug = () => cart.debug();
window.debugCartDetailed = debugCartDetailed;
window.cartDetails = () => cart.debugDetailed();

// Función helper para mostrar estado del carrito de forma simple
window.cartInfo = () => {
    console.log(`🛒 Carrito Usuario ${cart.userId}: ${cart.cartItems.length} items, Total: $${cart.formatPrice(cart.getTotal())}`);
    if (cart.currentCart) {
        console.log(`📋 Carrito ID: ${cart.currentCart.id}`);
    }
    return cart;
};

// Hacer la instancia global disponible
window.cart = cart;