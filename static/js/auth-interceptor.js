/**
 * Interceptor de Autenticación Global
 * 
 * Este archivo resuelve el problema del bucle infinito de login mediante:
 * 1. Interceptor de fetch que automáticamente incluye tokens JWT
 * 2. Función de navegación con autenticación previa
 * 3. Validación automática de tokens
 * 
 * Uso: Incluir este script en todas las páginas que requieran autenticación
 */

console.log('🔐 Cargando interceptor de autenticación...');
console.log('🌐 URL actual:', window.location.href);
console.log('📅 Timestamp:', new Date().toISOString());

// Marcar que el interceptor se cargó
window.AUTH_INTERCEPTOR_LOADED = true;
window.AUTH_INTERCEPTOR_VERSION = '2.1.0';
console.log('✅ Interceptor de autenticación cargado - Versión:', window.AUTH_INTERCEPTOR_VERSION);

// =================================================================
// CONFIGURACIÓN Y CONSTANTES
// =================================================================

const AUTH_CONFIG = {
    TOKEN_KEY: 'access_token',
    LOGIN_ENDPOINT: '/login',
    LOGOUT_ENDPOINT: '/logout',
    LOGIN_PAGE: '/loginpage',
    DEBUG_ENDPOINT: '/admin-debug',
    EXCLUDED_PATHS: ['/login', '/logout', '/loginpage', '/registerpage', '/static']
};

// =================================================================
// INTERCEPTOR DE FETCH PARA AUTENTICACIÓN AUTOMÁTICA
// =================================================================

/**
 * Intercepta todas las peticiones fetch y agrega automáticamente
 * el token de autorización cuando está disponible
 */
(function setupFetchInterceptor() {
    // Guardar referencia al fetch original
    const originalFetch = window.fetch;
    
    // Sobrescribir fetch global
    window.fetch = function(url, options = {}) {
        // Obtener token de localStorage
        const token = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
        
        // Verificar si debe incluir token
        const shouldIncludeToken = token && 
            !AUTH_CONFIG.EXCLUDED_PATHS.some(path => url.includes(path)) &&
            url !== AUTH_CONFIG.DEBUG_ENDPOINT; // Evitar loop en validaciones
          if (shouldIncludeToken) {
            // Asegurar que existe el objeto headers
            options.headers = options.headers || {};
            
            // Solo agregar si no hay Authorization header ya presente
            const hasAuthHeader = Object.keys(options.headers).some(
                key => key.toLowerCase() === 'authorization'
            );
            
            if (!hasAuthHeader) {
                options.headers['Authorization'] = `Bearer ${token}`;
                console.log('🔐✅ Token agregado automáticamente a:', url);
                console.log('🎫 Token (primeros 20 chars):', token.substring(0, 20) + '...');
            } else {
                console.log('🔐⚠️ Header Authorization ya presente en:', url);
            }
        } else if (token) {
            console.log('🔐⏭️ Token disponible pero excluido para:', url);
        } else {
            console.log('🔐❌ No hay token disponible para:', url);
        }
        
        // Llamar al fetch original
        return originalFetch.call(this, url, options)
            .then(response => {
                // Manejar respuestas 401 (no autorizado)
                if (response.status === 401 && shouldIncludeToken) {
                    console.log('🚨 Token rechazado por el servidor, limpiando localStorage');
                    localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY);
                    
                    // Solo redirigir si no estamos ya en login
                    if (!window.location.pathname.includes('login')) {
                        window.location.href = AUTH_CONFIG.LOGIN_PAGE;
                    }
                }
                
                return response;
            })
            .catch(error => {
                console.error('❌ Error en petición interceptada:', error);
                throw error;
            });
    };
    
    console.log('✅ Interceptor de fetch configurado');
})();

// =================================================================
// NAVEGACIÓN CON AUTENTICACIÓN
// =================================================================

/**
 * Navega a una URL verificando primero la autenticación
 * Previene el bucle infinito haciendo una petición previa con token
 */
