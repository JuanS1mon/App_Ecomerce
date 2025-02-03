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

@pytest.mark.parametrize("co_value", range(1, ITERATIONS + 1))
def test_create_test15(co_value):
    response = client.post("/test15/", json={
        "co": co_value,
        "des": f'Valor de prueba {co_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["co"] == co_value
    assert data["des"] == f"Valor de prueba {co_value}"


@pytest.mark.parametrize("co_value", range(1, ITERATIONS + 1))
def test_gets_test15_all(co_value):
    response = client.get("/test15/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("co_value", range(1, ITERATIONS + 1))
def test_get_test15_by_id(co_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test15/id/{co_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test15/", json={
            "co": co_value,
            "des": f'Valor de prueba {co_value}',
        })
        response = client.get(f"/test15/id/{co_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["co"] == co_value


@pytest.mark.parametrize("co_value", range(1, ITERATIONS + 1))
def test_update_test15(co_value):
    response = client.put(f"/test15/id/{co_value}", json={
        "des": f'Valor actualizado {co_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["des"] == f"Valor actualizado {co_value}"


@pytest.mark.parametrize("co_value", range(1, ITERATIONS + 1))
def test_delete_test15(co_value):
    response = client.delete(f"/test15/id/{co_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["co"] == co_value

    # Verificar que ya no existe
    response = client.get(f"/test15/id/{co_value}")
    assert response.status_code == 404


def test_create_test15_invalid():
    response = client.post("/test15/", json={
        "des": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
