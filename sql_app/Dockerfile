# =========================================
# DOCKERFILE PARA APLICACIÓN FASTAPI
# =========================================

# Usar imagen base oficial de Python slim
FROM python:3.9-slim

# Información de metadata
LABEL maintainer="tu-email@tu-dominio.com"
LABEL version="2.0.0"
LABEL description="Sistema de Gestión de Stock - Aplicación FastAPI"

# Variables de entorno para optimización
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV TZ=America/Mexico_City

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias del sistema necesarias
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        unixodbc-dev \
        g++ \
        gcc \
        libc6-dev \
        wget \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Instalar Microsoft ODBC Driver 17 para SQL Server (versión corregida)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get remove -y unixodbc-dev \
    && ACCEPT_EULA=Y apt-get install -y --allow-downgrades msodbcsql17 mssql-tools unixodbc-dev \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/static /app/temp

# Copiar archivo de requerimientos primero (para mejor cache de Docker)
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn uvloop

# Copiar código de la aplicación
COPY sql_app/ /app/sql_app/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/
COPY .env* /app/

# Cambiar ownership al usuario no-root
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check mejorado
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Script de entrada para inicialización
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Punto de entrada
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando por defecto (puede ser sobrescrito)
CMD ["uvicorn", "sql_app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker"]