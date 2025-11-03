"""agregar_tabla_variantes_productos

Revision ID: 408ec56fa81b
Revises: e2f718a95752
Create Date: 2025-11-02 15:21:50.793871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '408ec56fa81b'
down_revision: Union[str, Sequence[str], None] = 'e2f718a95752'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('ecomerce_product_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(length=100), nullable=True),
        sa.Column('tipo', sa.String(length=100), nullable=True),
        sa.Column('precio_adicional', sa.Integer(), nullable=True, default=0),
        sa.Column('stock', sa.Integer(), nullable=True, default=0),
        sa.Column('imagen_url', sa.String(length=255), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, default=True),
        sa.ForeignKeyConstraint(['product_id'], ['ecomerce_productos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ecomerce_product_variants_id'), 'ecomerce_product_variants', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_ecomerce_product_variants_id'), table_name='ecomerce_product_variants')
    op.drop_table('ecomerce_product_variants')
