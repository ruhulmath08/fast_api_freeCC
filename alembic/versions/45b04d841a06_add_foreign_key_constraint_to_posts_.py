"""add foreign key constraint to posts table

Revision ID: 45b04d841a06
Revises: 7f4b90107b7d
Create Date: 2026-10-22 17:04:57.626776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45b04d841a06'
down_revision: Union[str, Sequence[str], None] = '7f4b90107b7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('post', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table='post', referent_table='users', local_cols=['owner_id'], remote_cols=['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('post_users_fk', table_name='post')
    op.drop_column('post', 'owner_id')
    pass
