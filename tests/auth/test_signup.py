import pytest
from httpx import AsyncClient
from fastapi import status
import psycopg.errors



@pytest.mark.asyncio
async def test_signup_success(async_client: AsyncClient, mock_db):
    mock_db.fetchone.return_value = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'test@example.com',
        'name': 'Test User',
    }

    response = await async_client.post(
        '/v1/auth/signup',
        json={
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpass123',
        }
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'test@example.com'
    mock_db.fetchone.assert_called_once()


@pytest.mark.asyncio
async def test_signup_duplicate_email(async_client: AsyncClient, mock_db):
    mock_db.fetchone.side_effect = psycopg.errors.UniqueViolation()

    response = await async_client.post(
        '/v1/auth/signup',
        json={
            'email': 'existing@example.com',
            'name': 'Test User',
            'password': 'testpass123',
        }
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert 'already registered' in response.json()['detail'].lower()
