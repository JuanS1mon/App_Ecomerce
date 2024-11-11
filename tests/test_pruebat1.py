import sys
import os
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Añadir la ruta del directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..main import app  # Asegúrate de importar tu aplicación FastAPI

client = TestClient(app)

def run_tests():
    start_time = time.time()
    iterations = 10  # Número de veces que se ejecutarán las pruebas

    for i in range(iterations):
        print(f"Ejecutando iteración {i + 1} de {iterations}")
        test_create_pruebat1()
        test_gets_pruebat1_all()
        test_get_pruebat1_campo1()
        test_update_pruebat1()
        test_delete_pruebat1()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Las pruebas se ejecutaron {iterations} veces en {total_time:.2f} segundos")

def test_create_pruebat1():
    response = client.post("/pruebat1/", json={
        "campot1": 2,
        "campot2": "Valor de prueba",
        "campot3": 3.14,
        "campot4": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["campot1"] == 2
    assert data["campot2"] == "Valor de prueba"

def test_gets_pruebat1_all():
    response = client.get("/pruebat1/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_pruebat1_campo1():
    # Primero, creamos un registro de prueba
    client.post("/pruebat1/", json={
        "campot1": 2,
        "campot2": "Valor de prueba",
        "campot3": 2.71,
        "campot4": False
    })
    # Luego, intentamos obtenerlo
    response = client.get("/pruebat1/2")
    assert response.status_code == 200
    data = response.json()
    assert data["campot1"] == 2
    assert data["campot2"] == "Valor de prueba"

def test_update_pruebat1():
    # Primero, creamos el registro que vamos a actualizar
    response = client.post("/pruebat1/", json={
        "campot1": 3,  # Usamos un ID distinto para evitar conflictos
        "campot2": "Valor inicial",
        "campot3": 2.71,
        "campot4": False
    })
    assert response.status_code == 200

    # Ahora, actualizamos el registro con campot1 = 3
    response = client.put("/pruebat1/3", json={
        "campot2": "Valor actualizado",
        "campot3": 1.61,
        "campot4": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["campot2"] == "Valor actualizado"
    assert data["campot3"] == 1.61
    assert data["campot4"] is True

def test_delete_pruebat1():
    # Eliminamos el registro con campot1 = 2
    response = client.delete("/pruebat1/2")
    assert response.status_code == 200
    data = response.json()
    assert data["campot1"] == 2
    # Verificamos que ya no existe
    response = client.get("/pruebat1/2")
    assert response.status_code == 404

if __name__ == "__main__":
    run_tests()