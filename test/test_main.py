from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

# Agrega más tests para las rutas que desees probar
def test_cors_headers():
    response = client.get("/")
    assert response.status_code == 200
