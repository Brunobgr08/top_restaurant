import logging
import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel
from main import lifespan, logger, http_exception_handler, validation_exception_handler, app

@pytest.mark.asyncio
async def test_lifespan_success():
    mock_app = MagicMock(spec=FastAPI)

    with patch('main.threading.Thread') as mock_thread, \
         patch('main.start_consumer') as mock_consumer:

        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        async with lifespan(mock_app) as _:
            pass

        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

@pytest.mark.asyncio
async def test_lifespan_failure(caplog):
    mock_app = MagicMock(spec=FastAPI)

    with patch('main.threading.Thread') as mock_thread, \
         patch('main.start_consumer', side_effect=Exception("Test error")):

        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        mock_thread_instance.start.side_effect = Exception("Test error")

        life_span = lifespan(mock_app)
        async with life_span as _:
            pass

        assert any("❌ Falha ao iniciar consumer: Test error" in record.message
                 for record in caplog.records)

@pytest.mark.asyncio
async def test_http_exception_handler():
    mock_request = MagicMock()
    exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    response = await http_exception_handler(mock_request, exc)

    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.body.decode() == '{"detail":"Not Found"}'