# Configuración de MercadoPago

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

## Paso 4: Configurar en el proyecto
1. Abre el archivo `.env` en la raíz del proyecto
2. Reemplaza `YOUR_ACCESS_TOKEN_HERE` con tu Access Token real:
   ```
   MERCADOPAGO_ACCESS_TOKEN=APP_USR-1234567890123456-123456-7890123456789abcd1234567890
   ```

## Paso 5: Probar la integración
1. Reinicia el servidor
2. Realiza un pedido con método de pago "mercadopago"
3. Deberías recibir un `payment_url` en la respuesta
4. Haz clic en el link para probar el pago

## Notas importantes
- El Access Token es sensible, nunca lo subas a repositorios públicos
- Para desarrollo, puedes usar el Access Token de pruebas inicialmente
- Asegúrate de que tu cuenta de MercadoPago esté verificada para recibir pagos reales
- Los webhooks se configuran en el panel de MercadoPago apuntando a tus endpoints de callback

## URLs de callback configuradas
- Success: `http://tu-dominio.com/checkout/success/{pedido_id}`
- Failure: `http://tu-dominio.com/checkout/failure/{pedido_id}`
- Pending: `http://tu-dominio.com/checkout/pending/{pedido_id}`