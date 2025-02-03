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
def test_create_test22(codigo_value):
    response = client.post("/test22/", json={
        "codigo": codigo_value,
        "descripcion": f'Valor de prueba {codigo_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value
    assert data["descripcion"] == f"Valor de prueba {codigo_value}"


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_gets_test22_all(codigo_value):
    response = client.get("/test22/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_get_test22_by_id(codigo_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test22/id/{codigo_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test22/", json={
            "codigo": codigo_value,
            "descripcion": f'Valor de prueba {codigo_value}',
        })
        response = client.get(f"/test22/id/{codigo_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_update_test22(codigo_value):
    response = client.put(f"/test22/id/{codigo_value}", json={
        "descripcion": f'Valor actualizado {codigo_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["descripcion"] == f"Valor actualizado {codigo_value}"


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_delete_test22(codigo_value):
    response = client.delete(f"/test22/id/{codigo_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value

    # Verificar que ya no existe
    response = client.get(f"/test22/id/{codigo_value}")
    assert response.status_code == 404


def test_create_test22_invalid():
    response = client.post("/test22/", json={
        "descripcion": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
