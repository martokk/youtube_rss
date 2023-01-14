"""update

Revision ID: 99612f792e96
Revises: 0d7b56ee619f
Create Date: 2023-01-13 14:52:47.102376

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = '99612f792e96'
down_revision = '0d7b56ee619f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
