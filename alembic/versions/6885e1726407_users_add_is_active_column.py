"""users_add_is_active_column

Revision ID: 6885e1726407
Revises: a3f8c2d91e4b
Create Date: 2026-07-28 18:06:42.317031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6885e1726407'
down_revision: Union[str, Sequence[str], None] = 'a3f8c2d91e4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.alter_column(
        'users',
        'image_reference',
        existing_type=sa.VARCHAR(),
        type_=sa.Uuid(),
        existing_nullable=True,
        postgresql_using='image_reference::uuid',
    )
    op.alter_column('users', 'is_active', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'users',
        'image_reference',
        existing_type=sa.Uuid(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using='image_reference::text',
    )
    op.drop_column('users', 'is_active')
