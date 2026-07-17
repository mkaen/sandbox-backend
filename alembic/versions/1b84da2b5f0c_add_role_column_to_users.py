"""Add role column to users

Revision ID: 1b84da2b5f0c
Revises: 5ec4d18622f6
Create Date: 2026-06-28 22:28:54.504837

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b84da2b5f0c'
down_revision: Union[str, Sequence[str], None] = '5ec4d18622f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

userroles_enum = sa.Enum('ADMIN', 'USER', name='userroles')


def upgrade() -> None:
    """Upgrade schema."""
    userroles_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'users',
        sa.Column('role', userroles_enum, nullable=False, server_default='USER'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    userroles_enum.drop(op.get_bind(), checkfirst=True)
