"""empty message

Revision ID: 7b85e09d655e
Revises: 
Create Date: 2021-09-29 11:25:52.074333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b85e09d655e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('password', sa.String(length=80), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('public_id')
    )
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=200), nullable=False),
    sa.Column('date_created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('author', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('covid',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('country', sa.String(length=50), nullable=True),
    sa.Column('cases', sa.String(length=50000), nullable=True),
    sa.Column('tests', sa.String(length=50000), nullable=True),
    sa.Column('deaths', sa.String(length=50000), nullable=True),
    sa.Column('recovered', sa.String(length=50000), nullable=True),
    sa.Column('date_created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('covid')
    op.drop_table('comments')
    op.drop_table('user')
    # ### end Alembic commands ###