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
def test_create_test16(codi_value):
    response = client.post("/test16/", json={
        "codi": codi_value,
        "dns": f'Valor de prueba {codi_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value
    assert data["dns"] == f"Valor de prueba {codi_value}"


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_gets_test16_all(codi_value):
    response = client.get("/test16/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_get_test16_by_id(codi_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test16/id/{codi_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test16/", json={
            "codi": codi_value,
            "dns": f'Valor de prueba {codi_value}',
        })
        response = client.get(f"/test16/id/{codi_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_update_test16(codi_value):
    response = client.put(f"/test16/id/{codi_value}", json={
        "dns": f'Valor actualizado {codi_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["dns"] == f"Valor actualizado {codi_value}"


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_delete_test16(codi_value):
    response = client.delete(f"/test16/id/{codi_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value

    # Verificar que ya no existe
    response = client.get(f"/test16/id/{codi_value}")
    assert response.status_code == 404


def test_create_test16_invalid():
    response = client.post("/test16/", json={
        "dns": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
