import psycopg
from fastapi import APIRouter, HTTPException, Request, status

from .schema import (
    User,
    UserSignupPayload,
    UserSigninPayload,
)


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup')
async def sign_up(data: UserSignupPayload, request: Request) -> User:
    db_client = request.app.state.db_client
    try:
        user = await db_client.fetchone('''
                INSERT INTO users (email, name, password)
                VALUES (
                    %(email)s, 
                    %(name)s, 
                    crypt(%(password)s, gen_salt('bf'))
                )
                RETURNING id, email, name
            ''',
            email=data.email,
            name=data.name,
            password=data.password,
        )

    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already registered.')

    return User(id=user['id'],email=user['email'])


@router.post('/signin')
async def signin(data: UserSigninPayload, request: Request) -> User:
    user = await request.app.state.db_client.fetchone('''
            SELECT 
                id, 
                email,
                password = crypt(%(password)s, password) AS password_matches,
                is_deleted
            FROM users
            WHERE email = %(email)s
        ''',
        email=data.email,
        password=data.password,
    )

    if user is None or user['is_deleted']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not user['password_matches']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    request.session['userid'] = str(user['id'])

    return User(id=user['id'], email=user['email'])


@router.post('/signout')
async def signout(request: Request):
    try:
        request.session.clear()
    except Exception as e:
        raise f'Signout Error: {str(e)}.'


@router.get('/testauth')
async def test_auth(request: Request):
    userid = request.session.get('userid')
    return {'userid': userid, 'hello': 'world'}
