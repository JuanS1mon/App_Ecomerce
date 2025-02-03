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

@pytest.mark.parametrize("cod_value", range(1, ITERATIONS + 1))
def test_create_test13(cod_value):
    response = client.post("/test13/", json={
        "cod": cod_value,
        "fecha": f'Valor de prueba {cod_value}',
        "nombre": f'Valor de prueba {cod_value}',
        "decimal": 3.14 + cod_value,
        "valor": cod_value % 2 == 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["cod"] == cod_value
    assert data["fecha"] == f"Valor de prueba {cod_value}"
    assert data["nombre"] == f"Valor de prueba {cod_value}"
    assert data["decimal"] == cod_value % 2 == 0
    assert data["valor"] == (cod_value % 2 == 0)


@pytest.mark.parametrize("cod_value", range(1, ITERATIONS + 1))
def test_gets_test13_all(cod_value):
    response = client.get("/test13/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("cod_value", range(1, ITERATIONS + 1))
def test_get_test13_by_id(cod_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test13/id/{cod_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test13/", json={
            "cod": cod_value,
            "fecha": f'Valor de prueba {cod_value}',
            "nombre": f'Valor de prueba {cod_value}',
            "decimal": 2.71 + cod_value,
            "valor": False,
        })
        response = client.get(f"/test13/id/{cod_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["cod"] == cod_value


@pytest.mark.parametrize("cod_value", range(1, ITERATIONS + 1))
def test_update_test13(cod_value):
    response = client.put(f"/test13/id/{cod_value}", json={
        "fecha": f'Valor actualizado {cod_value}',
        "nombre": f'Valor actualizado {cod_value}',
        "decimal": 1.61 + cod_value,
        "valor": cod_value % 2 != 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["fecha"] == f"Valor actualizado {cod_value}"
    assert data["nombre"] == f"Valor actualizado {cod_value}"
    assert data["decimal"] == cod_value % 2 != 0
    assert data["valor"] == (cod_value % 2 != 0)


@pytest.mark.parametrize("cod_value", range(1, ITERATIONS + 1))
def test_delete_test13(cod_value):
    response = client.delete(f"/test13/id/{cod_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["cod"] == cod_value

    # Verificar que ya no existe
    response = client.get(f"/test13/id/{cod_value}")
    assert response.status_code == 404


def test_create_test13_invalid():
    response = client.post("/test13/", json={
        "fecha": None,
        "nombre": None,
        "decimal": None,
        "valor": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
