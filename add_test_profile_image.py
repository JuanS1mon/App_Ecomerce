#!/usr/bin/env python3
"""
Script para agregar una imagen de perfil de prueba al usuario 'juan'
"""
import base64
from sql_app.db.database import get_db
from sql_app.db.models.config.usuarios import Usuarios
from sqlalchemy.orm import Session

def create_test_avatar():
    """Crear un avatar simple en base64 para pruebas"""
    # SVG simple de un avatar
    svg_content = '''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="50" fill="#4F46E5"/>
    <circle cx="50" cy="35" r="15" fill="white"/>
    <ellipse cx="50" cy="75" rx="20" ry="15" fill="white"/>
    <text x="50" y="55" font-family="Arial" font-size="24" fill="#4F46E5" text-anchor="middle">J</text>
</svg>'''
    
    # Convertir SVG a base64
    svg_bytes = svg_content.encode('utf-8')
    base64_image = base64.b64encode(svg_bytes).decode('utf-8')
    return base64_image

def update_user_profile_image():
    """Actualizar la imagen de perfil del usuario juan"""
    db = next(get_db())
    
    try:
        # Buscar el usuario 'juan'
        user = db.query(Usuarios).filter(Usuarios.usuario == 'juan').first()
        
        if not user:
            print("❌ Usuario 'juan' no encontrado")
            return
        
        # Crear imagen de prueba
        test_image = create_test_avatar()
        
        # Actualizar imagen de perfil
        user.imagen_perfil = test_image
        
        db.commit()
        print("✅ Imagen de perfil agregada exitosamente al usuario 'juan'")
        print(f"📏 Tamaño de imagen: {len(test_image)} caracteres")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_user_profile_image()