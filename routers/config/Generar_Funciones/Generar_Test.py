def generate_tests(module_name, field_names, field_types):
    """
    Genera el código de pruebas para un módulo dado.
    """
    # Agregar importaciones y configuración inicial
    test_code = f"""import sys
import os
import time
import warnings
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Filtrar las advertencias específicas
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Añadir la ruta del directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..main import app  # Asegúrate de importar tu aplicación FastAPI correctamente

client = TestClient(app)

# Definir el número de iteraciones
ITERATIONS = 10  # Puedes ajustar este valor según tus necesidades
"""

    # Obtener el nombre del campo clave (asumiendo que es el primer campo)
    key_field = field_names[0]

    # Función test_create parametrizada
    test_code += f"""
@pytest.mark.parametrize("{key_field}_value", range(1, ITERATIONS + 1))
def test_create_{module_name}({key_field}_value):
    response = client.post("/{module_name}/", json={{
"""
    # Valores de prueba para creación
    for field_name, field_type in zip(field_names, field_types):
        if field_name == key_field:
            test_value = f"{key_field}_value"
        elif field_type == 'int':
            test_value = f"{key_field}_value * 10"
        elif field_type == 'str':
            test_value = f"f'Valor de prueba {{{key_field}_value}}'"
        elif field_type == 'float':
            test_value = f"3.14 + {key_field}_value"
        elif field_type == 'bool':
            test_value = f"{key_field}_value % 2 == 0"
        else:
            test_value = "None"
        test_code += f'        "{field_name}": {test_value},\n'
    test_code += f"""    }})
    assert response.status_code == 200
    data = response.json()
"""
    for field_name in field_names:
        if field_name == key_field:
            test_code += f'    assert data["{field_name}"] == {key_field}_value\n'
        elif field_types[field_names.index(field_name)] == 'str':
            test_code += f'    assert data["{field_name}"] == f"Valor de prueba {{{key_field}_value}}"\n'
        elif field_types[field_names.index(field_name)] == 'bool':
            test_code += f'    assert data["{field_name}"] == ({key_field}_value % 2 == 0)\n'
        else:
            test_code += f'    assert data["{field_name}"] == {test_value}\n'

    # Función test_gets_all parametrizada
    test_code += f"""

@pytest.mark.parametrize("{key_field}_value", range(1, ITERATIONS + 1))
def test_gets_{module_name}_all({key_field}_value):
    response = client.get("/{module_name}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
"""

    # Función test_get_by_id parametrizada
    test_code += f"""

@pytest.mark.parametrize("{key_field}_value", range(1, ITERATIONS + 1))
def test_get_{module_name}_by_id({key_field}_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/{module_name}/id/{{{key_field}_value}}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/{module_name}/", json={{
"""
    for field_name, field_type in zip(field_names, field_types):
        if field_name == key_field:
            test_value = f"{key_field}_value"
        elif field_type == 'int':
            test_value = f"{key_field}_value * 10"
        elif field_type == 'str':
            test_value = f"f'Valor de prueba {{{key_field}_value}}'"
        elif field_type == 'float':
            test_value = f"2.71 + {key_field}_value"
        elif field_type == 'bool':
            test_value = "False"
        else:
            test_value = "None"
        test_code += f'            "{field_name}": {test_value},\n'
    test_code += f"""        }})
        response = client.get(f"/{module_name}/id/{{{key_field}_value}}")

    assert response.status_code == 200
    data = response.json()
    assert data["{key_field}"] == {key_field}_value
"""

    # Función test_update parametrizada
    test_code += f"""

@pytest.mark.parametrize("{key_field}_value", range(1, ITERATIONS + 1))
def test_update_{module_name}({key_field}_value):
    response = client.put(f"/{module_name}/id/{{{key_field}_value}}", json={{
"""
    for field_name, field_type in zip(field_names, field_types):
        if field_name == key_field:
            continue  # No actualizamos el campo clave
        elif field_type == 'int':
            test_value = f"1.61 + {key_field}_value"
        elif field_type == 'str':
            test_value = f"f'Valor actualizado {{{key_field}_value}}'"
        elif field_type == 'float':
            test_value = f"1.61 + {key_field}_value"
        elif field_type == 'bool':
            test_value = f"{key_field}_value % 2 != 0"
        else:
            test_value = "None"
        test_code += f'        "{field_name}": {test_value},\n'
    test_code += f"""    }})
    assert response.status_code == 200
    data = response.json()
"""
    for field_name in field_names:
        if field_name == key_field:
            continue  # No actualizamos el campo clave
        elif field_types[field_names.index(field_name)] == 'str':
            test_code += f'    assert data["{field_name}"] == f"Valor actualizado {{{key_field}_value}}"\n'
        elif field_types[field_names.index(field_name)] == 'bool':
            test_code += f'    assert data["{field_name}"] == ({key_field}_value % 2 != 0)\n'
        else:
            test_code += f'    assert data["{field_name}"] == {test_value}\n'

    # Función test_delete parametrizada
    test_code += f"""

@pytest.mark.parametrize("{key_field}_value", range(1, ITERATIONS + 1))
def test_delete_{module_name}({key_field}_value):
    response = client.delete(f"/{module_name}/id/{{{key_field}_value}}")
    assert response.status_code == 200
    data = response.json()
    assert data["{key_field}"] == {key_field}_value

    # Verificar que ya no existe
    response = client.get(f"/{module_name}/id/{{{key_field}_value}}")
    assert response.status_code == 404
"""

    # Funciones adicionales de prueba (opcional)

    # Prueba para crear registro inválido
    test_code += f"""

def test_create_{module_name}_invalid():
    response = client.post("/{module_name}/", json={{
"""
    for field_name in field_names[1:]:  # Omite el campo clave
        test_code += f'        "{field_name}": None,\n'
    test_code += f"""    }})
    assert response.status_code == 422  # Unprocessable Entity
"""

    # Añadir otras pruebas según sea necesario...

    return test_code

# Ejemplo de uso de la función
if __name__ == "__main__":
    module_name = "pruebat1"
    field_names = ["campot1", "campot2", "campot3", "campot4"]
    field_types = ["int", "str", "float", "bool"]
    test_code = generate_tests(module_name, field_names, field_types)

    # Guardar el código generado en un archivo
    with open(f"test_{module_name}.py", "w", encoding="utf-8") as f:
        f.write(test_code)