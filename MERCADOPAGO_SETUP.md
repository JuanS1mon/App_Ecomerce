# Configuración Completa de MercadoPago

## Variables de Entorno Requeridas

Para que la integración de MercadoPago funcione correctamente, necesitas configurar las siguientes variables de entorno:

### Variables Obligatorias

```bash
# Token de acceso de MercadoPago (producción o test)
MERCADOPAGO_ACCESS_TOKEN=APP_USR-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Clave secreta para validar webhooks (opcional pero recomendado)
MERCADOPAGO_WEBHOOK_SECRET=your_webhook_secret_here

# URL base de tu aplicación (para webhooks y redirecciones)
BASE_URL=https://tu-dominio.com
```

### Variables para Desarrollo Local

```bash
# Para desarrollo local
MERCADOPAGO_ACCESS_TOKEN=TEST-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
MERCADOPAGO_WEBHOOK_SECRET=your_test_webhook_secret_here
BASE_URL=http://localhost:8000
```

## Paso 1: Crear cuenta en MercadoPago
1. Ve a [https://www.mercadopago.com.ar/](https://www.mercadopago.com.ar/)
2. Regístrate como vendedor si no tienes cuenta
3. Verifica tu cuenta completando los datos requeridos

## Paso 2: Crear aplicación
1. Ve al [Panel de Desarrolladores](https://www.mercadopago.com.ar/developers/panel)
2. Haz clic en "Crear aplicación"
3. Selecciona "Pagos" como tipo de aplicación
4. Completa los datos de tu aplicación

## Paso 3: Obtener Access Token
1. En tu aplicación, ve a la sección "Credenciales"
2. Copia el "Access Token" de **producción**
3. **IMPORTANTE**: Nunca uses el Access Token de pruebas en producción

## Paso 4: Configurar Webhook Secret (Recomendado)
1. En tu aplicación, ve a "Webhooks" > "Configurar notificaciones"
2. Selecciona la pestaña "Modo productivo"
3. Selecciona el evento "Pagos"
4. La clave secreta se genera automáticamente al guardar
5. Copia la clave secreta para `MERCADOPAGO_WEBHOOK_SECRET`

## Paso 5: Configurar en el proyecto
1. Abre el archivo `.env` en la raíz del proyecto
2. Agrega las variables de entorno:
   ```bash
   MERCADOPAGO_ACCESS_TOKEN=APP_USR-1234567890123456-123456-7890123456789abcd1234567890
   MERCADOPAGO_WEBHOOK_SECRET=tu_clave_secreta_aqui
   BASE_URL=https://tu-dominio.com
   ```

## Paso 6: Probar la integración
1. Reinicia el servidor
2. Realiza un pedido con método de pago "mercadopago"
3. Deberías recibir un `preference_id` en la respuesta
4. El sistema crea automáticamente la URL de webhook por preferencia

## Estados de Pedido con MercadoPago

Los pedidos con MercadoPago pasan por los siguientes estados:

- `pendiente`: Pedido creado, esperando pago (carrito permanece activo)
- `pagado`: Pago aprobado, carrito se marca como completado
- `pendiente_pago`: Pago iniciado pero no completado
- `procesando_pago`: Pago en proceso de validación
- `pago_rechazado`: Pago rechazado por MercadoPago
- `pago_cancelado`: Pago cancelado por el usuario
- `reembolsado`: Pago reembolsado

## Endpoints Implementados

### Webhook Principal (con validación HMAC-SHA256)
```
POST /ecomerce/checkout/webhook/mercadopago
```
- Recibe notificaciones de cambios en el estado de pagos
- Valida firma HMAC-SHA256 para seguridad
- Actualiza automáticamente el estado de pedidos

### Endpoints de Redirección
```
GET /ecomerce/checkout/success?payment_id=...&status=...&external_reference=...
GET /ecomerce/checkout/failure?payment_id=...&status=...&external_reference=...
GET /ecomerce/checkout/pending?payment_id=...&status=...&external_reference=...
```
- Páginas informativas para usuarios después del pago
- Auto-redirección a tienda o pedidos

## Seguridad Implementada

- **Validación HMAC-SHA256**: Los webhooks se validan usando firma digital
- **External Reference**: Cada pago está vinculado a un pedido específico
- **Verificación de Estados**: Solo pagos aprobados completan el carrito
- **Timeouts**: Protección contra bloqueos de red

## Testing

Para probar la integración completa:

1. Usa credenciales de TEST inicialmente
2. Realiza pagos con tarjetas de prueba de MercadoPago
3. Verifica que los webhooks se reciban y procesen correctamente
4. Confirma que los estados de pedido se actualicen apropiadamente
5. Prueba diferentes escenarios: aprobado, rechazado, pendiente

## Notas importantes

- El Access Token y Webhook Secret son sensibles, nunca los subas a repositorios públicos
- Para desarrollo, puedes usar el Access Token de pruebas inicialmente
- Asegúrate de que tu cuenta de MercadoPago esté verificada para recibir pagos reales
- Los webhooks se configuran automáticamente por preferencia de pago (tiene prioridad sobre configuración global)
- La integración maneja automáticamente errores de "tracking prevention" del navegador