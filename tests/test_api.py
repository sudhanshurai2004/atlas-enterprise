from fastapi.testclient import TestClient

from app.api.auth import create_token
from app.main import app


client = TestClient(app)


def test_query_requires_auth() -> None:
    response = client.post(
        "/query",
        json={"question": "test", "session_id": "test-session"},
    )

    assert response.status_code == 401


def test_auth_token_and_history(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.get_history",
        lambda session_id: [],
    )
    token_response = client.post(
        "/auth/token",
        json={"username": "demo", "password": "demo"},
    )
    assert token_response.status_code == 200

    token = token_response.json()["access_token"]
    history_response = client.get(
        "/history/test-session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert history_response.status_code == 200


def test_create_token() -> None:
    token = create_token("demo")

    assert isinstance(token, str)
    assert token
