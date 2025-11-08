# Integración SDK MercadoPago.js - Guía Técnica

## 🎯 **Configuración del Frontend para Checkout Pro**

Esta guía documenta la integración completa del SDK MercadoPago.js para implementar el checkout del lado del cliente de manera segura.

## 📦 **Incluir el SDK con HTML/JS**

### **Opción 1: CDN (Recomendado)**

Incluye el SDK agregando la etiqueta `<script>` justo antes de `</body>` en tu archivo HTML:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Mi Integración con Checkout Pro</title>
</head>
<body>

  <!-- Contenido de tu página -->

  <script src="https://sdk.mercadopago.com/js/v2"></script>

  <script>
    // Tu código JavaScript irá aquí
  </script>

</body>
</html>
```

### **Opción 2: Descarga Local**

Descarga el SDK desde las [bibliotecas oficiales de MercadoPago](https://github.com/mercadopago/sdk-js) e inclúyelo localmente:

```html
<script src="/static/js/mercadopago-sdk.js"></script>
```

## 🔑 **Credenciales Requeridas**

### **Public Key**
- **Producción**: Utiliza tu Public Key de producción
- **Pruebas**: Utiliza tu Public Key de pruebas (TEST-...)
- **Ubicación**: Dashboard de MercadoPago → Credenciales

### **Preference ID**
- **Obtención**: Recibido como respuesta del endpoint `POST /ecomerce/checkout/`
- **Formato**: `168706559-xxxxxxxxxxxxxxxx`
- **Validez**: 30 días desde la creación

## 🚀 **Inicializar el Checkout**

### **Código de Inicialización**

```javascript
// 1. Incluir el SDK
<script src="https://sdk.mercadopago.com/js/v2"></script>

<script>
  // 2. Configurar credenciales
  const publicKey = "YOUR_PUBLIC_KEY";  // Reemplaza con tu Public Key
  const preferenceId = "YOUR_PREFERENCE_ID";  // Reemplaza con el ID de preferencia

  // 3. Inicializar el SDK
  const mp = new MercadoPago(publicKey, {
    locale: 'es-AR'  // Configurar idioma (opcional)
  });

  // 4. Crear el builder de bricks
  const bricksBuilder = mp.bricks();

  // 5. Función para renderizar el wallet brick
  const renderWalletBrick = async (bricksBuilder) => {
    await bricksBuilder.create("wallet", "walletBrick_container", {
      initialization: {
        preferenceId: preferenceId,
      },
      callbacks: {
        onReady: () => {
          console.log('✅ Wallet Brick listo');
        },
        onError: (error) => {
          console.error('❌ Error en Wallet Brick:', error);
        }
      }
    });
  };

  // 6. Renderizar el brick
  renderWalletBrick(bricksBuilder);
</script>
```

## 🏗️ **Crear Contenedor HTML**

### **Estructura del Contenedor**

```html
<!-- Contenedor para el botón de pago -->
<div id="walletBrick_container"></div>
```

### **Estilos Recomendados**

```css
#walletBrick_container {
  max-width: 400px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #ffffff;
}
```

## 📋 **Implementación Completa**

### **Ejemplo Funcional**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout MercadoPago</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="max-w-md mx-auto p-6">
        <h1 class="text-2xl font-bold mb-6">Checkout Seguro</h1>

        <!-- Contenedor del botón de pago -->
        <div id="walletBrick_container" class="border rounded-lg p-4 bg-white shadow-sm">
            <!-- El SDK renderizará el botón aquí -->
        </div>
    </div>

    <!-- SDK MercadoPago -->
    <script src="https://sdk.mercadopago.com/js/v2"></script>

    <script>
        // Configuración
        const MERCADOPAGO_PUBLIC_KEY = "TEST-xxxxxxxxxxxxxxxxxxxx"; // Reemplaza con tu Public Key
        let currentPreferenceId = null;

        // Inicializar MercadoPago
        const mp = new MercadoPago(MERCADOPAGO_PUBLIC_KEY, {
            locale: 'es-AR'
        });

        // Función para renderizar el brick
        async function renderWalletBrick(preferenceId) {
            const container = document.getElementById('walletBrick_container');
            container.innerHTML = '<div class="text-center py-4">Cargando...</div>';

            try {
                const bricksBuilder = mp.bricks();

                await bricksBuilder.create("wallet", "walletBrick_container", {
                    initialization: {
                        preferenceId: preferenceId,
                    },
                    callbacks: {
                        onReady: () => {
                            console.log('✅ Wallet Brick listo para pago');
                            container.innerHTML = ''; // Limpiar mensaje de carga
                        },
                        onError: (error) => {
                            console.error('❌ Error en Wallet Brick:', error);
                            container.innerHTML = `
                                <div class="text-red-600 text-center py-4">
                                    Error al cargar el botón de pago
                                </div>
                            `;
                        }
                    }
                });

            } catch (error) {
                console.error('Error renderizando brick:', error);
                container.innerHTML = `
                    <div class="text-red-600 text-center py-4">
                        Error al inicializar MercadoPago
                    </div>
                `;
            }
        }

        // Función para crear preferencia de pago
        async function createPaymentPreference() {
            try {
                const response = await fetch('/ecomerce/checkout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${getToken()}`
                    },
                    body: JSON.stringify({
                        payment_method: 'mercadopago'
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    currentPreferenceId = data.preference_id;
                    await renderWalletBrick(data.preference_id);
                } else {
                    throw new Error('Error al crear preferencia');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al inicializar pago');
            }
        }

        // Función para obtener token de autenticación
        function getToken() {
            return localStorage.getItem('ecommerce_token') ||
                   sessionStorage.getItem('ecommerce_token');
        }

        // Inicializar cuando el DOM esté listo
        document.addEventListener('DOMContentLoaded', () => {
            createPaymentPreference();
        });
    </script>
