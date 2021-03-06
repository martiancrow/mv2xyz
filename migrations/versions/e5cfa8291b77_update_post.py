"""update post

Revision ID: e5cfa8291b77
Revises: 69636664e834
Create Date: 2018-03-24 20:03:38.413604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5cfa8291b77'
down_revision = '69636664e834'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('res_posts', sa.Column('post_pid', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('res_posts', 'post_pid')
    # ### end Alembic commands ###
