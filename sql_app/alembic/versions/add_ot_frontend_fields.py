"""Add frontend fields to OT table

Revision ID: add_ot_frontend_fields
Revises: create_ot_materiales
Create Date: 2025-06-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_ot_frontend_fields'
down_revision = 'create_ot_materiales'
branch_labels = None
depends_on = None


def upgrade():
    """Add new fields to OT table for frontend compatibility"""
    
    # Add new columns to the ot table
    op.add_column('ot', sa.Column('numero', sa.String(50), nullable=True))
    op.add_column('ot', sa.Column('fecha', sa.DateTime(), nullable=True))
    op.add_column('ot', sa.Column('cliente', sa.String(255), nullable=True))
    op.add_column('ot', sa.Column('tipo', sa.String(50), nullable=True))
    op.add_column('ot', sa.Column('tecnico', sa.String(100), nullable=True))
    
    # Create indexes
    op.create_index('ix_ot_numero', 'ot', ['numero'])
    
    # Migrate existing data from old fields to new fields
    connection = op.get_bind()
    
    # Update existing records to populate new fields with data from old fields
    connection.execute(sa.text("""
        UPDATE ot 
        SET 
            numero = COALESCE(id_trabajo, 'OT-' || id),
            fecha = COALESCE(fecha_creacion, datetime('now')),
            cliente = COALESCE(titulo, 'Cliente no especificado'),
            tipo = 'mantenimiento',
            tecnico = personal
        WHERE numero IS NULL
    """))
    
    # Now make the required fields NOT NULL
    op.alter_column('ot', 'numero', nullable=False)
    op.alter_column('ot', 'fecha', nullable=False) 
    op.alter_column('ot', 'cliente', nullable=False)
    op.alter_column('ot', 'descripcion', nullable=False)


def downgrade():
    """Remove frontend fields from OT table"""
    
    # Remove indexes
    op.drop_index('ix_ot_numero', 'ot')
    
    # Remove columns
    op.drop_column('ot', 'tecnico')
    op.drop_column('ot', 'tipo')
    op.drop_column('ot', 'cliente')
    op.drop_column('ot', 'fecha')
    op.drop_column('ot', 'numero')
    
    # Restore nullable constraints
    op.alter_column('ot', 'descripcion', nullable=True)
