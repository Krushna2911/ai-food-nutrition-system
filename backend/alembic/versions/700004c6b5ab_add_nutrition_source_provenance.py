
"""add nutrition source provenance

Revision ID: 700004c6b5ab
Revises: 54866dc0fed8
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "700004c6b5ab"
down_revision: Union[str, Sequence[str], None] = "54866dc0fed8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "nutrition",
        sa.Column("fdc_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "nutrition",
        sa.Column("nutrition_source", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("nutrition", "nutrition_source")
    op.drop_column("nutrition", "fdc_id")
