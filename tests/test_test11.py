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
def test_create_test11(codigo_value):
    response = client.post("/test11/", json={
        "codigo": codigo_value,
        "nombre": f'Valor de prueba {codigo_value}',
        "de": 3.14 + codigo_value,
        "ea": codigo_value % 2 == 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value
    assert data["nombre"] == f"Valor de prueba {codigo_value}"
    assert data["de"] == codigo_value % 2 == 0
    assert data["ea"] == (codigo_value % 2 == 0)


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_gets_test11_all(codigo_value):
    response = client.get("/test11/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_get_test11_by_id(codigo_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test11/id/{codigo_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test11/", json={
            "codigo": codigo_value,
            "nombre": f'Valor de prueba {codigo_value}',
            "de": 2.71 + codigo_value,
            "ea": False,
        })
        response = client.get(f"/test11/id/{codigo_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_update_test11(codigo_value):
    response = client.put(f"/test11/id/{codigo_value}", json={
        "nombre": f'Valor actualizado {codigo_value}',
        "de": 1.61 + codigo_value,
        "ea": codigo_value % 2 != 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == f"Valor actualizado {codigo_value}"
    assert data["de"] == codigo_value % 2 != 0
    assert data["ea"] == (codigo_value % 2 != 0)


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_delete_test11(codigo_value):
    response = client.delete(f"/test11/id/{codigo_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value

    # Verificar que ya no existe
    response = client.get(f"/test11/id/{codigo_value}")
    assert response.status_code == 404


def test_create_test11_invalid():
    response = client.post("/test11/", json={
        "nombre": None,
        "de": None,
        "ea": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
