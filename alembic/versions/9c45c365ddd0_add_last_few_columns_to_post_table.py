"""add last few columns to post table

Revision ID: 9c45c365ddd0
Revises: 45b04d841a06
Create Date: 2026-10-22 17:25:05.103110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text


# revision identifiers, used by Alembic.
revision: str = '9c45c365ddd0'
down_revision: Union[str, Sequence[str], None] = '45b04d841a06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('post', sa.Column('published', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('post', sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('post', 'published')
    op.drop_column('post', 'created_at')
    pass
