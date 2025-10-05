/**
 * Auth Links Handler - Manejo automático de tokens en enlaces
 * ============================================================
 * 
 * Este script se encarga de:
 * 1. Detectar tokens de autenticación en la URL actual
 * 2. Propagar automáticamente tokens a todos los enlaces relevantes
 * 3. Manejar la navegación preservando la autenticación
 */

(function() {
    'use strict';
    
    // Función para obtener parámetros de URL
    function getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return Object.fromEntries(params);
    }
    
    // Función para obtener token de la URL actual o cookies
    function getCurrentToken() {
        // 1. Intentar desde URL params (prioridad alta)
        const urlParams = getUrlParams();
        if (urlParams.token) {
            console.log('🔑 Token encontrado en URL params');
            return urlParams.token;
        }
        
        // 2. Intentar desde cookies (fallback)
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'access_token' && value) {
                console.log('🔑 Token encontrado en cookies');
                return value;
            }
        }
        
        console.log('⚠️ No se encontró token');
        return null;
    }
    
    // Función para determinar si un enlace necesita token
    function needsAuth(href) {
        const authRoutes = [
            '/admin',
            '/usuarios_admin',
            '/migraciones',
            '/generar',
            '/analisis',
            '/scraping',
            '/tickets'
        ];
        
        return authRoutes.some(route => href.includes(route));
    }
    
    // Función para agregar token a un enlace
    function addTokenToLink(link, token) {
        if (!link.href || !token) return;
        
        try {
            const url = new URL(link.href, window.location.origin);
            
            // Solo agregar token si la ruta necesita autenticación
            if (needsAuth(url.pathname)) {
                url.searchParams.set('token', token);
                link.href = url.toString();
                console.log(`🔗 Token agregado a: ${url.pathname}`);
            }
        } catch (e) {
            console.warn('Error procesando enlace:', link.href, e);
        }
    }
    
    // Función para procesar todos los enlaces en la página
    function processAllLinks() {
        const token = getCurrentToken();
        
        if (!token) {
            console.log('⚠️ No hay token disponible, omitiendo procesamiento de enlaces');
            return;
        }
        
        // Procesar todos los enlaces <a>
        const links = document.querySelectorAll('a[href]');
        links.forEach(link => addTokenToLink(link, token));
        
        // Procesar formularios que van a rutas protegidas
        const forms = document.querySelectorAll('form[action]');
        forms.forEach(form => {
            if (needsAuth(form.action)) {
                // Agregar token como campo oculto
                let tokenInput = form.querySelector('input[name="token"]');
                if (!tokenInput) {
                    tokenInput = document.createElement('input');
                    tokenInput.type = 'hidden';
                    tokenInput.name = 'token';
                    form.appendChild(tokenInput);
                }
                tokenInput.value = token;
                console.log(`📝 Token agregado a formulario: ${form.action}`);
            }
        });
        
        console.log(`✅ Procesados ${links.length} enlaces y ${forms.length} formularios`);
    }
    
    // Función para manejar navegación dinámica
    function handleDynamicNavigation() {
        // Interceptar clics en enlaces
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a[href]');
            if (!link) return;
            
            const token = getCurrentToken();
            if (token && needsAuth(link.href)) {
                // Si el enlace no tiene token y necesita autenticación, agregarlo
                if (!link.href.includes('token=')) {
                    e.preventDefault();
                    addTokenToLink(link, token);
                    window.location.href = link.href;
                }
            }
        });
    }
    
    // Función para guardar token en cookies si viene en URL
    function saveTokenFromUrl() {
        const urlParams = getUrlParams();
        if (urlParams.token) {
            // Guardar token en cookie para navegación futura
            document.cookie = `access_token=${urlParams.token}; path=/; SameSite=Lax`;
            console.log('💾 Token guardado en cookies');
        }
    }
    
    // Función principal de inicialización
    function initAuthLinks() {
        console.log('🚀 Iniciando Auth Links Handler');
        
        // Guardar token de URL en cookies si existe
        saveTokenFromUrl();
        
        // Procesar enlaces existentes
        processAllLinks();
        
        // Configurar manejo de navegación dinámica
        handleDynamicNavigation();
        
        // Observar cambios en el DOM para procesar nuevos enlaces
        const observer = new MutationObserver(function(mutations) {
            let shouldReprocess = false;
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'A' || node.querySelector('a[href]')) {
                            shouldReprocess = true;
                        }
                    }
                });
            });
            
            if (shouldReprocess) {
                console.log('🔄 Reprocesando enlaces tras cambios en DOM');
                processAllLinks();
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('✅ Auth Links Handler inicializado');
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAuthLinks);
    } else {
        initAuthLinks();
    }
    
    // Exponer funciones globalmente para uso manual si es necesario
    window.AuthLinks = {
        processAllLinks: processAllLinks,
        getCurrentToken: getCurrentToken,
        addTokenToLink: addTokenToLink
    };
    
})();