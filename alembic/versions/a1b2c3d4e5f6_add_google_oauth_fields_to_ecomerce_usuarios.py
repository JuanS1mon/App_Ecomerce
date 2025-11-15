"""add_google_oauth_fields_to_ecomerce_usuarios

Revision ID: a1b2c3d4e5f6
Revises: f22bb8979b41
Create Date: 2025-11-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f22bb8979b41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Agregar campos para autenticación con Google."""
    # Agregar columna google_id (ID único de Google, único e indexado)
    op.add_column('ecomerce_usuarios', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.create_index('ix_ecomerce_usuarios_google_id', 'ecomerce_usuarios', ['google_id'], unique=True)
    
    # Agregar columna auth_provider (indica el método de autenticación: 'local' o 'google')
    op.add_column('ecomerce_usuarios', sa.Column('auth_provider', sa.String(length=50), nullable=True, server_default='local'))
    
    # Agregar columna profile_picture (URL de la foto de perfil de Google)
    op.add_column('ecomerce_usuarios', sa.Column('profile_picture', sa.String(length=500), nullable=True))
    
    # Hacer que contraseña_hash sea nullable (usuarios de Google no tienen contraseña)
    op.alter_column('ecomerce_usuarios', 'contraseña_hash',
                    existing_type=sa.String(length=255),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema - Remover campos de autenticación con Google."""
    # Revertir nullable de contraseña_hash
    op.alter_column('ecomerce_usuarios', 'contraseña_hash',
                    existing_type=sa.String(length=255),
                    nullable=False)
    
    # Eliminar columnas agregadas
    op.drop_column('ecomerce_usuarios', 'profile_picture')
    op.drop_column('ecomerce_usuarios', 'auth_provider')
    op.drop_index('ix_ecomerce_usuarios_google_id', table_name='ecomerce_usuarios')
    op.drop_column('ecomerce_usuarios', 'google_id')
