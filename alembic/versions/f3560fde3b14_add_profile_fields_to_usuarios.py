"""add_profile_fields_to_usuarios

Revision ID: f3560fde3b14
Revises: 163506fcdd36
Create Date: 2025-10-04 19:28:00.272379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3560fde3b14'
down_revision = '163506fcdd36'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar nuevas columnas a la tabla Usuarios existente
    with op.batch_alter_table('Usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('telefono', sa.NVARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('direccion', sa.NVARCHAR(length=255), nullable=True))
        batch_op.add_column(sa.Column('fecha_nacimiento', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('imagen_perfil', sa.Text(), nullable=True, comment='Base64 de imagen comprimida'))


def downgrade() -> None:
    # Remover las columnas agregadas
    with op.batch_alter_table('Usuarios', schema=None) as batch_op:
        batch_op.drop_column('imagen_perfil')
        batch_op.drop_column('fecha_nacimiento')
        batch_op.drop_column('direccion')
        batch_op.drop_column('telefono')
