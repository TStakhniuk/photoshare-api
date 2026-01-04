"""Add photos fields, tags and transformations tables

Revision ID: a1b2c3d4e5f6
Revises: 31004cf89c64
Create Date: 2025-12-27 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '31004cf89c64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add columns to existing photos table
    op.add_column('photos', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('photos', sa.Column('url', sa.String(500), nullable=False))
    op.add_column('photos', sa.Column('cloudinary_public_id', sa.String(255), nullable=False))
    op.add_column('photos', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('photos', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('photos', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))

    # Add foreign key and indexes to photos
    op.create_foreign_key('fk_photos_user_id', 'photos', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_photos_id'), 'photos', ['id'], unique=False)
    op.create_unique_constraint('uq_photos_cloudinary_public_id', 'photos', ['cloudinary_public_id'])

    # Create tags table
    op.create_table('tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)

    # Create photo_tags association table (many-to-many)
    op.create_table('photo_tags',
        sa.Column('photo_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('photo_id', 'tag_id')
    )

    # Create photo_transformations table
    op.create_table('photo_transformations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_photo_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('cloudinary_public_id', sa.String(255), nullable=False),
        sa.Column('transformation_params', sa.Text(), nullable=True),
        sa.Column('qr_code_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['original_photo_id'], ['photos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_photo_transformations_id'), 'photo_transformations', ['id'], unique=False)
    op.create_unique_constraint('uq_photo_transformations_cloudinary_public_id', 'photo_transformations', ['cloudinary_public_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop photo_transformations table
    op.drop_constraint('uq_photo_transformations_cloudinary_public_id', 'photo_transformations', type_='unique')
    op.drop_index(op.f('ix_photo_transformations_id'), table_name='photo_transformations')
    op.drop_table('photo_transformations')

    # Drop photo_tags table
    op.drop_table('photo_tags')

    # Drop tags table
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')

    # Remove columns and constraints from photos
    op.drop_constraint('uq_photos_cloudinary_public_id', 'photos', type_='unique')
    op.drop_index(op.f('ix_photos_id'), table_name='photos')
    op.drop_constraint('fk_photos_user_id', 'photos', type_='foreignkey')
    op.drop_column('photos', 'updated_at')
    op.drop_column('photos', 'created_at')
    op.drop_column('photos', 'description')
    op.drop_column('photos', 'cloudinary_public_id')
    op.drop_column('photos', 'url')
    op.drop_column('photos', 'user_id')
