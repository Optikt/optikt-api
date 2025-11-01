from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    print("hereee")
    assert response.status_code == 200
    data = response.json()
    print(data)
