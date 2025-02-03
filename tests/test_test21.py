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
def test_create_test21(codi_value):
    response = client.post("/test21/", json={
        "codi": codi_value,
        "test1": f'Valor de prueba {codi_value}',
        "descripcion": f'Valor de prueba {codi_value}',
        "fecha": f'Valor de prueba {codi_value}',
        "cccc": 3.14 + codi_value,
        "ordentrabajo": codi_value % 2 == 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value
    assert data["test1"] == f"Valor de prueba {codi_value}"
    assert data["descripcion"] == f"Valor de prueba {codi_value}"
    assert data["fecha"] == f"Valor de prueba {codi_value}"
    assert data["cccc"] == codi_value % 2 == 0
    assert data["ordentrabajo"] == (codi_value % 2 == 0)


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_gets_test21_all(codi_value):
    response = client.get("/test21/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_get_test21_by_id(codi_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/test21/id/{codi_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/test21/", json={
            "codi": codi_value,
            "test1": f'Valor de prueba {codi_value}',
            "descripcion": f'Valor de prueba {codi_value}',
            "fecha": f'Valor de prueba {codi_value}',
            "cccc": 2.71 + codi_value,
            "ordentrabajo": False,
        })
        response = client.get(f"/test21/id/{codi_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_update_test21(codi_value):
    response = client.put(f"/test21/id/{codi_value}", json={
        "test1": f'Valor actualizado {codi_value}',
        "descripcion": f'Valor actualizado {codi_value}',
        "fecha": f'Valor actualizado {codi_value}',
        "cccc": 1.61 + codi_value,
        "ordentrabajo": codi_value % 2 != 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["test1"] == f"Valor actualizado {codi_value}"
    assert data["descripcion"] == f"Valor actualizado {codi_value}"
    assert data["fecha"] == f"Valor actualizado {codi_value}"
    assert data["cccc"] == codi_value % 2 != 0
    assert data["ordentrabajo"] == (codi_value % 2 != 0)


@pytest.mark.parametrize("codi_value", range(1, ITERATIONS + 1))
def test_delete_test21(codi_value):
    response = client.delete(f"/test21/id/{codi_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["codi"] == codi_value

    # Verificar que ya no existe
    response = client.get(f"/test21/id/{codi_value}")
    assert response.status_code == 404


def test_create_test21_invalid():
    response = client.post("/test21/", json={
        "test1": None,
        "descripcion": None,
        "fecha": None,
        "cccc": None,
        "ordentrabajo": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
