"""Merge conflicting branches

Revision ID: 84d0b983f550
Revises: 208847c4255a, 5fdf99baade6
Create Date: 2026-03-02 05:43:19.311887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84d0b983f550'
down_revision: Union[str, Sequence[str], None] = ('208847c4255a', '5fdf99baade6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
