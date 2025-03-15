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
def test_create_articulos(id_value):
    response = client.post("/articulos/", json={
        "id": id_value,
        "codigo": f'Valor de prueba {id_value}',
        "descripcion": f'Valor de prueba {id_value}',
        "precio_costo": 3.14 + id_value,
        "modelo": f'Valor de prueba {id_value}',
        "marca": f'Valor de prueba {id_value}',
        "id_tipo": id_value * 10,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value
    assert data["codigo"] == f"Valor de prueba {id_value}"
    assert data["descripcion"] == f"Valor de prueba {id_value}"
    assert data["precio_costo"] == id_value * 10
    assert data["modelo"] == f"Valor de prueba {id_value}"
    assert data["marca"] == f"Valor de prueba {id_value}"
    assert data["id_tipo"] == id_value * 10


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_gets_articulos_all(id_value):
    response = client.get("/articulos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_get_articulos_by_id(id_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/articulos/id/{id_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/articulos/", json={
            "id": id_value,
            "codigo": f'Valor de prueba {id_value}',
            "descripcion": f'Valor de prueba {id_value}',
            "precio_costo": 2.71 + id_value,
            "modelo": f'Valor de prueba {id_value}',
            "marca": f'Valor de prueba {id_value}',
            "id_tipo": id_value * 10,
        })
        response = client.get(f"/articulos/id/{id_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_update_articulos(id_value):
    response = client.put(f"/articulos/id/{id_value}", json={
        "codigo": f'Valor actualizado {id_value}',
        "descripcion": f'Valor actualizado {id_value}',
        "precio_costo": 1.61 + id_value,
        "modelo": f'Valor actualizado {id_value}',
        "marca": f'Valor actualizado {id_value}',
        "id_tipo": 1.61 + id_value,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == f"Valor actualizado {id_value}"
    assert data["descripcion"] == f"Valor actualizado {id_value}"
    assert data["precio_costo"] == 1.61 + id_value
    assert data["modelo"] == f"Valor actualizado {id_value}"
    assert data["marca"] == f"Valor actualizado {id_value}"
    assert data["id_tipo"] == 1.61 + id_value


@pytest.mark.parametrize("id_value", range(1, ITERATIONS + 1))
def test_delete_articulos(id_value):
    response = client.delete(f"/articulos/id/{id_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id_value

    # Verificar que ya no existe
    response = client.get(f"/articulos/id/{id_value}")
    assert response.status_code == 404


def test_create_articulos_invalid():
    response = client.post("/articulos/", json={
        "codigo": None,
        "descripcion": None,
        "precio_costo": None,
        "modelo": None,
        "marca": None,
        "id_tipo": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
