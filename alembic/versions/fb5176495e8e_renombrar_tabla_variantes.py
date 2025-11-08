"""renombrar_tabla_variantes

Revision ID: fb5176495e8e
Revises: 32563ffaa01e
Create Date: 2025-11-04 00:35:17.748979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb5176495e8e'
down_revision: Union[str, Sequence[str], None] = '32563ffaa01e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Renombrar tabla de variantes para seguir nomenclatura en español
    op.rename_table('ecomerce_product_variants', 'ecomerce_productos_variantes')


def downgrade() -> None:
    """Downgrade schema."""
    # Revertir el cambio de nombre de tabla
    op.rename_table('ecomerce_productos_variantes', 'ecomerce_product_variants')
