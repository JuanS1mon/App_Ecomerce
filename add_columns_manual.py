from db.database import get_db
from sqlalchemy import text

def add_columns_manually():
    db = next(get_db())
    
    try:
        # Agregar las columnas una por una con SQL directo
        alter_commands = [
            "ALTER TABLE Usuarios ADD telefono NVARCHAR(20) NULL;",
            "ALTER TABLE Usuarios ADD direccion NVARCHAR(255) NULL;",
            "ALTER TABLE Usuarios ADD fecha_nacimiento DATE NULL;",
            "ALTER TABLE Usuarios ADD imagen_perfil TEXT NULL;"
        ]
        
        for command in alter_commands:
            try:
                print(f"Ejecutando: {command}")
                db.execute(text(command))
                db.commit()
                print("✓ Ejecutado exitosamente")
            except Exception as e:
                print(f"Error en comando '{command}': {e}")
                db.rollback()
                
    except Exception as e:
        print(f"Error general: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_columns_manually()