def generate_tests(module_name, field_names, field_types):
    """
    Genera el código de pruebas para un módulo dado.
    """
    # Agregar importaciones y configuración inicial
    test_code = f"""import sys
import os
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Añadir la ruta del directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..main import app  # Asegúrate de importar tu aplicación FastAPI

client = TestClient(app)
"""

    # Definir la función run_tests
    test_code += f"""

def run_tests():
    start_time = time.time()
    iterations = 10  # Número de veces que se ejecutarán las pruebas

    for i in range(iterations):
        print(f"Ejecutando iteración {{i + 1}} de {{iterations}}")
        test_create_{module_name}()
        test_gets_{module_name}_all()
        test_get_{module_name}_by_id()
        test_update_{module_name}()
        test_delete_{module_name}()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Las pruebas se ejecutaron {{iterations}} veces en {{total_time:.2f}} segundos")
"""

    # Función test_create
    test_code += f"""

def test_create_{module_name}():
    response = client.post("/{module_name}/", json={{
"""
    # Valores de prueba para creación
    test_values = {}
    for field_name, field_type in zip(field_names, field_types):
        if field_type == 'int':
            test_value = 1
        elif field_type == 'str':
            test_value = "Valor de prueba"
        elif field_type == 'float':
            test_value = 3.14
        elif field_type == 'bool':
            test_value = True
        else:
            test_value = None
        test_values[field_name] = test_value
        test_code += f'        "{field_name}": {repr(test_value)},\n'
    test_code += f"""    }})
    assert response.status_code == 200
    data = response.json()
"""
    for field_name in field_names:
        test_code += f'    assert data["{field_name}"] == {repr(test_values[field_name])}\n'

    # Función test_gets_all
    test_code += f"""

def test_gets_{module_name}_all():
    response = client.get("/{module_name}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
"""

    # Función test_get_by_id
    test_code += f"""

def test_get_{module_name}_by_id():
    # Primero, creamos un registro de prueba
    client.post("/{module_name}/", json={{
"""
    # Valores de prueba para obtener por ID
    test_values_get = {}
    for field_name, field_type in zip(field_names, field_types):
        if field_type == 'int':
            test_value = 2
        elif field_type == 'str':
            test_value = "Otro valor"
        elif field_type == 'float':
            test_value = 2.71
        elif field_type == 'bool':
            test_value = False
        else:
            test_value = None
        test_values_get[field_name] = test_value
        test_code += f'        "{field_name}": {repr(test_value)},\n'
    test_code += f"""    }})
    # Luego, intentamos obtenerlo
    response = client.get("/{module_name}/{test_values_get[field_names[0]]}")
    assert response.status_code == 200
    data = response.json()
"""
    for field_name in field_names:
        test_code += f'    assert data["{field_name}"] == {repr(test_values_get[field_name])}\n'

    # Función test_update
    test_code += f"""

def test_update_{module_name}():
    # Primero, creamos el registro que vamos a actualizar
    response = client.post("/{module_name}/", json={{
"""
    test_values_update = {}
    for field_name, field_type in zip(field_names, field_types):
        if field_type == 'int':
            test_value = 3
        elif field_type == 'str':
            test_value = "Valor inicial"
        elif field_type == 'float':
            test_value = 2.71
        elif field_type == 'bool':
            test_value = False
        else:
            test_value = None
        test_values_update[field_name] = test_value
        test_code += f'        "{field_name}": {repr(test_value)},\n'
    test_code += f"""    }})
    assert response.status_code == 200

    # Ahora, actualizamos el registro con {field_names[0]} = {test_values_update[field_names[0]]}
    response = client.put("/{module_name}/{test_values_update[field_names[0]]}", json={{
"""
    # Valores actualizados
    updated_values = {}
    for field_name, field_type in zip(field_names, field_types):
        if field_name == field_names[0]:
            continue  # No actualizamos la clave primaria
        if field_type == 'int':
            updated_value = 4
        elif field_type == 'str':
            updated_value = "Valor actualizado"
        elif field_type == 'float':
            updated_value = 1.61
        elif field_type == 'bool':
            updated_value = True
        else:
            updated_value = None
        updated_values[field_name] = updated_value
        test_code += f'        "{field_name}": {repr(updated_value)},\n'
    test_code += f"""    }})
    assert response.status_code == 200
    data = response.json()
"""
    for field_name in updated_values:
        test_code += f'    assert data["{field_name}"] == {repr(updated_values[field_name])}\n'

    # Función test_delete
    test_code += f"""

def test_delete_{module_name}():
    # Eliminamos el registro con {field_names[0]} = {test_values_get[field_names[0]]}
    response = client.delete("/{module_name}/{test_values_get[field_names[0]]}")
    assert response.status_code == 200
    data = response.json()
    assert data["{field_names[0]}"] == {test_values_get[field_names[0]]}
    # Verificamos que ya no existe
    response = client.get("/{module_name}/{test_values_get[field_names[0]]}")
    assert response.status_code == 404
"""

    # Bloque principal para ejecutar las pruebas
    test_code += f"""

if __name__ == "__main__":
    run_tests()
"""

    return test_code