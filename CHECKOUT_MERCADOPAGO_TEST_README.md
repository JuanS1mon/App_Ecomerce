# Checkout de Prueba - MercadoPago

Este documento explica cómo usar la página de checkout de prueba exclusiva para MercadoPago.

## 🎯 Propósito

La página `checkout_mercadopago_test.html` es una versión simplificada del checkout que **solo incluye MercadoPago** como método de pago. Su objetivo es:

- **Capturar exactamente** qué parámetros envía MercadoPago en las URLs de retorno
- **Depurar** problemas de integración sin interferencias de otros métodos de pago
- **Analizar** el flujo completo de pago de MercadoPago

## 🚀 Cómo Usar

### 1. Iniciar el Servidor

```bash
uvicorn main:app --reload
```

### 2. Acceder a la Página

**URL directa:** `http://localhost:8000/checkout/mercadopago/test`

**O usando el script de prueba:**
```bash
python test_checkout_mercadopago.py
```

### 3. Probar el Pago

1. **Inicia sesión** en la aplicación (necesitas un token válido)
2. **Haz clic en "Crear Preferencia de Pago"**
3. **Completa el pago** usando MercadoPago
4. **Observa los parámetros** que llegan en las URLs de retorno

## 📊 Información de Depuración

La página muestra automáticamente:

- **URL actual** con todos los parámetros GET
- **User Agent** del navegador
- **Timestamp** de recepción
- **Parámetros parseados** en formato JSON

### Parámetros Importantes de MercadoPago

Cuando MercadoPago redirige de vuelta, busca estos parámetros:

```javascript
{
  "collection_id": "123456789",           // ID de la colección
  "collection_status": "approved",        // Estado del pago
  "payment_id": "123456789",              // ID del pago
  "status": "approved",                   // Estado simplificado
  "external_reference": "ORDER-123",      // Referencia externa
  "merchant_order_id": "987654321",       // ID de orden del merchant
  "preference_id": "USER-123-PREF-456",   // ID de preferencia
  "payment_type": "credit_card"           // Tipo de pago
}
```

## 🔍 Diagnóstico

### Función de Diagnóstico

La página incluye una función global `diagnoseMercadoPago()` que puedes ejecutar en la consola:

```javascript
diagnoseMercadoPago()
```

Esta función retorna:
- Disponibilidad del SDK de MercadoPago
- Estado de la instancia de MercadoPago
- Configuración de la clave pública
- ID de preferencia actual

### URLs de Retorno Configuradas

- **Success:** `/ecomerce/checkout/success`
- **Failure:** `/ecomerce/checkout/failure`
- **Pending:** `/ecomerce/checkout/pending`
- **Webhook:** `/ecomerce/checkout/webhook/mercadopago`

## 🐛 Solución de Problemas

### MercadoPago no se carga
- Verifica que la configuración esté correcta en el servidor
- Revisa la consola del navegador por errores de red
- Confirma que la clave pública esté configurada

### No se crea la preferencia
- Asegúrate de estar logueado (token válido)
- Verifica que el endpoint `/ecomerce/checkout/` esté funcionando
- Revisa los logs del servidor

### Parámetros no llegan
- MercadoPago puede estar bloqueado por extensiones del navegador
- Verifica que las URLs de retorno estén configuradas correctamente
- Revisa si hay problemas de CORS

## 📝 Notas Técnicas

- La página usa el **SDK v2** de MercadoPago
- Incluye **Wallet Brick** para una integración simplificada
- Tiene **manejo de errores** detallado
- **No incluye** otros métodos de pago para evitar interferencias
- Los estilos usan **Tailwind CSS** para una UI moderna

## 🎯 Próximos Pasos

Después de capturar los parámetros, puedes:

1. **Actualizar el webhook** para procesar los pagos correctamente
2. **Mejorar el manejo de estados** de pago
3. **Implementar lógica de negocio** basada en los parámetros recibidos
4. **Configurar notificaciones** al usuario según el estado del pago