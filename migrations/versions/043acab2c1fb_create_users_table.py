"""create users table

Revision ID: 043acab2c1fb
Revises: 
Create Date: 2025-10-29 23:56:28.140284

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '043acab2c1fb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('''
        CREATE EXTENSION IF NOT EXISTS pgcrypto;
        CREATE EXTENSION IF NOT EXISTS citext;
    
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name CITEXT NULL,
            email CITEXT NOT NULL UNIQUE,
            password TEXT,
            is_deleted BOOLEAN DEFAULT FALSE
        )
    ''',
    )


def downgrade():
    op.execute("DROP TABLE users;")
