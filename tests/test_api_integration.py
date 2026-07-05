# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api import app
from src.core.state_manager import state_manager, AttackStatus


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_api_status_endpoint(client: TestClient) -> None:
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "target" in data


@patch("src.worker.service.worker_service.start_attack", new_callable=AsyncMock)
def test_api_start_and_stop_attack(mock_start: AsyncMock, client: TestClient) -> None:
    response = client.post("/api/attack/start", json={
        "target": "https://example.com",
        "duration": 60,
        "threads": 10,
        "method": "GET",
        "rpc": 100
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_start.assert_awaited_once_with(target="https://example.com", duration=60, threads=10, method="GET", rpc=100)
    
    with patch("src.worker.service.worker_service.stop_attack", new_callable=AsyncMock) as mock_stop:
        response = client.post("/api/attack/stop")
        assert response.status_code == 200
        mock_stop.assert_awaited_once()


def test_websocket_endpoint_reconcile(client: TestClient) -> None:
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "state_reconcile"
        assert "status" in data["payload"]
