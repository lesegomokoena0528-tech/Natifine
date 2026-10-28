"""audit log user_id to string

Revision ID: b1f6c9a2d4e7
Revises: fd274eb3c917
Create Date: 2026-10-13 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1f6c9a2d4e7'
down_revision = 'fd274eb3c917'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.Integer(),
            type_=sa.String(length=36),
            existing_nullable=False
        )


def downgrade():
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.String(length=36),
            type_=sa.Integer(),
            existing_nullable=False
        )
