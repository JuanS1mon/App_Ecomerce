from sql_app.db.database import get_db
from sql_app.Services.app_obras.institutions.model_institutions import Institutions
from sql_app.Services.app_obras.institutions.service_institutions import create_institutions

def create_sample_institutions():
    db = next(get_db())
    
    # Datos de instituciones de ejemplo
    institutions_data = [
        {
            'name': 'Museo Nacional de Bellas Artes',
            'address': 'Av. del Libertador 1473, Buenos Aires',
            'contact_info': 'info@mnba.gob.ar | +54 11 5288-9900'
        },
        {
            'name': 'Brooklyn Museum',
            'address': '200 Eastern Pkwy, Brooklyn, NY 11238',
            'contact_info': 'info@brooklynmuseum.org | +1 718-638-5000'
        },
        {
            'name': 'Museo Reina Sofía',
            'address': 'Calle de Santa Isabel, 52, Madrid',
            'contact_info': 'info@museoreinasofia.es | +34 917 741 000'
        },
        {
            'name': 'Museum of Modern Art (MoMA)',
            'address': '11 W 53rd St, New York, NY 10019',
            'contact_info': 'info@moma.org | +1 212-708-9400'
        },
        {
            'name': 'Galería de Arte Contemporáneo',
            'address': 'Calle Falsa 123, Ciudad',
            'contact_info': 'contacto@galeria.com | +1 555-0123'
        }
    ]
    
    print('=== CREANDO INSTITUCIONES DE PRUEBA ===')
    
    for institution_data in institutions_data:
        try:
            institution = Institutions(**institution_data)
            created_institution = create_institutions(db, institution)
            print(f'✓ Creada: {created_institution.name} (ID: {created_institution.id})')
        except Exception as e:
            print(f'✗ Error al crear {institution_data["name"]}: {e}')
    
    db.close()
    print('\n¡Instituciones creadas exitosamente!')

if __name__ == "__main__":
    create_sample_institutions()
