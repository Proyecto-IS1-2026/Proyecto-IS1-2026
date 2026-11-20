import pytest


@pytest.mark.skip(reason="Pendiente implementar users")
def test_create_user(client):
    response = client.post(
        "/users",
        data={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
        },
    )

    assert response.status_code == 302
