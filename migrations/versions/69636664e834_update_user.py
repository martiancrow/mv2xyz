"""update user

Revision ID: 69636664e834
Revises: 38b61b9a4c02
Create Date: 2018-03-24 19:44:13.794436

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '69636664e834'
down_revision = '38b61b9a4c02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ua_users', 'ua_email_confirmed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ua_users', 'ua_email_confirmed',
               existing_type=sa.SmallInteger(),
               nullable=False)
    # ### end Alembic commands ###
