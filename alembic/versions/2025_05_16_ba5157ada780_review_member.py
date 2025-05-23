"""review_member

Revision ID: ba5157ada780
Revises: 78bfe9674969
Create Date: 2025-05-16 10:55:01.127777

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ba5157ada780"
down_revision: Union[str, None] = "78bfe9674969"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "review_member",
        sa.Column("user_id", sa.BIGINT(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "game_id"),
    )
    op.execute(
        "insert into review_member (user_id, game_id) "
        "select gm.user_id, gm.game_id "
        "from game_member gm "
        "inner join game g on g.id = gm.game_id "
        "where g.done is true;",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("review_member")
    # ### end Alembic commands ###
