import os
import httpx
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from dotenv import load_dotenv
from main import app

load_dotenv()

API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

client = TestClient(app)

@pytest.mark.asyncio
@patch("proxy_routes.httpx.AsyncClient")
async def test_proxy_request_success(mock_async_client):
    mock_client = AsyncMock()
    mock_async_client.return_value.__aenter__.return_value = mock_client

    mock_response = httpx.Response(
        status_code=200,
        content=b'{"status": "success"}',
        headers={"content-type": "application/json"}
    )
    mock_client.request.return_value = mock_response

    response = client.get(f"{API_PREFIX}/payments")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

@pytest.mark.asyncio
@patch("proxy_routes.httpx.AsyncClient")
async def test_proxy_request_failure(mock_async_client):
    mock_client = AsyncMock()
    mock_async_client.return_value.__aenter__.return_value = mock_client
    mock_client.request.side_effect = httpx.ConnectError("Connection error")

    response = client.get(f"{API_PREFIX}/payments")
    assert response.status_code == 500
    assert "Erro ao redirecionar requisição" in response.text

@patch("proxy_routes.proxy_request")
def test_payments_proxy(mock_proxy):
    mock_proxy.return_value = "Mocked response"
    response = client.get(f"{API_PREFIX}/payments")
    assert response.text == '"Mocked response"'

@patch("proxy_routes.proxy_request")
def test_confirm_payment_proxy(mock_proxy):
    mock_proxy.return_value = "Mocked response"
    response = client.put(f"{API_PREFIX}/payments/confirm/123")
    assert response.text == '"Mocked response"'