window.navigateWithAuth = function(url) {
    console.log('🚀 navigateWithAuth llamado para:', url);
    const token = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
    console.log('🎫 Token disponible:', !!token);
    
    if (!token) {
        // Sin token, navegar normalmente (probablemente redirigirá a login)
        console.log('🚪 Navegando sin token a:', url);
        window.location.href = url;
        return;
    }
    
    console.log('🔐 Navegando con verificación de token a:', url);
    console.log('🎫 Token (primeros 20 chars):', token.substring(0, 20) + '...');
    
    // Hacer petición de verificación antes de navegar
    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    })
    .then(response => {
        if (response.ok) {
            // Token válido, navegar normalmente
            console.log('✅ Token válido, navegando a:', url);
            window.location.href = url;
        } else if (response.status === 401) {
            // Token inválido, limpiar y ir a login
            console.log('🚨 Token inválido, redirigiendo a login');
            localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY);
            window.location.href = AUTH_CONFIG.LOGIN_PAGE;
        } else {
            // Otros errores, navegar normalmente
            console.log(`⚠️ Error ${response.status}, navegando normalmente`);
            window.location.href = url;
        }
    })
    .catch(error => {
        console.error('❌ Error en verificación de navegación:', error);
        // En caso de error de red, navegar normalmente
        window.location.href = url;
    });
};

// =================================================================
// VALIDACIÓN DE TOKEN
// =================================================================

/**
 * Verifica si el token actual es válido
 */
window.validateCurrentToken = async function() {
    const token = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
    
    if (!token) {
        console.log('❌ No hay token para validar');
        return false;
    }
    
    try {
        console.log('🔍 Validando token actual...');
        
        const response = await fetch(AUTH_CONFIG.DEBUG_ENDPOINT, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            console.log('✅ Token válido');
            return true;
        } else if (response.status === 401) {
            console.log('❌ Token inválido o expirado');
            localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY);
            return false;
        } else {
            console.log(`⚠️ Respuesta inesperada: ${response.status}`);
            return false;
        }
        
    } catch (error) {
        console.error('❌ Error validando token:', error);
        return false;
    }
};

// =================================================================
// FUNCIONES DE UTILIDAD
// =================================================================

/**
 * Obtiene el token actual del localStorage
 */
window.getCurrentToken = function() {
    return localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
};

/**
 * Limpia el token y redirige a login
 */
window.logout = function() {
    localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY);
    window.location.href = AUTH_CONFIG.LOGIN_PAGE;
};

/**
 * Verifica si el usuario está logueado
 */
window.isLoggedIn = function() {
    return !!localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
};

// =================================================================
// INICIALIZACIÓN AUTOMÁTICA
// =================================================================

// Verificar token al cargar la página (solo si no estamos en login)
document.addEventListener('DOMContentLoaded', function() {
    if (!window.location.pathname.includes('login') && 
        !window.location.pathname.includes('register')) {
        
        const token = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
        if (token) {
            console.log('🔍 Verificando token al cargar página...');
            // La validación se hará automáticamente con el interceptor
        }
    }
});

// =================================================================
// FUNCIÓN DE DEBUG PARA CONSOLA DEL NAVEGADOR
// =================================================================

/**
 * Función de debug que el usuario puede ejecutar en la consola
 * para verificar el estado del interceptor
 */
window.debugAuthInterceptor = function() {
    console.log('🔍 DEBUG DEL INTERCEPTOR DE AUTENTICACIÓN');
    console.log('==========================================');
    console.log('✅ Interceptor cargado:', !!window.AUTH_INTERCEPTOR_LOADED);
    console.log('📦 Versión:', window.AUTH_INTERCEPTOR_VERSION || 'N/A');
    console.log('🌐 URL actual:', window.location.href);
    console.log('🎫 Token en localStorage:', !!localStorage.getItem(AUTH_CONFIG.TOKEN_KEY));
    console.log('🔧 Función navigateWithAuth disponible:', typeof window.navigateWithAuth);
    console.log('🔧 Función validateCurrentToken disponible:', typeof window.validateCurrentToken);
    console.log('📊 Fetch original respaldado:', !!window.fetch);
    
    const token = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
    if (token) {
        console.log('🎫 Token (primeros 30 chars):', token.substring(0, 30) + '...');
        console.log('🎫 Token (últimos 10 chars):', '...' + token.slice(-10));
        console.log('📏 Longitud del token:', token.length);
    }
    
    console.log('🔧 Configuración AUTH_CONFIG:', AUTH_CONFIG);
    console.log('==========================================');
    
    // Test rápido del interceptor
    console.log('🧪 Ejecutando test rápido del interceptor...');
    fetch('/usuarios/current', {
        method: 'GET',
        headers: {'Cache-Control': 'no-cache'}
    })
    .then(response => {
        console.log('📊 Respuesta del test:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📊 Datos del test:', data);
    })
    .catch(error => {
        console.log('❌ Error en test:', error);
    });
};

console.log('✅ Interceptor de autenticación cargado completamente');
console.log('🔧 Para debug, ejecuta: debugAuthInterceptor() en la consola');
