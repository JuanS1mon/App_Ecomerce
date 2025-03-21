# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY . /app

# Copia el archivo requirements.txt
COPY requirements.txt /app/requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que tu aplicación correrá
EXPOSE 8000

# Comando para correr la aplicación
CMD ["uvicorn", "sql_app.main:app", "--host", "0.0.0.0", "--port", "8000"]