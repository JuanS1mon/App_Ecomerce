#!/usr/bin/env python3
"""Script para ver los datos en SQL con detalle"""

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sql_app.db.database import engine
import json

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def detailed_sql_inspection():
    """Inspección detallada de los datos en SQL"""
    print("=== INSPECCIÓN DETALLADA DE DATOS EN SQL ===\n")
    
    db = SessionLocal()
    try:
        # 1. Ver la estructura de la tabla artworks
        print("📋 ESTRUCTURA DE LA TABLA ARTWORKS:")
        result = db.execute(text("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'artworks'
            ORDER BY ORDINAL_POSITION
        """))
        
        for row in result:
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            length = f"({row[3]})" if row[3] else ""
            print(f"   {row[0]} - {row[1]}{length} {nullable}")
        
        print("\n" + "="*60 + "\n")
        
        # 2. Ver todos los datos de la obra creada
        print("🎨 DATOS COMPLETOS DE LA OBRA CREADA:")
        result = db.execute(text("""
            SELECT * FROM artworks WHERE id = 1
        """))
        
        # Obtener nombres de columnas
        columns = result.keys()
        row = result.fetchone()
        
        if row:
            print("   🗃️ REGISTRO COMPLETO:")
            for i, col_name in enumerate(columns):
                value = row[i]
                if isinstance(value, str) and len(value) > 80:
                    value = value[:77] + "..."
                print(f"      {col_name}: {value}")
        
        print("\n" + "="*60 + "\n")
        
        # 3. Ver las relaciones (JOIN con artistas y estados)
        print("🔗 DATOS CON RELACIONES (JOIN):")
        result = db.execute(text("""
            SELECT 
                a.id as obra_id,
                a.inventory_code,
                a.title,
                a.thumbnail_url,
                a.creation_year,
                a.is_available,
                art.id as artist_id,
                art.full_name as artist_name,
                s.id as state_id,
                s.description as state_description
            FROM artworks a
            LEFT JOIN artists art ON a.artist_id = art.id
            LEFT JOIN artwork_states s ON a.state_id = s.id
            WHERE a.id = 1
        """))
        
        row = result.fetchone()
        if row:
            print(f"   🆔 ID Obra: {row[0]}")
            print(f"   📋 Código: {row[1]}")
            print(f"   🎨 Título: {row[2]}")
            print(f"   🖼️ Imagen: {row[3]}")
            print(f"   📅 Año: {row[4]}")
            print(f"   ✅ Disponible: {row[5]}")
            print(f"   👨‍🎨 Artista: ID {row[6]} - {row[7]}")
            print(f"   🏷️ Estado: ID {row[8]} - {row[9]}")
        
        print("\n" + "="*60 + "\n")
        
        # 4. Verificar URLs de imagen
        print("🖼️ ANÁLISIS DE IMÁGENES:")
        result = db.execute(text("""
            SELECT 
                id,
                title,
                thumbnail_url,
                LEN(thumbnail_url) as url_length
            FROM artworks 
            WHERE thumbnail_url IS NOT NULL
        """))
        
        for row in result:
            print(f"   Obra ID {row[0]}: {row[1]}")
            print(f"      URL: {row[2]}")
            print(f"      Longitud URL: {row[3]} caracteres")
            
            # Verificar si la URL es válida
            if "/static/uploads/artworks/" in row[2]:
                print(f"      ✅ URL válida del sistema")
            else:
                print(f"      ⚠️ URL externa o formato no estándar")
        
        print("\n" + "="*60 + "\n")
        
        # 5. Estadísticas generales
        print("📊 ESTADÍSTICAS GENERALES:")
        
        # Total de obras
        result = db.execute(text("SELECT COUNT(*) FROM artworks"))
        total_obras = result.scalar()
        print(f"   📚 Total de obras: {total_obras}")
        
        # Obras con imagen
        result = db.execute(text("SELECT COUNT(*) FROM artworks WHERE thumbnail_url IS NOT NULL"))
        obras_con_imagen = result.scalar()
        print(f"   🖼️ Obras con imagen: {obras_con_imagen}")
        
        # Obras sin imagen
        obras_sin_imagen = total_obras - obras_con_imagen
        print(f"   📋 Obras sin imagen: {obras_sin_imagen}")
        
        # Porcentaje
        if total_obras > 0:
            porcentaje = (obras_con_imagen / total_obras) * 100
            print(f"   📈 Porcentaje con imagen: {porcentaje:.1f}%")
        
        print("\n" + "="*60 + "\n")
        
        # 6. Raw SQL data como JSON
        print("🔧 DATOS RAW (formato JSON):")
        result = db.execute(text("SELECT * FROM artworks WHERE id = 1"))
        columns = result.keys()
        row = result.fetchone()
        
        if row:
            data_dict = {}
            for i, col_name in enumerate(columns):
                value = row[i]
                # Convertir tipos no serializables
                if hasattr(value, 'isoformat'):  # datetime
                    value = value.isoformat()
                elif isinstance(value, bytes):
                    value = str(value)
                data_dict[col_name] = value
            
            print(json.dumps(data_dict, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    detailed_sql_inspection()
