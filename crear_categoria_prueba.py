"""
Script para crear una categoría de prueba con imagen
"""
import os
import sys
sys.path.append('.')

from db.database import get_db, create_database
from Projects.ecomerce.models.categorias import EcomerceCategorias
from sqlalchemy.orm import Session

def crear_categoria_prueba():
    try:
        # Crear base de datos si no existe
        create_database()

        # Obtener sesión de base de datos
        db: Session = next(get_db())

        # Crear categoría de prueba con imagen
        categoria_prueba = EcomerceCategorias(
            nombre="Electrónica",
            descripcion="Computadoras, tablets, laptops y gadgets tecnológicos",
            imagen_url="/static/img/categorias/electronica.jpg",  # Imagen de ejemplo
            id_padre=0,
            active=True
        )

        # Verificar si ya existe
        existente = db.query(EcomerceCategorias).filter(EcomerceCategorias.nombre == "Electrónica").first()
        if existente:
            print("La categoría 'Electrónica' ya existe")
            return

        # Agregar a la base de datos
        db.add(categoria_prueba)
        db.commit()
        db.refresh(categoria_prueba)

        print(f"✅ Categoría 'Electrónica' creada exitosamente con ID: {categoria_prueba.id}")

    except Exception as e:
        print(f"❌ Error creando categoría de prueba: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crear_categoria_prueba()