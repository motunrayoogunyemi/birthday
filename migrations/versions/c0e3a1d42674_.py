"""empty message

Revision ID: c0e3a1d42674
Revises: 8623a3912804
Create Date: 2021-12-03 11:56:36.046405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0e3a1d42674'
down_revision = '8623a3912804'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'lga', 'state', ['state_id'], ['id'])
    op.add_column('transaction', sa.Column('trx_ipaddress', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transaction', 'trx_ipaddress')
    op.drop_constraint(None, 'lga', type_='foreignkey')
    # ### end Alembic commands ###
