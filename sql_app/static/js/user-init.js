/**
 * user-init.js
 * Script para inicializar datos del usuario en todas las páginas de la aplicación
 * Este script debe incluirse antes de cualquier componente que necesite información del usuario
 */

// Función para cargar los datos del usuario actual
function loadCurrentUser() {
    // Verificar si ya tenemos datos del usuario en window.currentUser
    if (window.currentUser && window.currentUser.autenticado) {
        console.log('Usando datos de usuario ya cargados');
        return Promise.resolve(window.currentUser);
    }

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
        console.log('Datos de usuario obtenidos de API');
        return data;
    })
    .catch(error => {
        console.warn('Error al cargar usuario:', error);
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