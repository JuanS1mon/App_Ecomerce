// Script de prueba para verificar la conectividad de MercadoPago
// Ejecutar en la consola del navegador en la página de checkout

async function testMercadoPagoConnectivity() {
    console.log('🧪 Probando conectividad de MercadoPago...');

    try {
        const isConnected = await checkMercadoPagoConnectivity();
        console.log('✅ Resultado de conectividad:', isConnected);

        if (isConnected) {
            console.log('🎉 MercadoPago está disponible. El checkout debería funcionar correctamente.');
        } else {
            console.log('⚠️ MercadoPago está bloqueado. Se mostrará el mensaje de error al usuario.');
        }

        return isConnected;
    } catch (error) {
        console.error('❌ Error durante la prueba de conectividad:', error);
        return false;
    }
}

// Función para probar la renderización del brick (solo si está conectado)
async function testBrickRendering() {
    console.log('🧪 Probando renderización del brick de MercadoPago...');

    const isConnected = await testMercadoPagoConnectivity();

    if (!isConnected) {
        console.log('⏭️ Saltando prueba de renderización porque MercadoPago está bloqueado.');
        return false;
    }

    try {
        // Simular la selección de MercadoPago
        const mercadopagoOption = document.querySelector('input[value="mercadopago"]');
        if (mercadopagoOption) {
            mercadopagoOption.checked = true;
            mercadopagoOption.dispatchEvent(new Event('change'));
            console.log('✅ Opción de MercadoPago seleccionada.');
        } else {
            console.log('⚠️ No se encontró la opción de MercadoPago en el DOM.');
        }

        return true;
    } catch (error) {
        console.error('❌ Error durante la prueba de renderización:', error);
        return false;
    }
}

// Ejecutar pruebas automáticamente
console.log('🚀 Iniciando pruebas de MercadoPago...');
testMercadoPagoConnectivity().then(() => {
    console.log('📋 Prueba de conectividad completada.');
    console.log('💡 Para probar la renderización del brick, ejecuta: testBrickRendering()');
});

// Hacer las funciones disponibles globalmente para pruebas manuales
window.testMercadoPagoConnectivity = testMercadoPagoConnectivity;
window.testBrickRendering = testBrickRendering;