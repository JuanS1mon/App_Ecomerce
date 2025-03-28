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

@pytest.mark.parametrize("tetwe_value", range(1, ITERATIONS + 1))
def test_create_familias(tetwe_value):
    response = client.post("/familias/", json={
        "tetwe": tetwe_value,
        "asd": f'Valor de prueba {tetwe_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["tetwe"] == tetwe_value
    assert data["asd"] == f"Valor de prueba {tetwe_value}"


@pytest.mark.parametrize("tetwe_value", range(1, ITERATIONS + 1))
def test_gets_familias_all(tetwe_value):
    response = client.get("/familias/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("tetwe_value", range(1, ITERATIONS + 1))
def test_get_familias_by_id(tetwe_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/familias/id/{tetwe_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/familias/", json={
            "tetwe": tetwe_value,
            "asd": f'Valor de prueba {tetwe_value}',
        })
        response = client.get(f"/familias/id/{tetwe_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["tetwe"] == tetwe_value


@pytest.mark.parametrize("tetwe_value", range(1, ITERATIONS + 1))
def test_update_familias(tetwe_value):
    response = client.put(f"/familias/id/{tetwe_value}", json={
        "asd": f'Valor actualizado {tetwe_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["asd"] == f"Valor actualizado {tetwe_value}"


@pytest.mark.parametrize("tetwe_value", range(1, ITERATIONS + 1))
def test_delete_familias(tetwe_value):
    response = client.delete(f"/familias/id/{tetwe_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["tetwe"] == tetwe_value

    # Verificar que ya no existe
    response = client.get(f"/familias/id/{tetwe_value}")
    assert response.status_code == 404


def test_create_familias_invalid():
    response = client.post("/familias/", json={
        "asd": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
