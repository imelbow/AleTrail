"""create organisations table

Revision ID: 6a87769f8346
Revises: 043acab2c1fb
Create Date: 2025-11-04 22:55:29.365435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a87769f8346'
down_revision: Union[str, Sequence[str], None] = '043acab2c1fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('''
        CREATE TABLE organisation (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(100) NOT NULL
        )
    ''')

    op.execute('''
        CREATE TYPE role_enum AS ENUM ('owner', 'manager');

        CREATE TABLE access_roles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            orgid UUID NOT NULL REFERENCES organisation(id) ON DELETE CASCADE,
            userid UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role role_enum NOT NULL,
        UNIQUE (orgid, userid)
        )
    ''')

    op.execute('CREATE INDEX idx_access_roles_orgid ON access_roles(orgid)')
    op.execute('CREATE INDEX idx_access_roles_userid ON access_roles(userid)')


def downgrade() -> None:
    op.execute('DROP TABLE IF EXISTS access_roles CASCADE')
    op.execute('DROP TABLE IF EXISTS organisation CASCADE')
