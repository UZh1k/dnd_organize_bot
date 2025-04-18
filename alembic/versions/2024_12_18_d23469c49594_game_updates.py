"""game updates

Revision ID: d23469c49594
Revises: 0bfadddd1f40
Create Date: 2024-12-18 01:03:19.856024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd23469c49594'
down_revision: Union[str, None] = '0bfadddd1f40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game', sa.Column('redaction', sa.String(), nullable=True))
    op.add_column('game', sa.Column('setting', sa.String(), nullable=True))
    op.add_column('game', sa.Column('start_level', sa.String(), nullable=True))
    op.alter_column('game', 'max_age',
               existing_type=sa.SMALLINT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('game', 'max_age',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.drop_column('game', 'start_level')
    op.drop_column('game', 'setting')
    op.drop_column('game', 'redaction')
    # ### end Alembic commands ###
