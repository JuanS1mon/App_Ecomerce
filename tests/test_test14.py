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

@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_create_test14(codi_value):
    response = client.post("/test14/", json={
        "codi": codi_value,
        "valor": codi_value * 10,
        "valor2": 3.14 + codi_value,
        "nombre": f'Valor de prueba {codi_value}',
        "fecha": f'Valor de prueba {codi_value}',
        "validar": codi_value % 2 == 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value
    assert data["valor"] == codi_value % 2 == 0
    assert data["valor2"] == codi_value % 2 == 0
    assert data["nombre"] == f"Valor de prueba {codi_value}"
    assert data["fecha"] == f"Valor de prueba {codi_value}"
    assert data["validar"] == (codi_value % 2 == 0)


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_gets_test14_all(codi_value):
    response = client.get("/test14/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_get_test14_by_id(codi_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test14/id/{codi_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test14/", json={
            "codi": codi_value,
            "valor": codi_value * 10,
            "valor2": 2.71 + codi_value,
            "nombre": f'Valor de prueba {codi_value}',
            "fecha": f'Valor de prueba {codi_value}',
            "validar": False,
        })
        response = client.get(f"/test14/id/{codi_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_update_test14(codi_value):
    response = client.put(f"/test14/id/{codi_value}", json={
        "valor": 1.61 + codi_value,
        "valor2": 1.61 + codi_value,
        "nombre": f'Valor actualizado {codi_value}',
        "fecha": f'Valor actualizado {codi_value}',
        "validar": codi_value % 2 != 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["valor"] == codi_value % 2 != 0
    assert data["valor2"] == codi_value % 2 != 0
    assert data["nombre"] == f"Valor actualizado {codi_value}"
    assert data["fecha"] == f"Valor actualizado {codi_value}"
    assert data["validar"] == (codi_value % 2 != 0)


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_delete_test14(codi_value):
    response = client.delete(f"/test14/id/{codi_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value

    # Verificar que ya no existe
    response = client.get(f"/test14/id/{codi_value}")
    assert response.status_code == 404


def test_create_test14_invalid():
    response = client.post("/test14/", json={
        "valor": None,
        "valor2": None,
        "nombre": None,
        "fecha": None,
        "validar": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
