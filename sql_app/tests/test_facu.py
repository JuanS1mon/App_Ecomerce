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
def test_create_facu(id_value):
    response = client.post("/facu/", json={
        "id": id_value,
        "asd": f'Valor de prueba {id_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value
    assert data["asd"] == f"Valor de prueba {id_value}"


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_gets_facu_all(id_value):
    response = client.get("/facu/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_get_facu_by_id(id_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/facu/id/{id_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/facu/", json={
            "id": id_value,
            "asd": f'Valor de prueba {id_value}',
        })
        response = client.get(f"/facu/id/{id_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_update_facu(id_value):
    response = client.put(f"/facu/id/{id_value}", json={
        "asd": f'Valor actualizado {id_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["asd"] == f"Valor actualizado {id_value}"


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_delete_facu(id_value):
    response = client.delete(f"/facu/id/{id_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value

    # Verificar que ya no existe
    response = client.get(f"/facu/id/{id_value}")
    assert response.status_code == 404


def test_create_facu_invalid():
    response = client.post("/facu/", json={
        "asd": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
