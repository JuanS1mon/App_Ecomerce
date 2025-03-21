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

@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_create_rubros(codigo_value):
    response = client.post("/rubros/", json={
        "codigo": codigo_value,
        "test1": f'Valor de prueba {codigo_value}',
        "test2": 3.14 + codigo_value,
        "test3": codigo_value % 2 == 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value
    assert data["test1"] == f"Valor de prueba {codigo_value}"
    assert data["test2"] == codigo_value % 2 == 0
    assert data["test3"] == (codigo_value % 2 == 0)


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_gets_rubros_all(codigo_value):
    response = client.get("/rubros/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_get_rubros_by_id(codigo_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/rubros/id/{codigo_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/rubros/", json={
            "codigo": codigo_value,
            "test1": f'Valor de prueba {codigo_value}',
            "test2": 2.71 + codigo_value,
            "test3": False,
        })
        response = client.get(f"/rubros/id/{codigo_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_update_rubros(codigo_value):
    response = client.put(f"/rubros/id/{codigo_value}", json={
        "test1": f'Valor actualizado {codigo_value}',
        "test2": 1.61 + codigo_value,
        "test3": codigo_value % 2 != 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["test1"] == f"Valor actualizado {codigo_value}"
    assert data["test2"] == codigo_value % 2 != 0
    assert data["test3"] == (codigo_value % 2 != 0)


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_delete_rubros(codigo_value):
    response = client.delete(f"/rubros/id/{codigo_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value

    # Verificar que ya no existe
    response = client.get(f"/rubros/id/{codigo_value}")
    assert response.status_code == 404


def test_create_rubros_invalid():
    response = client.post("/rubros/", json={
        "test1": None,
        "test2": None,
        "test3": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
