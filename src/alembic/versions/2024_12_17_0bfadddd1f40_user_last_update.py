"""user last update

Revision ID: 0bfadddd1f40
Revises: 0e2344f23b03
Create Date: 2024-12-17 00:40:03.701889

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0bfadddd1f40"
down_revision: Union[str, None] = "0e2344f23b03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("last_update", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "last_update")
    # ### end Alembic commands ###