"""empty message

Revision ID: 4eeaf9bcd197
Revises: bb27bcff06e5
Create Date: 2022-04-13 22:01:17.617295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4eeaf9bcd197'
down_revision = 'bb27bcff06e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('questionmarks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('interview_id', sa.Integer(), nullable=True),
    sa.Column('expert_id', sa.Integer(), nullable=True),
    sa.Column('mark', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('questionmarks')
    # ### end Alembic commands ###