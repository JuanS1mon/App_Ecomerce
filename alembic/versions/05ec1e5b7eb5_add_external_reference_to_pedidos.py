"""add_external_reference_to_pedidos

Revision ID: 05ec1e5b7eb5
Revises: f8e6fa79ad05
Create Date: 2025-11-04 12:54:07.945286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05ec1e5b7eb5'
down_revision: Union[str, Sequence[str], None] = 'f8e6fa79ad05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar columna external_reference a ecomerce_pedidos
    op.add_column('ecomerce_pedidos', sa.Column('external_reference', sa.String(255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar columna external_reference de ecomerce_pedidos
    op.drop_column('ecomerce_pedidos', 'external_reference')
