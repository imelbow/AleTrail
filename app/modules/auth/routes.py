import psycopg
from fastapi import APIRouter, HTTPException, Request, status

from .schema import (
    User,
    UserSignupPayload,
)



router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/sign_up', response_model=User, status_code=status.HTTP_201_CREATED)
async def sign_up(payload: UserSignupPayload, request: Request):
    try:
        rows = await request.app.db_client.fetchone('''
                INSERT INTO users (email, name, password)
                VALUES (%s, %s, crypt(%s, gen_salt('bf')))
                RETURNING id, email, name
            ''',
            payload.email,
            payload.name,
            payload.password,
        )

    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

    return User(
        id=rows['id'],
        email=rows['email'],
    )
