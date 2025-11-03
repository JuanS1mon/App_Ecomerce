"""add_google_maps_link_to_ecomerce_usuarios

Revision ID: f22bb8979b41
Revises: 408ec56fa81b
Create Date: 2025-11-03 15:40:51.953972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f22bb8979b41'
down_revision: Union[str, Sequence[str], None] = '408ec56fa81b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('ecomerce_usuarios', sa.Column('google_maps_link', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('ecomerce_usuarios', 'google_maps_link')
