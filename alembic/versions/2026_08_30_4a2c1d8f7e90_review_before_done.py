"""allow comments before a game is done

Revision ID: 4a2c1d8f7e90
Revises: e62f8a9a69f8
Create Date: 2026-08-30 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4a2c1d8f7e90"
down_revision: Union[str, None] = "e62f8a9a69f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("review", "value", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.execute("DELETE FROM review WHERE value IS NULL")
    op.alter_column("review", "value", existing_type=sa.Integer(), nullable=False)
