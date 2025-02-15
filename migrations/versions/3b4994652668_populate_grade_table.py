"""populate grade table

Revision ID: 3b4994652668
Revises: 2c282135e834
Create Date: 2025-02-16 20:00:00.708651

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from models.grade import Grade


# revision identifiers, used by Alembic.
revision: str = "3b4994652668"
down_revision: Union[str, None] = "2c282135e834"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


GRADE_ASSOCIATION_DICT = {
    "6a": 1,
    "6a+": 2,
    "6b": 3,
    "6b+": 4,
    "6c": 5,
    "6c+": 6,
    "7a": 7,
    "7a+": 8,
    "7b": 9,
    "7b+": 10,
    "7c": 11,
    "7c+": 12,
    "8a": 13,
    "8a+": 14,
    "8b": 15,
    "8b+": 16,
    "8c": 17,
    "8c+": 18,
    "9a": 19,
}


def upgrade() -> None:
    grade_list = []

    for grade_value, correspondence in GRADE_ASSOCIATION_DICT.items():
        grade_list.append(
            {"grade_value": grade_value, "correspondence": correspondence}
        )

    op.bulk_insert(
        sa.table(
            "grade",
            sa.column("grade_value", sa.String),
            sa.column("correspondence", sa.Integer),
        ),
        grade_list,
    )


def downgrade() -> None:
    op.execute(
        f"DELETE FROM grade WHERE grade_value IN {tuple(GRADE_ASSOCIATION_DICT.keys())}"
    )
