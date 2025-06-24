/**
 * Script avanzado de gestión de usuarios - Panel de administración
 * Versión LIMPIA sin tokens - Backend maneja toda la autenticación
 */

// ==================== VARIABLES GLOBALES ====================
let usuarios = [];
let roles = [];
let paginaActual = 1;
let usuariosPorPagina = 10;
let usuarioIdActual = null;
let totalPaginas = 0;
let tabActual = 'usuarios';

// ==================== FUNCIONES GLOBALES ====================

function initializeToken() {
    // No manejamos tokens en el frontend - la autenticación la maneja el backend
    // Solo limpiamos la URL si tiene token para que no se vea
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    
    if (tokenFromUrl) {
        console.log('🔑 Limpiando token de URL - la autenticación la maneja el backend');
        // Limpiar la URL para que no se vea el token
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    }
    
    console.log('✅ Frontend inicializado - autenticación delegada al backend');
    return true;
}

async function cargarUsuarios() {
    try {
        console.log('🔄 === INICIO CARGA USUARIOS ===');
        console.log('🔍 Cargando usuarios sin token (backend maneja autenticación)');
        
        // Construir parámetros de consulta
        const params = new URLSearchParams();
        const searchUsuarios = document.getElementById('searchUsuarios');
        const filterEstado = document.getElementById('filterEstado');
        const filterRol = document.getElementById('filterRol');
        
        const busqueda = searchUsuarios?.value?.trim();
        const estado = filterEstado?.value;
        const rol = filterRol?.value;
        
        if (busqueda) params.append('search', busqueda);
        if (estado) params.append('activo', estado);
        if (rol) params.append('rol', rol);
        
        console.log('🔄 Cargando usuarios con parámetros:', params.toString());
        console.log('🌐 URL completa:', `/usuarios_admin/usuarios-con-detalles/?${params.toString()}`);
        
        const response = await fetch(`/usuarios_admin/usuarios-con-detalles/?${params.toString()}`);
        
        console.log('📡 Status de respuesta:', response.status);
        console.log('📡 Headers de respuesta:', Object.fromEntries(response.headers));
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        usuarios = await response.json();
        console.log('✅ Usuarios cargados:', usuarios.length);
        console.log('📋 Primeros usuarios:', usuarios.slice(0, 2));
        
        renderizarUsuarios();
        actualizarPaginacion();
        
    } catch (error) {
        console.error('❌ Error al cargar usuarios:', error);
        mostrarNotificacion('Error al cargar usuarios: ' + error.message, 'error');
        mostrarErrorCarga();
    }
    console.log('🔚 === FIN CARGA USUARIOS ===');
}

// ==================== FUNCIONES PARA ESTADÍSTICAS SIN TOKENS ====================

async function cargarEstadisticas() {
    try {
        console.log('📊 Cargando estadísticas...');
        const response = await fetch('/usuarios_admin/estadisticas-avanzadas/');
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const estadisticas = await response.json();
        console.log('📊 Estadísticas cargadas:', estadisticas);
        
        // Actualizar elementos de estadísticas usando los datos del resumen
        const totalUsersElement = document.getElementById('total-users');
        const activeUsersElement = document.getElementById('active-users');
        const adminUsersElement = document.getElementById('admin-users');
        const totalRolesElement = document.getElementById('total-roles');
        
        if (totalUsersElement) {
            totalUsersElement.textContent = estadisticas.resumen.total_usuarios || 0;
            console.log('📊 Total usuarios actualizado:', estadisticas.resumen.total_usuarios);
        }
        if (activeUsersElement) {
            activeUsersElement.textContent = estadisticas.resumen.usuarios_activos || 0;
            console.log('📊 Usuarios activos actualizado:', estadisticas.resumen.usuarios_activos);
        }
        if (adminUsersElement) {
            // Usar total_administradores del resumen, no del por_roles
            const adminCount = estadisticas.resumen.total_administradores || 
                              estadisticas.por_roles.admin || 
                              estadisticas.por_roles.administrador || 1;
            adminUsersElement.textContent = adminCount;
            console.log('📊 Administradores actualizado:', adminCount);
        }
        if (totalRolesElement) {
            const totalRoles = estadisticas.resumen.total_roles || 
                              Object.keys(estadisticas.por_roles || {}).length || 0;
            totalRolesElement.textContent = totalRoles;
            console.log('📊 Total roles actualizado:', totalRoles);
        }
        
        return estadisticas;
        
    } catch (error) {
        console.error('❌ Error al cargar estadísticas:', error);
        // Valores por defecto en caso de error
        const totalUsersElement = document.getElementById('total-users');
        const activeUsersElement = document.getElementById('active-users');
        const adminUsersElement = document.getElementById('admin-users');
        const totalRolesElement = document.getElementById('total-roles');
        
        if (totalUsersElement) totalUsersElement.textContent = '0';
        if (activeUsersElement) activeUsersElement.textContent = '0';
        if (adminUsersElement) adminUsersElement.textContent = '0';
        if (totalRolesElement) totalRolesElement.textContent = '0';
        
        mostrarNotificacion('Error al cargar estadísticas: ' + error.message, 'error');
    }
}

async function cargarRoles() {
    try {
        console.log('🏷️ Cargando roles...');
        const response = await fetch('/usuarios_admin/roles/');
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        roles = await response.json();
        console.log('✅ Roles cargados:', roles.length);
        
        renderizarRoles();
        
    } catch (error) {
        console.error('❌ Error al cargar roles:', error);
        mostrarNotificacion('Error al cargar roles: ' + error.message, 'error');
    }
}

async function cargarPermisos() {
    try {
        console.log('🔒 Cargando permisos...');
        const response = await fetch('/usuarios_admin/permisos/');
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const permisos = await response.json();
        console.log('✅ Permisos cargados:', permisos.length);
        
        renderizarPermisos(permisos);
        
    } catch (error) {
        console.error('❌ Error al cargar permisos:', error);
        mostrarNotificacion('Error al cargar permisos: ' + error.message, 'error');
    }
}

async function cargarAuditoria() {
    try {
        console.log('📋 Cargando auditoría...');
        const response = await fetch('/usuarios_admin/auditoria/');
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const auditoria = await response.json();
        console.log('✅ Auditoría cargada:', auditoria.length);
        
        renderizarAuditoria(auditoria);
        
    } catch (error) {
        console.error('❌ Error al cargar auditoría:', error);
        mostrarNotificacion('Error al cargar auditoría: ' + error.message, 'error');
    }
}

console.log('🔑 Script de gestión sin tokens cargado correctamente - Versión LIMPIA');
