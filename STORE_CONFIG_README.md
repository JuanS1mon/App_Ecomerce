# Configuración de la Tienda Ecommerce

## Cómo cambiar el nombre de la tienda

El nombre de la tienda está centralizado en un solo archivo para facilitar su modificación. Para cambiar el nombre de la tienda que aparece en todas las páginas:

### Método 1: Edición directa del archivo config.js

1. Abre el archivo `static/config.js`
2. Modifica la propiedad `name` en el objeto `STORE_CONFIG`:

```javascript
const STORE_CONFIG = {
    name: 'Tu Nuevo Nombre de Tienda',  // ← Cambia aquí
    description: 'Tu tienda online de confianza',
    // ... resto de configuración
};
```

### Método 2: Cambio dinámico desde la consola del navegador

Puedes cambiar el nombre de la tienda en tiempo real desde la consola del navegador:

```javascript
// Desde la consola del navegador en cualquier página
setStoreName('Mi Nueva Tienda Online');
```

Esto cambiará inmediatamente el nombre en todos los elementos que lo usan.

### Método 3: Prueba rápida

1. Abre cualquier página de la tienda (login, registro, productos)
2. Abre la consola del navegador (F12 → Console)
3. Ejecuta: `setStoreName('Mi Tienda Personalizada')`
4. Verás cómo el nombre cambia inmediatamente en headers, títulos, etc.

### Páginas que se actualizan automáticamente

Una vez que cambies el nombre en `config.js`, se actualizará automáticamente en:

- ✅ **Títulos de página** (login, registro, tienda de productos)
- ✅ **Headers y navegación**
- ✅ **Textos de bienvenida**
- ✅ **Cualquier elemento con `data-store-name`**
- ✅ **Títulos de pestaña del navegador**

### Elementos que requieren actualización manual

Algunos elementos pueden necesitar actualización manual si contienen texto hardcoded:

- Comentarios en CSS (ya actualizados)
- Meta descripciones
- Textos en plantillas del backend (si las hay)

### Ejemplos de nombres sugeridos

- "Mi Tienda Online"
- "Ecommerce Store"
- "Tienda Digital"
- "Marketplace Online"
- "Shop Online"
- "Store Pro"

### Archivos relacionados

- `static/config.js` - Configuración principal
- `static/ecommerce_login.html` - Página de login
- `static/ecommerce_register.html` - Página de registro
- `Projects/ecomerce/templates/productos_tienda.html` - Página de productos
- `ejemplo_cambio_nombre.js` - Ejemplos de uso

### Notas importantes

- El cambio se aplica inmediatamente en todas las páginas que incluyen `config.js`
- No es necesario reiniciar el servidor
- Los cambios se mantienen hasta que se modifique el archivo `config.js`
- El cambio dinámico desde consola es temporal (se pierde al recargar la página)