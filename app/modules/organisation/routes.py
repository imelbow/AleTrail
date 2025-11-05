from fastapi import APIRouter, Request

from .schema import (
    OrganisationCreatePayload,
    Organisation,
)


router = APIRouter(prefix='/organisation', tags=['organisation'])


@router.post('')
async def create_organisation(data: OrganisationCreatePayload, request: Request) -> Organisation:
    db_client = request.app.state.db_client

    org = await db_client.fetchone('''
            INSERT INTO organisation (title)
            VALUES ( %(title)s )
            RETURNING id, title
        ''',
        title=data.title
    )

    await db_client.fetchone('''
            INSERT INTO access_roles (orgid, userid, role)
            VALUES (
                %(orgid)s,
                %(userid)s,
                %(role)s
            )
            RETURNING id
        ''',
        orgid=org['id'],
        userid=request.session.get('userid'),
        role='owner',
    )

    return Organisation(
        id=org['id'],
        title=org['title'],
    )