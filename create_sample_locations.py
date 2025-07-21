from sql_app.db.database import get_db
from sql_app.Services.app_obras.locations.model_locations import Locations
from sql_app.Services.app_obras.locations.service_locations import create_locations

def create_sample_locations():
    db = next(get_db())
    
    # Datos de ubicaciones de ejemplo
    locations_data = [
        {
            'city': 'Buenos Aires',
            'country': 'Argentina',
            'address': 'Av. del Libertador 1473'
        },
        {
            'city': 'Nueva York',
            'country': 'Estados Unidos',
            'address': '200 Eastern Pkwy, Brooklyn'
        },
        {
            'city': 'Madrid',
            'country': 'España',
            'address': 'Calle de Santa Isabel, 52'
        },
        {
            'city': 'Nueva York',
            'country': 'Estados Unidos',
            'address': '11 W 53rd St, Manhattan'
        },
        {
            'city': 'París',
            'country': 'Francia',
            'address': 'Place du Carrousel'
        },
        {
            'city': 'Londres',
            'country': 'Reino Unido',
            'address': 'Great Russell St'
        }
    ]
    
    print('=== CREANDO UBICACIONES DE PRUEBA ===')
    
    for location_data in locations_data:
        try:
            location = Locations(**location_data)
            created_location = create_locations(db, location)
            print(f'✓ Creada: {created_location.city}, {created_location.country} (ID: {created_location.id})')
        except Exception as e:
            print(f'✗ Error al crear {location_data["city"]}: {e}')
    
    db.close()
    print('\n¡Ubicaciones creadas exitosamente!')

if __name__ == "__main__":
    create_sample_locations()
