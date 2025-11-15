## ✅ Checklist Previo al Deployment

Antes de hacer push a GitHub y desplegar:

- [ ] **Variables de entorno verificadas**: Copiar `.env.example` como `.env` y completar todos los valores
- [ ] **Credenciales de producción listas**: Secret key seguro, credenciales de Azure SQL
- [ ] **Base de datos preparada**: Azure SQL Database creada y accesible
- [ ] **Verificar .gitignore**: El archivo `.env` NO debe subirse a GitHub
- [ ] **Commit de cambios**: `git add . && git commit -m "Ready for Azure deployment"`
- [ ] **Push a GitHub**: `git push origin main`

## 📝 Checklist Durante el Deployment en Azure

- [ ] **App Service creado**: Runtime Python 3.11, Linux
- [ ] **GitHub conectado**: Deployment Center configurado con tu repositorio
- [ ] **Variables de entorno configuradas**: Todas las variables del `.env` agregadas en Configuration
- [ ] **Connection strings agregadas**: Si usas Azure SQL Database
- [ ] **Firewall configurado**: Azure SQL permite conexiones desde Azure services

## 🧪 Checklist Post-Deployment

- [ ] **Aplicación accesible**: `https://tu-app.azurewebsites.net` carga correctamente
- [ ] **API funciona**: `/docs` muestra la documentación
- [ ] **Logs revisados**: No hay errores críticos en Log Stream
- [ ] **Base de datos conectada**: Las operaciones CRUD funcionan
- [ ] **Autenticación funciona**: Login/registro operativos

## 🔄 Para Actualizaciones Futuras

```bash
git add .
git commit -m "Nueva funcionalidad"
git push origin main
# Azure detectará el cambio y desplegará automáticamente
```
