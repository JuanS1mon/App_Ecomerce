"""add_profile_fields_to_usuarios

Revision ID: 32563ffaa01e
Revises: 3e1f4bc6dc53
Create Date: 2025-10-04 19:47:09.732983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32563ffaa01e'
down_revision: Union[str, Sequence[str], None] = 'f22bb8979b41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar nuevas columnas a la tabla Usuarios existente
    with op.batch_alter_table('Usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('telefono', sa.NVARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('direccion', sa.NVARCHAR(length=255), nullable=True))
        batch_op.add_column(sa.Column('fecha_nacimiento', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('imagen_perfil', sa.Text(), nullable=True, comment='Base64 de imagen comprimida'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remover las columnas agregadas
    with op.batch_alter_table('Usuarios', schema=None) as batch_op:
        batch_op.drop_column('imagen_perfil')
        batch_op.drop_column('fecha_nacimiento')
        batch_op.drop_column('direccion')
        batch_op.drop_column('telefono')
