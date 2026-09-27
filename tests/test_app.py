import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_artists_api(client):
    response = client.get("/artists")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_invalid_first_guess(client):
    response = client.post(
        "/first-guess",
        data={"artist": "This Artist Does Not Exist"},
        follow_redirects=False
    )

    assert response.status_code == 302
