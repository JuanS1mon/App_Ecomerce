#!/usr/bin/env python3

from sql_app.db.database import get_db
from sqlalchemy import text

db = next(get_db())
result = db.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'depositos'")).fetchone()
print('Tabla depositos existe' if result else 'Tabla depositos NO existe')

# Si no existe, crearla
if not result:
    print("Creando tabla depositos...")
    create_sql = """
    CREATE TABLE depositos (
        id int IDENTITY(1,1) PRIMARY KEY,
        nombre varchar(100) NOT NULL,
        descripcion varchar(255) NULL,
        activo bit DEFAULT 1
    )
    """
    db.execute(text(create_sql))
    db.commit()
    
    # Insertar un depósito por defecto
    insert_sql = "INSERT INTO depositos (nombre, descripcion) VALUES ('Principal', 'Depósito principal')"
    db.execute(text(insert_sql))
    db.commit()
    print("Tabla depositos creada con depósito por defecto")

db.close()
