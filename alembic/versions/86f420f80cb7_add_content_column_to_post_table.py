"""add content column to post table

Revision ID: 86f420f80cb7
Revises: be88c17d1e9b
Create Date: 2026-10-22 03:17:26.822912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86f420f80cb7'
down_revision: Union[str, Sequence[str], None] = 'be88c17d1e9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('post', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('post', 'content')
    pass
