# Sistema de Checkout MercadoPago - Documentación Completa

## 📋 Resumen

Este documento describe el sistema completo de integración con MercadoPago, incluyendo el checkout de prueba, las páginas de resultado y el análisis de parámetros.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **Página de Checkout de Prueba** (`/checkout/mercadopago/test`)
   - Página dedicada exclusivamente para MercadoPago
   - Agrega automáticamente un producto al carrito
   - Crea preferencia de pago y muestra el brick

2. **Páginas de Resultado**
   - **Success** (`/checkout/success`): Pago exitoso
   - **Failure** (`/checkout/failure`): Pago rechazado
   - **Pending** (`/checkout/pending`): Pago pendiente

3. **API Endpoints**
   - `POST /ecomerce/checkout/`: Crear preferencia de pago
   - `POST /ecomerce/checkout/webhook/mercadopago`: Webhook para notificaciones
   - `GET /ecomerce/checkout/config/mercadopago`: Configuración de MP

## 🔍 Parámetros de MercadoPago Analizados

### Parámetros Principales

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `collection_id` | ID único de la colección/cobro | `123456789` |
| `collection_status` | Estado del cobro | `approved`, `rejected`, `pending` |
| `payment_id` | ID único del pago | `987654321` |
| `status` | Estado general del pago | `approved`, `rejected`, `pending` |
| `external_reference` | Referencia externa (ID del pedido) | `1028` |
| `payment_type` | Tipo de medio de pago | `credit_card`, `debit_card`, etc. |
| `merchant_order_id` | ID de la orden del mercante | `456789123` |
| `preference_id` | ID de la preferencia de pago | `168706559-xxx` |
| `site_id` | ID del sitio/país | `MLA` (Argentina) |
| `processing_mode` | Modo de procesamiento | `aggregator` |
| `merchant_account_id` | ID de la cuenta del mercante | `168706559` |

### Estados de Pago

- **`approved`**: Pago aprobado exitosamente
- **`rejected`**: Pago rechazado (fondos insuficientes, tarjeta bloqueada, etc.)
- **`pending`**: Pago pendiente de confirmación
- **`cancelled`**: Pago cancelado por el usuario
- **`in_process`**: Pago en proceso de validación

## 🚀 Cómo Usar el Sistema

### 1. Iniciar el Servidor

```bash
uvicorn main:app --reload
```

### 2. Probar el Checkout

```bash
python test_checkout_mercadopago.py
```

Este script:
- Abre la página de checkout de prueba
- Agrega automáticamente un producto al carrito
- Crea la preferencia de MercadoPago
- Muestra el brick de pago

### 3. Probar las Páginas de Resultado

```bash
python test_checkout_results.py
```

Este script abre las tres páginas de resultado con parámetros de ejemplo.

## 📊 Análisis de Parámetros

### Página de Success
- Muestra todos los parámetros en formato visual
- Resalta los parámetros importantes
- Incluye información del pedido desde la base de datos
- Funciones de diagnóstico: `diagnoseSuccessPage()`

### Página de Failure
- Muestra el estado de error
- Explica posibles causas del rechazo
- Incluye opción para reintentar el pago
- Funciones de diagnóstico: `diagnoseFailurePage()`

### Página de Pending
- Indica que el pago está siendo procesado
- Muestra estado actual del pedido
- Incluye enlace para verificar estado
- Funciones de diagnóstico: `diagnosePendingPage()`

## 🔧 Configuración de MercadoPago

### Variables de Entorno Requeridas

```env
MERCADOPAGO_ACCESS_TOKEN=tu_access_token_aqui
MERCADOPAGO_PUBLIC_KEY=tu_public_key_aqui
MERCADOPAGO_WEBHOOK_SECRET=tu_webhook_secret_aqui
```

### URLs de Redirección Configuradas

```python
back_urls = {
    'success': 'http://localhost:8000/ecomerce/checkout/success',
    'failure': 'http://localhost:8000/ecomerce/checkout/failure',
    'pending': 'http://localhost:8000/ecomerce/checkout/pending'
}
```

## 📝 Logs y Depuración

### Información Registrada

Cada página de resultado registra en consola:
- URL completa con parámetros
- Timestamp de recepción
- Todos los parámetros GET recibidos
- Información adicional del pedido (si está disponible)

### Funciones Globales de Diagnóstico

En cada página, puedes ejecutar en la consola del navegador:

```javascript
// Página de éxito
diagnoseSuccessPage()

// Página de error
diagnoseFailurePage()

// Página pendiente
diagnosePendingPage()
```

## 🔄 Flujo Completo de Pago

1. **Usuario inicia checkout** → Página de prueba
2. **Sistema agrega producto** → Carrito actualizado
3. **Creación de preferencia** → MercadoPago genera preference_id
4. **Usuario paga** → Redirección a MercadoPago
5. **MercadoPago procesa** → Envía resultado a back_urls
6. **Usuario regresa** → Página de resultado correspondiente
7. **Sistema captura parámetros** → Logs y análisis completo

## 📋 Checklist de Verificación

- [x] Página de checkout de prueba creada
- [x] Producto agregado automáticamente al carrito
- [x] Preferencia de MercadoPago creada correctamente
- [x] Brick de MercadoPago renderizado
- [x] Páginas de resultado (success/failure/pending) implementadas
- [x] Captura completa de parámetros GET
- [x] Análisis visual de parámetros importantes
- [x] Funciones de diagnóstico implementadas
- [x] Logs detallados en consola
- [x] URLs de redirección configuradas
- [x] Webhook endpoint disponible

## 🎯 Próximos Pasos

1. **Implementar webhook processing** para notificaciones en tiempo real
2. **Actualizar estado de pedidos** basado en notificaciones de MP
3. **Agregar validación de firmas** para webhooks
4. **Implementar reintentos automáticos** para pagos pendientes
5. **Agregar métricas y analytics** de conversiones de pago

## 📞 Soporte

Para debugging adicional:
- Revisa los logs del servidor en la consola
- Usa las funciones de diagnóstico en el navegador
- Verifica la configuración de MercadoPago en `/ecomerce/checkout/config/mercadopago`
- Consulta la documentación oficial de MercadoPago para más detalles sobre parámetros