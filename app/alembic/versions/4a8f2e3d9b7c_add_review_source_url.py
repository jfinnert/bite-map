"""add review source url

Revision ID: 4a8f2e3d9b7c
Revises: 003_add_place_geom_and_indexes
Create Date: 2025-05-24 16:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4a8f2e3d9b7c'
down_revision = '003_add_place_geom_and_indexes'
branch_labels = None
depends_on = None

def upgrade():
    # Add source_url column to reviews table
    op.add_column('reviews', sa.Column('source_url', sa.String(), nullable=True))

def downgrade():
    # Remove the added column
    op.drop_column('reviews', 'source_url')
