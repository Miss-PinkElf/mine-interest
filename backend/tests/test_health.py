from fastapi.testclient import TestClient

from app.main import app


VITE_LOOPBACK_ORIGIN = "http://127.0.0.1:5173"
HEALTH_ENDPOINT = "/api/health"
ACCESS_CONTROL_REQUEST_METHOD_HEADER = "Access-Control-Request-Method"
ACCESS_CONTROL_ALLOW_ORIGIN_HEADER = "access-control-allow-origin"
GET_REQUEST_METHOD = "GET"


def test_health_returns_service_status() -> None:
    client = TestClient(app)

    response = client.get(HEALTH_ENDPOINT)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_preflight_allows_vite_loopback_origin() -> None:
    client = TestClient(app)

    response = client.options(
        HEALTH_ENDPOINT,
        headers={
            "Origin": VITE_LOOPBACK_ORIGIN,
            ACCESS_CONTROL_REQUEST_METHOD_HEADER: GET_REQUEST_METHOD,
        },
    )

    assert response.status_code == 200
    assert response.headers[ACCESS_CONTROL_ALLOW_ORIGIN_HEADER] == VITE_LOOPBACK_ORIGIN
