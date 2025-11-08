"""base

Revision ID: e2f718a95752
Revises: 
Create Date: 2025-11-02 15:22:35.208594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2f718a95752'
down_revision: Union[str, Sequence[str], None] = '3e1f4bc6dc53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