</body>
</html>
```

## ⚙️ **Configuración Avanzada**

### **Callbacks Disponibles**

```javascript
await bricksBuilder.create("wallet", "walletBrick_container", {
    initialization: {
        preferenceId: preferenceId,
    },
    callbacks: {
        onReady: () => {
            console.log('Brick listo');
            // El botón está renderizado y listo
        },
        onError: (error) => {
            console.error('Error en brick:', error);
            // Manejar errores de renderizado
        },
        onSubmit: (formData) => {
            console.log('Pago iniciado:', formData);
            // El usuario hizo clic en pagar
        }
    },
    customization: {
        visual: {
            buttonBackground: 'blue',
            borderRadius: '6px'
        },
        texts: {
            action: 'pay',
            valueProp: 'security_details'
        }
    }
});
```

### **Personalización Visual**

```javascript
customization: {
    visual: {
        buttonBackground: 'blue', // 'blue', 'white', 'black'
        buttonHeight: '48px',
        borderRadius: '6px',
        valuePropColor: 'grey'
    },
    texts: {
        action: 'pay', // 'pay', 'buy'
        valueProp: 'security_details' // 'security_details', 'convenience', 'payment_methods'
    }
}
```

## 🔧 **Solución de Problemas**

### **Errores Comunes**

1. **"MercadoPago is not defined"**
   - Verifica que el script del SDK esté cargado antes de tu código
   - Asegúrate de que la URL del CDN sea correcta

2. **"Invalid preferenceId"**
   - Verifica que el preferenceId sea válido y no haya expirado
   - Confirma que el preferenceId corresponda a tu Public Key

3. **"Brick container not found"**
   - Asegúrate de que el elemento con id `walletBrick_container` exista en el DOM
   - Verifica que el ID coincida exactamente

4. **"Public key not found"**
   - Confirma que estés usando la Public Key correcta
   - Verifica que no estés usando la Access Token por error

### **Debugging**

```javascript
// Función de diagnóstico
window.diagnoseMercadoPago = function() {
    return {
        sdkLoaded: typeof MercadoPago !== 'undefined',
        publicKey: MERCADOPAGO_PUBLIC_KEY,
        preferenceId: currentPreferenceId,
        containerExists: document.getElementById('walletBrick_container') !== null,
        userAgent: navigator.userAgent
    };
};

// Ejecutar en consola: diagnoseMercadoPago()
```

## 📚 **Recursos Adicionales**

- [Documentación Oficial MercadoPago](https://www.mercadopago.com.ar/developers/es/docs/checkout-pro/integrate-checkout-pro/web)
- [Referencia API Bricks](https://github.com/mercadopago/sdk-js)
- [Ejemplos de Integración](https://github.com/mercadopago/sdk-js-examples)
- [Dashboard de Credenciales](https://www.mercadopago.com.ar/developers/panel)

## ✅ **Checklist de Implementación**

- [ ] SDK incluido en el HTML
- [ ] Public Key configurada correctamente
- [ ] Preference ID obtenido del backend
- [ ] Contenedor HTML creado
- [ ] Brick renderizado exitosamente
- [ ] Callbacks implementados
- [ ] Manejo de errores agregado
- [ ] Testing en modo sandbox completado</content>
<parameter name="filePath">c:\Users\PCJuan\Desktop\sql_app_Ecomerce\MERCADOPAGO_SDK_FRONTEND_GUIDE.md