# 🚀 COMANDOS UVICORN - SISTEMA DE STOCK

## 📋 Comando Principal para Desarrollo

### **Comando Recomendado:**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info
```

### **¿Por qué este comando?**

| Parámetro | Descripción | Beneficio |
|-----------|-------------|-----------|
| `main:app` | Aplicación principal completa | Todas las funcionalidades disponibles |
| `--host 127.0.0.1` | Solo acceso local | Seguridad durante desarrollo |
| `--port 8000` | Puerto estándar | Puerto configurado en el proyecto |
| `--reload` | Recarga automática | Cambios de código se reflejan inmediatamente |
| `--log-level info` | Nivel de logging informativo | Balance entre detalle y ruido |

### **¿Cuándo usar cada comando?**

#### 🔧 **Para Desarrollo Diario:**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info
```
- ✅ Desarrollo normal con todas las funcionalidades
- ✅ Recarga automática de cambios
- ✅ Logs informativos sin spam

#### 🧪 **Para Pruebas Rápidas (Servidor Simplificado):**
```bash
uvicorn main_simple:app --host 127.0.0.1 --port 8001 --reload
```
- ✅ Evita problemas de migraciones de Alembic
- ✅ Solo Editor Visual y Generador
- ✅ Puerto diferente para evitar conflictos

#### 🐛 **Para Debug Detallado:**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level debug --access-log
```
- ✅ Logs muy detallados
- ✅ Registro de todas las peticiones HTTP
- ✅ Ideal para diagnosticar problemas

#### 🌐 **Para Pruebas en Red Local:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
```
- ✅ Acceso desde otras máquinas en la red
- ✅ Pruebas desde móviles/tablets
- ✅ Colaboración en equipo

## 🔍 **Explicación de Parámetros Adicionales:**

### **Hosts:**
- `127.0.0.1` - Solo acceso local (más seguro)
- `0.0.0.0` - Acceso desde la red (para pruebas remotas)

### **Puertos Comunes:**
- `8000` - Puerto principal del proyecto
- `8001` - Puerto alternativo (servidor simplificado)
- `8080` - Puerto alternativo común

### **Niveles de Log:**
- `critical` - Solo errores críticos
- `error` - Solo errores
- `warning` - Errores y advertencias (recomendado para producción)
- `info` - Información general (recomendado para desarrollo)
- `debug` - Máximo detalle (para debugging)

### **Opciones de Reload:**
- `--reload` - Recarga cuando cambia cualquier archivo Python
- `--reload-dir sql_app` - Solo recarga cambios en directorio específico
- `--reload-exclude "*.log"` - Excluye tipos de archivo del reload

## 🛠️ **Comandos Especializados:**

### **Para Análisis de Performance:**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info --access-log --loop uvloop
```

### **Para Máximo Performance (Desarrollo):**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --workers 1 --loop uvloop
```

### **Para Desarrollo con SSL (HTTPS):**
```bash
uvicorn main:app --host 127.0.0.1 --port 8443 --reload --ssl-keyfile key.pem --ssl-certfile cert.pem
```

## 📝 **Notas Importantes:**

1. **Activar entorno virtual primero:**
   ```bash
   & C:/Users/PCJuan/Desktop/sql_app/sql_app/env/Scripts/Activate.ps1
   ```

2. **Directorio de trabajo:**
   ```bash
   cd C:\Users\PCJuan\Desktop\sql_app
   ```

3. **Verificar que el puerto esté libre:**
   ```bash
   netstat -ano | findstr :8000
   ```

4. **Detener servidor:**
   - `Ctrl+C` en el terminal
   - O cerrar la ventana del terminal

## 🚨 **Solución de Problemas Comunes:**

### **Error: Puerto ocupado**
```bash
# Verificar qué usa el puerto
netstat -ano | findstr :8000

# Matar proceso si es necesario
taskkill /f /pid [PID_NUMBER]
```

### **Error: Módulo no encontrado**
```bash
# Verificar entorno virtual activado
which python
pip list
```

### **Error: Alembic migration**
```bash
# Usar servidor simplificado
uvicorn main_simple:app --host 127.0.0.1 --port 8001 --reload
```

---

**Fecha de creación:** 5 de octubre de 2025  
**Proyecto:** Sistema de Stock - SQL App  
**Autor:** Documentación automática del sistema