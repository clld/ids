"""fix polymorphic_type

Revision ID: 28accca7dc14
Revises: 
Create Date: 2014-11-26 14:47:59.049000

"""

# revision identifiers, used by Alembic.
revision = '28accca7dc14'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    update_pmtype(['parameter', 'contribution', 'unit', 'value'], 'base', 'custom')


def downgrade():
    update_pmtype(['parameter', 'contribution', 'unit', 'value'], 'custom', 'base')


def update_pmtype(tablenames, before, after):
    for table in tablenames:
        op.execute(sa.text('UPDATE %s SET polymorphic_type = :after '
            'WHERE polymorphic_type = :before' % table
            ).bindparams(before=before, after=after))
