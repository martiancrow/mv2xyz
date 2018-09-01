"""empty message

Revision ID: 48eff7641cc4
Revises: 
Create Date: 2018-03-24 03:50:31.588028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48eff7641cc4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ua_session_base',
    sa.Column('ua_sb_key', sa.String(length=256), nullable=False),
    sa.Column('ua_sb_ip', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('ua_sb_exceed', sa.SmallInteger(), nullable=True),
    sa.Column('ua_sb_lastheart', sa.BigInteger(), nullable=True),
    sa.Column('ua_sb_creattime', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('ua_sb_key'),
    mysql_ENGINE='MEMORY'
    )
    op.create_table('ua_users',
    sa.Column('ua_user_id', sa.Integer(), nullable=False),
    sa.Column('ua_user_email', sa.String(length=128), nullable=True),
    sa.Column('ua_user_nick', sa.String(length=64), nullable=True),
    sa.Column('ua_pwd_hash', sa.String(length=128), nullable=True),
    sa.Column('ua_email_confirmed', sa.SmallInteger(), nullable=True),
    sa.Column('ua_creattime', sa.DateTime(), nullable=True),
    sa.Column('avatar_hash', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('ua_user_id'),
    mysql_ENGINE='MyISAM'
    )
    op.create_index(op.f('ix_ua_users_ua_user_email'), 'ua_users', ['ua_user_email'], unique=True)
    op.create_index(op.f('ix_ua_users_ua_user_nick'), 'ua_users', ['ua_user_nick'], unique=True)
    op.create_table('res_posts',
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('post_name', sa.String(length=64), nullable=True),
    sa.Column('post_body', sa.Text(), nullable=True),
    sa.Column('post_body_html', sa.Text(), nullable=True),
    sa.Column('post_updatetime', sa.DateTime(), nullable=True),
    sa.Column('post_creattime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['ua_users.ua_user_id'], ),
    sa.PrimaryKeyConstraint('post_id'),
    mysql_ENGINE='MyISAM'
    )
    op.create_table('ua_session_data',
    sa.Column('ua_sb_key', sa.String(length=128), nullable=False),
    sa.Column('ua_sd_key', sa.String(length=64), nullable=False),
    sa.Column('ua_sd_value', sa.VARBINARY(length=512), nullable=True),
    sa.Column('ua_sd_type', sa.String(length=8), nullable=True),
    sa.ForeignKeyConstraint(['ua_sb_key'], ['ua_session_base.ua_sb_key'], ),
    sa.PrimaryKeyConstraint('ua_sb_key', 'ua_sd_key'),
    mysql_ENGINE='MEMORY'
    )
    op.create_table('res_files',
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('file_name', sa.String(length=128), nullable=True),
    sa.Column('file_type', sa.String(length=64), nullable=True),
    sa.Column('file_data', sa.LONGBLOB(), nullable=True),
    sa.Column('file_creattime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['res_posts.post_id'], ),
    sa.PrimaryKeyConstraint('file_id'),
    mysql_ENGINE='MyISAM'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('res_files')
    op.drop_table('ua_session_data')
    op.drop_table('res_posts')
    op.drop_index(op.f('ix_ua_users_ua_user_nick'), table_name='ua_users')
    op.drop_index(op.f('ix_ua_users_ua_user_email'), table_name='ua_users')
    op.drop_table('ua_users')
    op.drop_table('ua_session_base')
    # ### end Alembic commands ###
