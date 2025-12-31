"""Add is_active and role to users table

Revision ID: add_user_is_active_role
Revises: 271da6bba801
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_user_is_active_role'
down_revision: Union[str, Sequence[str], None] = '271da6bba801'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type for user role (if it doesn't exist)
    op.execute("DO $$ BEGIN CREATE TYPE userrole AS ENUM ('user', 'admin'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Add is_active column with default True
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    
    # Add role column with default 'user'
    op.add_column('users', sa.Column('role', sa.Enum('user', 'admin', name='userrole', create_type=False), nullable=False, server_default=sa.text("'user'")))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns
    op.drop_column('users', 'role')
    op.drop_column('users', 'is_active')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS userrole")

