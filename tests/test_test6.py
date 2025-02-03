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

@pytest.mark.parametrize("codigo_int_value", range(1, ITERATIONS + 1))
def test_create_test6(codigo_int_value):
    response = client.post("/test6/", json={
        "codigo_int": codigo_int_value,
        "nombre": f'Valor de prueba {codigo_int_value}',
        "descripcion": f'Valor de prueba {codigo_int_value}',
        "valor": 3.14 + codigo_int_value,
        "check": codigo_int_value % 2 == 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_int"] == codigo_int_value
    assert data["nombre"] == f"Valor de prueba {codigo_int_value}"
    assert data["descripcion"] == f"Valor de prueba {codigo_int_value}"
    assert data["valor"] == codigo_int_value % 2 == 0
    assert data["check"] == (codigo_int_value % 2 == 0)


@pytest.mark.parametrize("codigo_int_value", range(1, ITERATIONS + 1))
def test_gets_test6_all(codigo_int_value):
    response = client.get("/test6/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("codigo_int_value", range(1, ITERATIONS + 1))
def test_get_test6_by_id(codigo_int_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test6/id/{codigo_int_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test6/", json={
            "codigo_int": codigo_int_value,
            "nombre": f'Valor de prueba {codigo_int_value}',
            "descripcion": f'Valor de prueba {codigo_int_value}',
            "valor": 2.71 + codigo_int_value,
            "check": False,
        })
        response = client.get(f"/test6/id/{codigo_int_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["codigo_int"] == codigo_int_value


@pytest.mark.parametrize("codigo_int_value", range(1, ITERATIONS + 1))
def test_update_test6(codigo_int_value):
    response = client.put(f"/test6/id/{codigo_int_value}", json={
        "nombre": f'Valor actualizado {codigo_int_value}',
        "descripcion": f'Valor actualizado {codigo_int_value}',
        "valor": 1.61 + codigo_int_value,
        "check": codigo_int_value % 2 != 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == f"Valor actualizado {codigo_int_value}"
    assert data["descripcion"] == f"Valor actualizado {codigo_int_value}"
    assert data["valor"] == codigo_int_value % 2 != 0
    assert data["check"] == (codigo_int_value % 2 != 0)


@pytest.mark.parametrize("codigo_int_value", range(1, ITERATIONS + 1))
def test_delete_test6(codigo_int_value):
    response = client.delete(f"/test6/id/{codigo_int_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_int"] == codigo_int_value

    # Verificar que ya no existe
    response = client.get(f"/test6/id/{codigo_int_value}")
    assert response.status_code == 404


def test_create_test6_invalid():
    response = client.post("/test6/", json={
        "nombre": None,
        "descripcion": None,
        "valor": None,
        "check": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
