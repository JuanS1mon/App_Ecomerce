"""Change total column from Integer to Float in ecomerce_pedidos

Revision ID: f8e6fa79ad05
Revises: 7fce0fdad7a4
Create Date: 2025-11-04 10:55:28.923239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision: str = 'f8e6fa79ad05'
down_revision: Union[str, Sequence[str], None] = 'fb5176495e8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # For SQL Server, we need to drop the default constraint before altering the column
    # Execute raw SQL to drop the default constraint
    op.execute("DECLARE @constraint_name nvarchar(128); SELECT @constraint_name = name FROM sys.default_constraints WHERE parent_object_id = OBJECT_ID('ecomerce_pedidos') AND col_name(parent_object_id, parent_column_id) = 'total'; IF @constraint_name IS NOT NULL EXEC('ALTER TABLE ecomerce_pedidos DROP CONSTRAINT ' + @constraint_name)")
    
    # Change total column from Integer to Float in ecomerce_pedidos table
    op.alter_column('ecomerce_pedidos', 'total',
                    existing_type=sa.INTEGER(),
                    type_=sa.FLOAT(),
                    existing_nullable=True)
    
    # Add the default constraint back with float value
    op.execute("ALTER TABLE ecomerce_pedidos ADD CONSTRAINT DF_ecomerce_pedidos_total DEFAULT 0.0 FOR total")


def downgrade() -> None:
    """Downgrade schema."""
    # For SQL Server, we need to drop the default constraint before altering the column
    # Execute raw SQL to drop the default constraint
    op.execute("DECLARE @constraint_name nvarchar(128); SELECT @constraint_name = name FROM sys.default_constraints WHERE parent_object_id = OBJECT_ID('ecomerce_pedidos') AND col_name(parent_object_id, parent_column_id) = 'total'; IF @constraint_name IS NOT NULL EXEC('ALTER TABLE ecomerce_pedidos DROP CONSTRAINT ' + @constraint_name)")
    
    # Change total column back from Float to Integer in ecomerce_pedidos table
    op.alter_column('ecomerce_pedidos', 'total',
                    existing_type=sa.FLOAT(),
                    type_=sa.INTEGER(),
                    existing_nullable=True)
    
    # Add the default constraint back with integer value
    op.execute("ALTER TABLE ecomerce_pedidos ADD CONSTRAINT DF_ecomerce_pedidos_total DEFAULT 0 FOR total")
