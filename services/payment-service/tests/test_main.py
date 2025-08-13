import pytest
from fastapi.testclient import TestClient
from main import app

def test_app_creation():
    """Testa se a aplicação FastAPI foi criada corretamente"""
    assert app is not None
    assert app.title == "Payment Service API"

def test_docs_endpoint():
    """Testa endpoint de documentação"""
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_endpoint():
    """Testa endpoint do OpenAPI schema"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
