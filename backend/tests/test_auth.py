import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "invalid@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "is_admin": False
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data


@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient):
    # First registration
    await client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "is_admin": False
        }
    )
    
    # Second registration with same email
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "AnotherPass123!",
            "is_admin": False
        }
    )
    assert response.status_code == 400
