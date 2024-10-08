"""Update models with correct table names and relationships

Revision ID: f963b2df2197
Revises: aeb7989ee867
Create Date: 2024-09-01 08:43:10.873090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f963b2df2197'
down_revision: Union[str, None] = 'aeb7989ee867'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.String(), nullable=True))
    op.drop_index('ix_users_username', table_name='users')
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)
    op.drop_column('users', 'username')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.drop_column('users', 'name')
    # ### end Alembic commands ###
