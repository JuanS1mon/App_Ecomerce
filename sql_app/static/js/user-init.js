/**
 * user-init.js
 * Script para inicializar datos del usuario en todas las páginas de la aplicación
 * Este script debe incluirse antes de cualquier componente que necesite información del usuario
 */

// Variable global para evitar llamadas duplicadas
window._USER_LOADING = false;
window._USER_LOADED = false;

// Función para cargar los datos del usuario actual
function loadCurrentUser() {
    // ✅ PREVENIR LLAMADAS DUPLICADAS
    if (window._USER_LOADING) {
        console.log('🔄 Usuario ya cargándose, esperando...');
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (window._USER_LOADED && window.currentUser) {
                    clearInterval(checkInterval);
                    resolve(window.currentUser);
                } else if (!window._USER_LOADING) {
                    clearInterval(checkInterval);
                    loadCurrentUser().then(resolve);
                }
            }, 100);
        });
    }

    // Verificar si ya tenemos datos del usuario en window.currentUser
    if (window.currentUser && window.currentUser.autenticado) {
        console.log('Usando datos de usuario ya cargados');
        window._USER_LOADED = true;
        return Promise.resolve(window.currentUser);
    }

    // Marcar que estamos cargando para evitar duplicados
    window._USER_LOADING = true;
    console.log('🔄 Cargando datos de usuario...');

    // Si no hay datos, cargarlos desde la API
    return fetch('/usuarios/current', {
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
    })
    .then(response => {
        if (response.ok) return response.json();
        throw new Error('No se pudo obtener la información del usuario');
    })
    .then(data => {
        // Guardar para uso futuro en toda la aplicación
        window.currentUser = data;
        window._USER_LOADED = true;
        window._USER_LOADING = false;
        console.log('✅ Datos de usuario obtenidos de API');
        return data;
    })
    .catch(error => {
        window._USER_LOADING = false;
        console.warn('⚠️ Error al cargar usuario:', error);
        // Crear un usuario genérico para evitar errores en la UI
        window.currentUser = {
            nombre: "Usuario",
            email: "usuario@ejemplo.com", 
            usuario: "invitado",
            autenticado: false
        };
        return window.currentUser;
    });
}

// Cargar el usuario al inicio
document.addEventListener('DOMContentLoaded', function() {
    loadCurrentUser().then(user => {
        // Actualizar elementos de UI si existen
        const userInitials = document.querySelectorAll('[id="user-initial"]');
        const userNames = document.querySelectorAll('[id="user-name"]');
        const userEmails = document.querySelectorAll('[id="user-email"]');

        // Actualizar inicial del usuario
        userInitials.forEach(el => {
            if (user.nombre) {
                el.textContent = user.nombre.charAt(0).toUpperCase();
            }
        });

        // Actualizar nombre de usuario
        userNames.forEach(el => {
            if (user.nombre) {
                el.textContent = user.nombre;
            }
        });

        // Actualizar email de usuario
        userEmails.forEach(el => {
            if (user.email) {
                el.textContent = user.email;
            }
        });

        // Propagar un evento personalizado para que otros componentes sepan que el usuario está cargado
        document.dispatchEvent(new CustomEvent('userLoaded', { detail: user }));
    });
});

// Exponer la función globalmente para otros scripts
window.loadCurrentUser = loadCurrentUser;