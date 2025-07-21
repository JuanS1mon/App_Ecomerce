from sql_app.db.database import get_db
from sql_app.Services.app_obras.locations.model_locations import Locations
from sql_app.Services.app_obras.locations.service_locations import create_locations
from sql_app.Services.app_obras.institutions.model_institutions import Institutions
from sql_app.Services.app_obras.institutions.service_institutions import create_institutions

def create_sample_locations_and_institutions():
    db = next(get_db())
    
    # Datos de ubicaciones de ejemplo
    locations_data = [
        {
            'name': 'Buenos Aires Centro',
            'city': 'Buenos Aires',
            'country': 'Argentina',
            'address': 'Centro de la ciudad'
        },
        {
            'name': 'Brooklyn Heights',
            'city': 'New York',
            'country': 'Estados Unidos',
            'address': 'Brooklyn, NY'
        },
        {
            'name': 'Centro Madrid',
            'city': 'Madrid',
            'country': 'España',
            'address': 'Centro histórico'
        },
        {
            'name': 'Manhattan',
            'city': 'New York',
            'country': 'Estados Unidos',
            'address': 'Manhattan, NY'
        },
        {
            'name': 'Zona Artística',
            'city': 'Ciudad Genérica',
            'country': 'País',
            'address': 'Distrito artístico'
        }
    ]
    
    print('=== CREANDO UBICACIONES DE PRUEBA ===')
    created_locations = []
    
    for location_data in locations_data:
        try:
            location = Locations(**location_data)
            created_location = create_locations(db, location)
            created_locations.append(created_location)
            print(f'✓ Creada ubicación: {created_location.name} (ID: {created_location.id})')
        except Exception as e:
            print(f'✗ Error al crear {location_data["name"]}: {e}')
    
    # Datos de instituciones de ejemplo
    institutions_data = [
        {
            'name': 'Museo Nacional de Bellas Artes',
            'location_id': created_locations[0].id if created_locations else 1
        },
        {
            'name': 'Brooklyn Museum',
            'location_id': created_locations[1].id if len(created_locations) > 1 else 1
        },
        {
            'name': 'Museo Reina Sofía',
            'location_id': created_locations[2].id if len(created_locations) > 2 else 1
        },
        {
            'name': 'Museum of Modern Art (MoMA)',
            'location_id': created_locations[3].id if len(created_locations) > 3 else 1
        },
        {
            'name': 'Galería de Arte Contemporáneo',
            'location_id': created_locations[4].id if len(created_locations) > 4 else 1
        }
    ]
    
    print('\n=== CREANDO INSTITUCIONES DE PRUEBA ===')
    
    for institution_data in institutions_data:
        try:
            institution = Institutions(**institution_data)
            created_institution = create_institutions(db, institution)
            print(f'✓ Creada institución: {created_institution.name} (ID: {created_institution.id})')
        except Exception as e:
            print(f'✗ Error al crear {institution_data["name"]}: {e}')
    
    db.close()
    print('\n¡Ubicaciones e instituciones creadas exitosamente!')

if __name__ == "__main__":
    create_sample_locations_and_institutions()
