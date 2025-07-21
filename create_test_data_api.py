import requests
import json

def create_sample_locations():
    """Crear ubicaciones de prueba usando la API REST"""
    
    # URL base de la API
    base_url = "http://localhost:8000/app_obras/locations/"
    
    # Datos de ubicaciones de ejemplo
    locations_data = [
        {
            "name": "Centro Histórico de Buenos Aires",
            "city": "Buenos Aires",
            "country": "Argentina",
            "address": "Av. del Libertador 1473, CABA"
        },
        {
            "name": "Brooklyn Museum District",
            "city": "Nueva York",
            "country": "Estados Unidos",
            "address": "200 Eastern Pkwy, Brooklyn, NY 11238"
        },
        {
            "name": "Barrio de los Museos Madrid",
            "city": "Madrid",
            "country": "España",
            "address": "Calle de Santa Isabel, 52"
        },
        {
            "name": "Manhattan Art District",
            "city": "Nueva York",
            "country": "Estados Unidos",
            "address": "11 W 53rd St, Manhattan, NY 10019"
        },
        {
            "name": "Louvre District",
            "city": "París",
            "country": "Francia",
            "address": "Place du Carrousel, 75001 Paris"
        },
        {
            "name": "Bloomsbury Cultural Quarter",
            "city": "Londres",
            "country": "Reino Unido",
            "address": "Great Russell St, Bloomsbury, London WC1B 3DG"
        }
    ]
    
    print('=== CREANDO UBICACIONES DE PRUEBA VIA API ===')
    
    created_locations = []
    
    for location_data in locations_data:
        try:
            response = requests.post(base_url, json=location_data)
            
            if response.status_code == 201:
                created_location = response.json()
                created_locations.append(created_location)
                print(f'✓ Creada: {created_location["name"]} (ID: {created_location["id"]})')
            else:
                error_data = response.json()
                print(f'✗ Error al crear {location_data["name"]}: {error_data.get("detail", "Error desconocido")}')
                
        except requests.RequestException as e:
            print(f'✗ Error de conexión al crear {location_data["name"]}: {e}')
        except Exception as e:
            print(f'✗ Error inesperado al crear {location_data["name"]}: {e}')
    
    print(f'\n¡{len(created_locations)} ubicaciones creadas exitosamente!')
    
    # Mostrar resumen
    if created_locations:
        print('\n=== RESUMEN DE UBICACIONES CREADAS ===')
        for location in created_locations:
            print(f'- {location["name"]}: {location["city"]}, {location["country"]}')

def create_sample_institutions():
    """Crear instituciones de prueba usando la API REST"""
    
    # Primero obtener las ubicaciones disponibles
    try:
        locations_response = requests.get("http://localhost:8000/app_obras/locations/")
        if locations_response.status_code != 200:
            print("Error al obtener ubicaciones. Crear ubicaciones primero.")
            return
        
        locations = locations_response.json()
        if not locations:
            print("No hay ubicaciones disponibles. Crear ubicaciones primero.")
            return
            
    except Exception as e:
        print(f"Error al obtener ubicaciones: {e}")
        return
    
    # URL base de la API
    base_url = "http://localhost:8000/app_obras/institutions/"
    
    # Datos de instituciones de ejemplo
    institutions_data = [
        {
            "name": "Museo Nacional de Bellas Artes",
            "location_id": 1  # Buenos Aires
        },
        {
            "name": "Brooklyn Museum",
            "location_id": 2  # Nueva York
        },
        {
            "name": "Museo Reina Sofía",
            "location_id": 3  # Madrid
        },
        {
            "name": "Museum of Modern Art (MoMA)",
            "location_id": 4  # Nueva York
        },
        {
            "name": "Musée du Louvre",
            "location_id": 5  # París
        },
        {
            "name": "British Museum",
            "location_id": 6  # Londres
        }
    ]
    
    print('\n=== CREANDO INSTITUCIONES DE PRUEBA VIA API ===')
    
    created_institutions = []
    
    for institution_data in institutions_data:
        try:
            response = requests.post(base_url, json=institution_data)
            
            if response.status_code == 201:
                created_institution = response.json()
                created_institutions.append(created_institution)
                print(f'✓ Creada: {created_institution["name"]} (ID: {created_institution["id"]})')
            else:
                error_data = response.json()
                print(f'✗ Error al crear {institution_data["name"]}: {error_data.get("detail", "Error desconocido")}')
                
        except requests.RequestException as e:
            print(f'✗ Error de conexión al crear {institution_data["name"]}: {e}')
        except Exception as e:
            print(f'✗ Error inesperado al crear {institution_data["name"]}: {e}')
    
    print(f'\n¡{len(created_institutions)} instituciones creadas exitosamente!')

if __name__ == "__main__":
    print("Iniciando creación de datos de prueba...")
    
    # Crear ubicaciones primero
    create_sample_locations()
    
    # Luego crear instituciones
    create_sample_institutions()
    
    print("\n🎉 ¡Proceso completado!")
    print("\n📍 Puedes ver las ubicaciones en: http://localhost:8000/app_obras/locations/html/")
    print("🏛️ Puedes ver las instituciones en: http://localhost:8000/app_obras/institutions/html/")
