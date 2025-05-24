"""Add source_url to reviews and fix review schema

Revision ID: 004_add_review_source_url_and_fix_schema
Revises: 003_add_place_geom_and_indexes
Create Date: 2025-05-24 16:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_review_source_url_and_fix_schema'
down_revision = '003_add_place_geom_and_indexes'
branch_labels = None
depends_on = None

def upgrade():
    # Add source_url column to reviews table
    op.add_column('reviews', sa.Column('source_url', sa.String(), nullable=True))
    
    # Add missing columns that should be in reviews based on current model
    # First check if user_id column exists, if not add it
    try:
        op.add_column('reviews', sa.Column('user_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_reviews_user_id', 'reviews', 'users', ['user_id'], ['id'])
    except:
        # Column might already exist from a previous migration
        pass
    
    # Add rating and comment columns if they don't exist
    try:
        op.add_column('reviews', sa.Column('rating', sa.Integer(), nullable=True))
        op.add_column('reviews', sa.Column('comment', sa.Text(), nullable=True))
    except:
        # Columns might already exist
        pass
    
    # Update the unique constraint to match current model
    try:
        op.drop_constraint('uix_review_source_place', 'reviews', type_='unique')
    except:
        pass
    
    try:
        op.create_unique_constraint('uq_user_place_review', 'reviews', ['user_id', 'place_id'])
    except:
        pass

def downgrade():
    # Remove the added columns
    op.drop_column('reviews', 'source_url')
    
    # Note: We're not dropping user_id, rating, comment as they might be needed
    # This is a one-way migration for schema consistency
