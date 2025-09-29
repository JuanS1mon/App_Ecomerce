/**
 * Sistema de Autenticación Universal para todas las páginas protegidas
 * 
 * Este script debe incluirse en todas las páginas HTML que requieran autenticación.
 * Maneja automáticamente:
 * - Verificación de token en localStorage
 * - Redirección a login si no hay token
 * - Obtención de datos del usuario desde API protegida
 * - Actualización dinámica de información del usuario en la página
 * - Interceptor automático para peticiones fetch
 */

(function() {
    'use strict';
    
    // Configuración del sistema de autenticación
    const AUTH_CONFIG = {
        TOKEN_KEY: 'access_token',
        LOGIN_PAGE: '/loginpage',
        EXCLUDED_PATHS: ['/login', '/logout', '/loginpage', '/registerpage', '/static'],
        DEBUG: true  // Cambiar a false en producción
    };
    
    // Función de logging condicional
    function log(message, ...args) {
        if (AUTH_CONFIG.DEBUG) {
            console.log(`🔐 Auth: ${message}`, ...args);
        }
    }
    
    /**
     * Configurar interceptor global para fetch
     * Agrega automáticamente el token JWT a todas las peticiones
     */
    function setupFetchInterceptor() {
        if (window.AUTH_INTERCEPTOR_LOADED) return;
        
        log('Configurando interceptor de fetch...');
        
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            const token = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
            const shouldIncludeToken = token && 
                !AUTH_CONFIG.EXCLUDED_PATHS.some(path => url.includes(path));
            
            if (shouldIncludeToken) {
                options.headers = options.headers || {};
                const hasAuthHeader = Object.keys(options.headers).some(
                    key => key.toLowerCase() === 'authorization'
                );
                
                if (!hasAuthHeader) {
                    options.headers['Authorization'] = `Bearer ${token}`;
                    log('Token agregado a petición:', url);
                }
            }
            
            return originalFetch.call(this, url, options)
                .then(response => {
                    if (response.status === 401 && shouldIncludeToken) {
                        log('Token rechazado (401), redirigiendo a login');
                        redirectToLogin('token_rejected');
                    }
                    return response;
                });
        };
        
        window.AUTH_INTERCEPTOR_LOADED = true;
        log('Interceptor de fetch configurado');
    }
    
    /**
     * Redirigir al usuario a la página de login
     */
    function redirectToLogin(reason = '') {
        localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY);
        const errorParam = reason ? `?error=${reason}` : '';
        log(`Redirigiendo a login. Razón: ${reason}`);
        window.location.href = AUTH_CONFIG.LOGIN_PAGE + errorParam;
    }
    
    /**
     * Actualizar información del usuario en la página
     */
    function updateUserInfo(user) {
        log('Actualizando información del usuario en la página');
        
        // Actualizar elementos con data-user-name
        const userNameElements = document.querySelectorAll('[data-user-name]');
        userNameElements.forEach(element => {
            element.textContent = user.nombre || user.username || 'Usuario';
        });
        
        // Actualizar elementos con data-user-email
        const userEmailElements = document.querySelectorAll('[data-user-email]');
        userEmailElements.forEach(element => {
            element.textContent = user.email || 'usuario@sistema.com';
        });
        
        // Actualizar elementos con data-user-roles
        const userRoleElements = document.querySelectorAll('[data-user-roles]');
        userRoleElements.forEach(element => {
            const roles = Array.isArray(user.roles) ? user.roles.join(', ') : 'Usuario';
            element.textContent = roles;
        });
        
        // Disparar evento personalizado para que otras partes del código reaccionen
        window.dispatchEvent(new CustomEvent('userInfoUpdated', { detail: user }));
        
        log('Información del usuario actualizada');
    }
    
    /**
     * Verificar autenticación y obtener datos del usuario
     */
    function verifyAuthAndLoadData(dataEndpoint) {
        log('Verificando autenticación...');
        
        // Verificar si hay token
        const token = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
        if (!token) {
            log('No hay token almacenado');
            redirectToLogin('token_required');
            return;
        }
        
        log('Token encontrado, verificando validez...');
        
        // Verificar token y obtener datos del usuario
        fetch(dataEndpoint, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.status === 401) {
                log('Token inválido (401)');
                redirectToLogin('token_invalid');
                return null;
            } else if (response.ok) {
                log('Token válido, obteniendo datos...');
                return response.json();
            } else {
                log('Error obteniendo datos:', response.status);
                throw new Error(`HTTP ${response.status}`);
            }
        })
        .then(data => {
            if (data && data.user) {
                log('Datos del usuario obtenidos:', data.user);
                updateUserInfo(data.user);
                
                // Disparar evento con todos los datos para uso específico de la página
                window.dispatchEvent(new CustomEvent('pageDataLoaded', { detail: data }));
            }
        })
        .catch(error => {
            log('Error de conexión:', error);
            // En caso de error de red, mostrar mensaje pero no redirigir automáticamente
            console.warn('⚠️ Error cargando datos del usuario. Verifique su conexión.');
        });
    }
    
    /**
     * Función principal de inicialización
     */
    function initializeAuth(dataEndpoint) {
        log('Inicializando sistema de autenticación...');
        log('Endpoint de datos:', dataEndpoint);
        
        // Configurar interceptor
        setupFetchInterceptor();
        
        // Verificar autenticación cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                verifyAuthAndLoadData(dataEndpoint);
            });
        } else {
            verifyAuthAndLoadData(dataEndpoint);
        }
    }
    
    // Exportar funciones para uso global
    window.AuthSystem = {
        init: initializeAuth,
        updateUserInfo: updateUserInfo,
        redirectToLogin: redirectToLogin,
        getToken: () => localStorage.getItem(AUTH_CONFIG.TOKEN_KEY),
        isAuthenticated: () => !!localStorage.getItem(AUTH_CONFIG.TOKEN_KEY)
    };
    
    log('Sistema de autenticación cargado y listo');
    
})();
