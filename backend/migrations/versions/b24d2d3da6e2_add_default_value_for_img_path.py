"""add default value for img_path

Revision ID: b24d2d3da6e2
Revises: 2cad51cebfc5
Create Date: 2026-05-26 22:12:17.691210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'b24d2d3da6e2'
down_revision: Union[str, Sequence[str], None] = '2cad51cebfc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(text("ALTER TABLE goals ALTER COLUMN img_path SET DEFAULT './backend/images/placeholder.png';"))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(text("ALTER TABLE goals ALTER COLUMN img_path DROP DEFAULT;"))
    pass
