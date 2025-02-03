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
def test_create_planilla_test(codigo_value):
    response = client.post("/planilla_test/", json={
        "codigo": codigo_value,
        "fecha": f'Valor de prueba {codigo_value}',
        "origen": f'Valor de prueba {codigo_value}',
        "tipo": f'Valor de prueba {codigo_value}',
        "prioridad": f'Valor de prueba {codigo_value}',
        "caratula": f'Valor de prueba {codigo_value}',
        "clasificacion": f'Valor de prueba {codigo_value}',
        "estado": f'Valor de prueba {codigo_value}',
        "localidad": f'Valor de prueba {codigo_value}',
        "barrio": f'Valor de prueba {codigo_value}',
        "lugar": f'Valor de prueba {codigo_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value
    assert data["fecha"] == f"Valor de prueba {codigo_value}"
    assert data["origen"] == f"Valor de prueba {codigo_value}"
    assert data["tipo"] == f"Valor de prueba {codigo_value}"
    assert data["prioridad"] == f"Valor de prueba {codigo_value}"
    assert data["caratula"] == f"Valor de prueba {codigo_value}"
    assert data["clasificacion"] == f"Valor de prueba {codigo_value}"
    assert data["estado"] == f"Valor de prueba {codigo_value}"
    assert data["localidad"] == f"Valor de prueba {codigo_value}"
    assert data["barrio"] == f"Valor de prueba {codigo_value}"
    assert data["lugar"] == f"Valor de prueba {codigo_value}"


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_gets_planilla_test_all(codigo_value):
    response = client.get("/planilla_test/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_get_planilla_test_by_id(codigo_value):
    # Asegurarnos de que el registro existe
    response = client.get(f"/planilla_test/id/{codigo_value}")
    if response.status_code == 404:
        # Crear el registro si no existe
        client.post("/planilla_test/", json={
            "codigo": codigo_value,
            "fecha": f'Valor de prueba {codigo_value}',
            "origen": f'Valor de prueba {codigo_value}',
            "tipo": f'Valor de prueba {codigo_value}',
            "prioridad": f'Valor de prueba {codigo_value}',
            "caratula": f'Valor de prueba {codigo_value}',
            "clasificacion": f'Valor de prueba {codigo_value}',
            "estado": f'Valor de prueba {codigo_value}',
            "localidad": f'Valor de prueba {codigo_value}',
            "barrio": f'Valor de prueba {codigo_value}',
            "lugar": f'Valor de prueba {codigo_value}',
        })
        response = client.get(f"/planilla_test/id/{codigo_value}")

    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_update_planilla_test(codigo_value):
    response = client.put(f"/planilla_test/id/{codigo_value}", json={
        "fecha": f'Valor actualizado {codigo_value}',
        "origen": f'Valor actualizado {codigo_value}',
        "tipo": f'Valor actualizado {codigo_value}',
        "prioridad": f'Valor actualizado {codigo_value}',
        "caratula": f'Valor actualizado {codigo_value}',
        "clasificacion": f'Valor actualizado {codigo_value}',
        "estado": f'Valor actualizado {codigo_value}',
        "localidad": f'Valor actualizado {codigo_value}',
        "barrio": f'Valor actualizado {codigo_value}',
        "lugar": f'Valor actualizado {codigo_value}',
    })
    assert response.status_code == 200
    data = response.json()
    assert data["fecha"] == f"Valor actualizado {codigo_value}"
    assert data["origen"] == f"Valor actualizado {codigo_value}"
    assert data["tipo"] == f"Valor actualizado {codigo_value}"
    assert data["prioridad"] == f"Valor actualizado {codigo_value}"
    assert data["caratula"] == f"Valor actualizado {codigo_value}"
    assert data["clasificacion"] == f"Valor actualizado {codigo_value}"
    assert data["estado"] == f"Valor actualizado {codigo_value}"
    assert data["localidad"] == f"Valor actualizado {codigo_value}"
    assert data["barrio"] == f"Valor actualizado {codigo_value}"
    assert data["lugar"] == f"Valor actualizado {codigo_value}"


@pytest.mark.parametrize("codigo_value", range(1, ITERATIONS + 1))
def test_delete_planilla_test(codigo_value):
    response = client.delete(f"/planilla_test/id/{codigo_value}")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == codigo_value

    # Verificar que ya no existe
    response = client.get(f"/planilla_test/id/{codigo_value}")
    assert response.status_code == 404


def test_create_planilla_test_invalid():
    response = client.post("/planilla_test/", json={
        "fecha": None,
        "origen": None,
        "tipo": None,
        "prioridad": None,
        "caratula": None,
        "clasificacion": None,
        "estado": None,
        "localidad": None,
        "barrio": None,
        "lugar": None,
    })
    assert response.status_code == 422  # Unprocessable Entity
