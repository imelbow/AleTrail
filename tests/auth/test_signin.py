import pytest
from httpx import AsyncClient
from fastapi import status




@pytest.mark.asyncio
async def test_signin_success(async_client: AsyncClient, mock_db):
    mock_db.fetchone.return_value = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'test@example.com',
        'password_matches': True,
        'is_deleted': False,
    }

    response = await async_client.post(
        '/v1/auth/signin',
        json={
            'email': 'test@example.com',
            'password': 'testpass123',
        }
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'test@example.com'


@pytest.mark.asyncio
async def test_signin_wrong_password(async_client: AsyncClient, mock_db):
    mock_db.fetchone.return_value = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'test@example.com',
        'password_matches': False,
        'is_deleted': False,
    }

    response = await async_client.post(
        '/v1/auth/signin',
        json={
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_signin_user_not_found(async_client: AsyncClient, mock_db):
    mock_db.fetchone.return_value = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'test@example.com',
        'password_matches': True,
        'is_deleted': True,
    }

    response = await async_client.post(
        '/v1/auth/signin',
        json={
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
