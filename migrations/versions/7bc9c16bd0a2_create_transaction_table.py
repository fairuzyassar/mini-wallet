"""create transaction table

Revision ID: 7bc9c16bd0a2
Revises: 77b90025976c
Create Date: 2024-12-15 08:31:14.388755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bc9c16bd0a2'
down_revision: Union[str, None] = '77b90025976c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('reference_id', sa.String(length=100), nullable=False),
    sa.Column('wallet_id', sa.String(length=36), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PROCESSING', 'SUCCESS', 'FAILED', name='transactionstatustype'), nullable=False),
    sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('type', sa.Enum('DEPOSIT', 'WITHDRAWN', name='transactiontype'), nullable=False),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallet.wallet_id'], ),
    sa.PrimaryKeyConstraint('reference_id')
    )
    op.create_index(op.f('ix_transaction_wallet_id'), 'transaction', ['wallet_id'], unique=False)
    op.create_table('transaction_state',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('reference_id', sa.String(length=36), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PROCESSING', 'SUCCESS', 'FAILED', name='transactionstatustype'), nullable=False),
    sa.Column('changed_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['reference_id'], ['transaction.reference_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_state_reference_id'), 'transaction_state', ['reference_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_state_reference_id'), table_name='transaction_state')
    op.drop_table('transaction_state')
    op.drop_index(op.f('ix_transaction_wallet_id'), table_name='transaction')
    op.drop_table('transaction')
    # ### end Alembic commands ###
