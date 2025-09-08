"""Crear tabla ot_materiales para gestión de materiales en órdenes de trabajo

Revision ID: create_ot_materiales
Revises: 
Create Date: 2025-06-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey

# revision identifiers, used by Alembic.
revision = 'create_ot_materiales'
down_revision = None  # Cambiar por la última revisión existente
branch_labels = None
depends_on = None

def upgrade():
    """Crear tabla ot_materiales"""
    
    # Crear tabla ot_materiales
    op.create_table(
        'ot_materiales',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('ot_id', Integer, ForeignKey('ot.id', ondelete='CASCADE'), nullable=False),
        Column('codigo_art', Integer, nullable=False),
        Column('id_deposito', Integer, ForeignKey('depositos.id'), nullable=False),
        Column('cantidad_planificada', Float, default=0.0),
        Column('cantidad_utilizada', Float, default=0.0),
        Column('cantidad_devuelta', Float, default=0.0),
        Column('estado', String(20), default='planificado'),
        Column('fecha_planificacion', DateTime, default=sa.func.now()),
        Column('fecha_consumo', DateTime, nullable=True),
        Column('fecha_devolucion', DateTime, nullable=True),
        Column('observacion', Text, nullable=True),
        Column('usuario_consumo', String(100), nullable=True),
        Column('nro_movimiento_stock', Integer, nullable=True),
    )
    
    # Crear índices para mejorar rendimiento
    op.create_index('ix_ot_materiales_ot_id', 'ot_materiales', ['ot_id'])
    op.create_index('ix_ot_materiales_codigo_art', 'ot_materiales', ['codigo_art'])
    op.create_index('ix_ot_materiales_deposito', 'ot_materiales', ['id_deposito'])
    op.create_index('ix_ot_materiales_estado', 'ot_materiales', ['estado'])
    
    # Crear índice compuesto para búsquedas frecuentes
    op.create_index(
        'ix_ot_materiales_ot_articulo_deposito', 
        'ot_materiales', 
        ['ot_id', 'codigo_art', 'id_deposito'],
        unique=False
    )

def downgrade():
    """Eliminar tabla ot_materiales"""
    
    # Eliminar índices
    op.drop_index('ix_ot_materiales_ot_articulo_deposito', 'ot_materiales')
    op.drop_index('ix_ot_materiales_estado', 'ot_materiales')
    op.drop_index('ix_ot_materiales_deposito', 'ot_materiales')
    op.drop_index('ix_ot_materiales_codigo_art', 'ot_materiales')
    op.drop_index('ix_ot_materiales_ot_id', 'ot_materiales')
    
    # Eliminar tabla
    op.drop_table('ot_materiales')
