"""constraint for new column

Revision ID: 2cad51cebfc5
Revises: 10ad26537a2b
Create Date: 2026-05-26 21:40:24.710864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '2cad51cebfc5'
down_revision: Union[str, Sequence[str], None] = '10ad26537a2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(text("ALTER TABLE goals ADD CONSTRAINT goals_status_check CHECK (status IN ('Active', 'Done'));"))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(text("ALTER TABLE goals DROP CONSTRAINT goals_status_check"))
    pass
