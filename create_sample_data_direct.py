import sqlite3

def create_sample_data():
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    print('=== CREANDO DATOS DE PRUEBA DIRECTAMENTE ===')
    
    # Crear ubicaciones
    locations_data = [
        ('Buenos Aires', 'Argentina', 'Av. del Libertador 1473'),
        ('Nueva York', 'Estados Unidos', '200 Eastern Pkwy, Brooklyn'),
        ('Madrid', 'España', 'Calle de Santa Isabel, 52'),
        ('Nueva York', 'Estados Unidos', '11 W 53rd St, Manhattan'),
        ('París', 'Francia', 'Place du Carrousel'),
        ('Londres', 'Reino Unido', 'Great Russell St')
    ]
    
    print('--- Creando ubicaciones ---')
    for city, country, address in locations_data:
        try:
            cursor.execute(
                "INSERT INTO locations (city, country, address) VALUES (?, ?, ?)",
                (city, country, address)
            )
            print(f'✓ Ubicación: {city}, {country}')
        except sqlite3.IntegrityError:
            print(f'- Ya existe: {city}, {country}')
    
    # Crear instituciones
    institutions_data = [
        ('Museo Nacional de Bellas Artes', 1),
        ('Brooklyn Museum', 2),
        ('Museo Reina Sofía', 3),
        ('Museum of Modern Art (MoMA)', 4),
        ('Musée du Louvre', 5),
        ('British Museum', 6)
    ]
    
    print('\n--- Creando instituciones ---')
    for name, location_id in institutions_data:
        try:
            cursor.execute(
                "INSERT INTO institutions (name, location_id) VALUES (?, ?)",
                (name, location_id)
            )
            print(f'✓ Institución: {name}')
        except sqlite3.IntegrityError:
            print(f'- Ya existe: {name}')
    
    # Confirmar cambios
    conn.commit()
    
    # Verificar datos creados
    print('\n=== VERIFICACIÓN ===')
    cursor.execute("SELECT COUNT(*) FROM locations")
    locations_count = cursor.fetchone()[0]
    print(f'Total ubicaciones: {locations_count}')
    
    cursor.execute("SELECT COUNT(*) FROM institutions")
    institutions_count = cursor.fetchone()[0]
    print(f'Total instituciones: {institutions_count}')
    
    conn.close()
    print('\n¡Datos creados exitosamente!')

if __name__ == "__main__":
    create_sample_data()
