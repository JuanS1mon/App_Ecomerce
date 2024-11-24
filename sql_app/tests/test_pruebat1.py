import sys
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

from ..main import app  # Asegúrate de importar tu aplicación FastAPI

client = TestClient(app)

# Definir el número de iteraciones
ITERATIONS = 10  # Puedes ajustar este valor según tus necesidades

@pytest.mark.parametrize("campot1_value", range(1, ITERATIONS + 1))
def test_create_pruebat1(campot1_value):
    response = client.post("/pruebat1/", json={
        "campot1": campot1_value,
        "campot2": f"Valor de prueba {campot1_value}",
        "campot3": 3.14 + campot1_value,
        "campot4": campot1_value % 2 == 0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["campot1"] == campot1_value
    assert data["campot2"] == f"Valor de prueba {campot1_value}"

@pytest.mark.parametrize("campot1_value", range(1, ITERATIONS + 1))
def test_gets_pruebat1_all(campot1_value):
    response = client.get("/pruebat1/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.parametrize("campot1_value", range(1, ITERATIONS + 1))
def test_get_pruebat1_campo1(campot1_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/pruebat1/id/{campot1_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/pruebat1/", json={
            "campot1": campot1_value,
            "campot2": f"Valor de prueba {campot1_value}",
            "campot3": 2.71 + campot1_value,
            "campot4": False
        })
        response = client.get(f"/pruebat1/id/{campot1_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["campot1"] == campot1_value
    assert data["campot2"] == f"Valor de prueba {campot1_value}"

@pytest.mark.parametrize("campot1_value", range(1, ITERATIONS + 1))
def test_update_pruebat1(campot1_value):
    response = client.put(f"/pruebat1/id/{campot1_value}", json={
        "campot2": f"Valor actualizado {campot1_value}",
        "campot3": 1.61 + campot1_value,
        "campot4": campot1_value % 2 != 0  # Cambiamos el valor booleano
    })
    assert response.status_code == 200
    data = response.json()
    assert data["campot2"] == f"Valor actualizado {campot1_value}"
    assert data["campot3"] == 1.61 + campot1_value
    assert data["campot4"] == (campot1_value % 2 != 0)

@pytest.mark.parametrize("campot1_value", range(1, ITERATIONS + 1))
def test_delete_pruebat1(campot1_value):
    response = client.delete(f"/pruebat1/id/{campot1_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["campot1"] == campot1_value

    # Verificar que ya no existe
    response = client.get(f"/pruebat1/id/{campot1_value}")
    assert response.status_code == 404

def test_create_pruebat1_invalid():
    # Intentar crear un registro con datos faltantes
    response = client.post("/pruebat1/", json={
        "campot2": "Sin campot1",
        "campot3": 0.0,
        "campot4": False
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_create_pruebat1_missing_required_fields():
    response = client.post("/pruebat1/", json={
        "campot2": "Sin campot1",  # Falta campot1 que es obligatorio
        "campot3": 0.0,
        "campot4": False
    })
    assert response.status_code == 422

def test_create_pruebat1_invalid_types():
    response = client.post("/pruebat1/", json={
        "campot1": "texto en lugar de entero",  # campot1 debería ser int
        "campot2": 123,  # campot2 debería ser str
        "campot3": "debería ser un número",
        "campot4": "no es booleano"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_create_pruebat1_sql_injection():
    response = client.post("/pruebat1/", json={
        "campot1": 9999,
        "campot2": "valor'; DROP TABLE pruebat1; --",
        "campot3": 1.0,
        "campot4": True
    })
    assert response.status_code == 200  # Debería tratar la entrada como texto normal
    # Eliminar el registro creado
    client.delete("/pruebat1/id/9999")

def test_create_pruebat1_boundary_values():
    response = client.post("/pruebat1/", json={
        "campot1": -1,  # Valor negativo
        "campot2": "Valor límite",
        "campot3": float('inf'),  # Infinito
        "campot4": True
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_create_pruebat1_unicode():
    response = client.post("/pruebat1/", json={
        "campot1": 10001,
        "campot2": "Prueba con acentos y caracteres especiales: ñ Á ü 😊",
        "campot3": 1.0,
        "campot4": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["campot2"] == "Prueba con acentos y caracteres especiales: ñ Á ü 😊"
    # Eliminar el registro creado
    client.delete("/pruebat1/id/10001")

def test_response_time():
    start_time = time.time()
    response = client.get("/pruebat1/")
    end_time = time.time()
    elapsed_time = end_time - start_time
    assert response.status_code == 200
    assert elapsed_time < 0.5  # Por ejemplo, menos de 500ms

