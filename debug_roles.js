/* Script de depuración para ejecutar en la consola del navegador
   Para verificar el estado de las variables y funciones */

console.log('🔍 === DEPURACIÓN DE ROLES ===');

// 1. Verificar variables globales
console.log('📊 Estado de variables globales:');
console.log('- usuarios:', typeof usuarios, usuarios?.length || 0);
console.log('- roles:', typeof roles, roles?.length || 0);
console.log('- authToken:', authToken ? 'Presente' : 'No presente');

// 2. Verificar función de construcción de URL
if (typeof buildAuthUrl === 'function') {
    console.log('✅ buildAuthUrl disponible');
    const testUrl = buildAuthUrl('/usuarios_admin/roles/');
    console.log('🔗 URL de prueba:', testUrl);
} else {
    console.log('❌ buildAuthUrl no disponible');
}

// 3. Probar carga manual de roles
async function probarCargarRoles() {
    try {
        console.log('🧪 Probando carga manual de roles...');
        const url = buildAuthUrl('/usuarios_admin/roles/');
        const response = await fetch(url);
        console.log('📡 Status respuesta:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Roles cargados:', data);
        } else {
            console.log('❌ Error en respuesta:', response.statusText);
        }
    } catch (error) {
        console.log('❌ Error en fetch:', error);
    }
}

// 4. Verificar botones de editar roles
const botonesEditarRoles = document.querySelectorAll('.btn-editar-roles');
console.log('🔘 Botones editar roles encontrados:', botonesEditarRoles.length);

// 5. Función de prueba para simular clic
function probarEditarRoles() {
    if (botonesEditarRoles.length > 0) {
        console.log('🖱️ Simulando clic en primer botón...');
        botonesEditarRoles[0].click();
    } else {
        console.log('❌ No hay botones de editar roles');
    }
}

console.log('📝 Comandos disponibles:');
console.log('- probarCargarRoles(): Probar carga manual de roles');
console.log('- probarEditarRoles(): Simular clic en botón editar roles');

// Ejecutar prueba automática
probarCargarRoles();