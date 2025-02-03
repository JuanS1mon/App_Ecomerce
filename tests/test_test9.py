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

from ..main import app  # Asegúrate de importar tu aplicación FastAPI correctamente

client = TestClient(app)

# Definir el número de iteraciones
ITERATIONS = 10  # Puedes ajustar este valor según tus necesidades

@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_create_test9(id_value):
    response = client.post("/test9/", json={
        "id": id_value,
        "nombre": f'Valor de prueba {id_value}',
        "fecha": f'Valor de prueba {id_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value
    assert data["nombre"] == f"Valor de prueba {id_value}"
    assert data["fecha"] == f"Valor de prueba {id_value}"


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_gets_test9_all(id_value):
    response = client.get("/test9/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_get_test9_by_id(id_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test9/id/{id_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test9/", json={
            "id": id_value,
            "nombre": f'Valor de prueba {id_value}',
            "fecha": f'Valor de prueba {id_value}',
        })
        response = client.get(f"/test9/id/{id_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_update_test9(id_value):
    response = client.put(f"/test9/id/{id_value}", json={
        "nombre": f'Valor actualizado {id_value}',
        "fecha": f'Valor actualizado {id_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == f"Valor actualizado {id_value}"
    assert data["fecha"] == f"Valor actualizado {id_value}"


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_delete_test9(id_value):
    response = client.delete(f"/test9/id/{id_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value

    # Verificar que ya no existe
    response = client.get(f"/test9/id/{id_value}")
    assert response.status_code == 404


def test_create_test9_invalid():
    response = client.post("/test9/", json={
        "nombre": None,
        "fecha": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
