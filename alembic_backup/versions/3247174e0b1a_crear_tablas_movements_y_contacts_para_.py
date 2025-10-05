"""Crear tablas movements y contacts para seguimiento de movimientos de obras

Revision ID: 3247174e0b1a
Revises: add_ot_frontend_fields
Create Date: 2025-07-11 13:26:54.322688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3247174e0b1a'
down_revision = 'add_ot_frontend_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla contacts
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('organization', sa.String(length=255), nullable=True),
        sa.Column('position', sa.String(length=255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_contacts_id', 'id')
    )
    
    # Crear tabla movements
    op.create_table('movements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('artwork_id', sa.Integer(), nullable=False),
        sa.Column('movement_type', sa.Enum('PRESTAMO', 'VENTA', 'CESION', 'TRASLADO', 'EXHIBICION', name='movementtype'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVO', 'FINALIZADO', 'CANCELADO', name='movementstatus'), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('from_location_id', sa.Integer(), nullable=True),
        sa.Column('to_location_id', sa.Integer(), nullable=True),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reference_document', sa.String(length=255), nullable=True),
        sa.Column('sale_id', sa.Integer(), nullable=True),
        sa.Column('exhibition_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['artwork_id'], ['artworks.id'], ),
        sa.ForeignKeyConstraint(['exhibition_id'], ['exhibitions.id'], ),
        sa.ForeignKeyConstraint(['from_location_id'], ['locations.id'], ),
        sa.ForeignKeyConstraint(['sale_id'], ['sales.id'], ),
        sa.ForeignKeyConstraint(['to_location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_movements_id', 'id')
    )


def downgrade() -> None:
    # Eliminar tabla movements
    op.drop_index('ix_movements_id', table_name='movements')
    op.drop_table('movements')
    
    # Eliminar tabla contacts
    op.drop_index('ix_contacts_id', table_name='contacts')
    op.drop_table('contacts')
