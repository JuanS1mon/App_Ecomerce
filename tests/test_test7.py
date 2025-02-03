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
def test_create_test7(id_value):
    response = client.post("/test7/", json={
        "id": id_value,
        "nombre": f'Valor de prueba {id_value}',
        "fecha": f'Valor de prueba {id_value}',
        "aa": 3.14 + id_value,
        "bb": id_value % 2 == 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value
    assert data["nombre"] == f"Valor de prueba {id_value}"
    assert data["fecha"] == f"Valor de prueba {id_value}"
    assert data["aa"] == id_value % 2 == 0
    assert data["bb"] == (id_value % 2 == 0)


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_gets_test7_all(id_value):
    response = client.get("/test7/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_get_test7_by_id(id_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test7/id/{id_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test7/", json={
            "id": id_value,
            "nombre": f'Valor de prueba {id_value}',
            "fecha": f'Valor de prueba {id_value}',
            "aa": 2.71 + id_value,
            "bb": False,
        })
        response = client.get(f"/test7/id/{id_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_update_test7(id_value):
    response = client.put(f"/test7/id/{id_value}", json={
        "nombre": f'Valor actualizado {id_value}',
        "fecha": f'Valor actualizado {id_value}',
        "aa": 1.61 + id_value,
        "bb": id_value % 2 != 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == f"Valor actualizado {id_value}"
    assert data["fecha"] == f"Valor actualizado {id_value}"
    assert data["aa"] == id_value % 2 != 0
    assert data["bb"] == (id_value % 2 != 0)


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_delete_test7(id_value):
    response = client.delete(f"/test7/id/{id_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value

    # Verificar que ya no existe
    response = client.get(f"/test7/id/{id_value}")
    assert response.status_code == 404


def test_create_test7_invalid():
    response = client.post("/test7/", json={
        "nombre": None,
        "fecha": None,
        "aa": None,
        "bb": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
