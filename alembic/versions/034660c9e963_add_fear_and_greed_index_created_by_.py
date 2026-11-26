"""add_fear_and_greed_index_created_by_column

Revision ID: 034660c9e963
Revises: 58d584bbb30f
Create Date: 2026-11-26 11:58:38.011695

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '034660c9e963'
down_revision: str | Sequence[str] | None = '58d584bbb30f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'fear_and_greed_index',
        sa.Column('created_by', sa.String(), nullable=False, server_default='System'),
    )
    op.alter_column('fear_and_greed_index', 'created_by', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('fear_and_greed_index', 'created_by')
