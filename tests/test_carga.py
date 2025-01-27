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

@pytest.mark.parametrize("nrosuceso_value", range(1, ITERATIONS + 1))
def test_create_carga(nrosuceso_value):
    response = client.post("/carga/", json={
        "nrosuceso": nrosuceso_value,
        "fecha": f'Valor de prueba {nrosuceso_value}',
        "origen": f'Valor de prueba {nrosuceso_value}',
        "tipo": f'Valor de prueba {nrosuceso_value}',
        "caratula": f'Valor de prueba {nrosuceso_value}',
        "clasificacion": f'Valor de prueba {nrosuceso_value}',
        "estado": f'Valor de prueba {nrosuceso_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nrosuceso"] == nrosuceso_value
    assert data["fecha"] == f"Valor de prueba {nrosuceso_value}"
    assert data["origen"] == f"Valor de prueba {nrosuceso_value}"
    assert data["tipo"] == f"Valor de prueba {nrosuceso_value}"
    assert data["caratula"] == f"Valor de prueba {nrosuceso_value}"
    assert data["clasificacion"] == f"Valor de prueba {nrosuceso_value}"
    assert data["estado"] == f"Valor de prueba {nrosuceso_value}"


@pytest.mark.parametrize("nrosuceso_value", range(1, ITERATIONS + 1))
def test_gets_carga_all(nrosuceso_value):
    response = client.get("/carga/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("nrosuceso_value", range(1, ITERATIONS + 1))
def test_get_carga_by_id(nrosuceso_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/carga/id/{nrosuceso_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/carga/", json={
            "nrosuceso": nrosuceso_value,
            "fecha": f'Valor de prueba {nrosuceso_value}',
            "origen": f'Valor de prueba {nrosuceso_value}',
            "tipo": f'Valor de prueba {nrosuceso_value}',
            "caratula": f'Valor de prueba {nrosuceso_value}',
            "clasificacion": f'Valor de prueba {nrosuceso_value}',
            "estado": f'Valor de prueba {nrosuceso_value}',
        })
        response = client.get(f"/carga/id/{nrosuceso_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["nrosuceso"] == nrosuceso_value


@pytest.mark.parametrize("nrosuceso_value", range(1, ITERATIONS + 1))
def test_update_carga(nrosuceso_value):
    response = client.put(f"/carga/id/{nrosuceso_value}", json={
        "fecha": f'Valor actualizado {nrosuceso_value}',
        "origen": f'Valor actualizado {nrosuceso_value}',
        "tipo": f'Valor actualizado {nrosuceso_value}',
        "caratula": f'Valor actualizado {nrosuceso_value}',
        "clasificacion": f'Valor actualizado {nrosuceso_value}',
        "estado": f'Valor actualizado {nrosuceso_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["fecha"] == f"Valor actualizado {nrosuceso_value}"
    assert data["origen"] == f"Valor actualizado {nrosuceso_value}"
    assert data["tipo"] == f"Valor actualizado {nrosuceso_value}"
    assert data["caratula"] == f"Valor actualizado {nrosuceso_value}"
    assert data["clasificacion"] == f"Valor actualizado {nrosuceso_value}"
    assert data["estado"] == f"Valor actualizado {nrosuceso_value}"


@pytest.mark.parametrize("nrosuceso_value", range(1, ITERATIONS + 1))
def test_delete_carga(nrosuceso_value):
    response = client.delete(f"/carga/id/{nrosuceso_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["nrosuceso"] == nrosuceso_value

    # Verificar que ya no existe
    response = client.get(f"/carga/id/{nrosuceso_value}")
    assert response.status_code == 404


def test_create_carga_invalid():
    response = client.post("/carga/", json={
        "fecha": None,
        "origen": None,
        "tipo": None,
        "caratula": None,
        "clasificacion": None,
        "estado": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
