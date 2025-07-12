"""remove processing status

Revision ID: 2b469c6f3817
Revises: 9c8d16f8c7aa
Create Date: 2025-07-12 14:56:58.041755

"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "2b469c6f3817"
down_revision: Union[str, Sequence[str], None] = "9c8d16f8c7aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ENUM_NAME = "status"
OLD_VALUE = "PROCESSING"
NEW_VALUE = "SENT"
TABLE_NAME = "reminders"
COLUMN_NAME = "status"


def upgrade():
    op.alter_column(TABLE_NAME, COLUMN_NAME, server_default=None)

    op.execute(
        f"""
        UPDATE {TABLE_NAME}
        SET {COLUMN_NAME} = '{NEW_VALUE}'
        WHERE {COLUMN_NAME}::text = '{OLD_VALUE}';
    """
    )
    temp_type = ENUM_NAME + "_old"
    op.execute(f"ALTER TYPE {ENUM_NAME} RENAME TO {temp_type};")

    new_enum = postgresql.ENUM("PENDING", "SENT", "FAILED", name=ENUM_NAME)
    new_enum.create(op.get_bind())

    op.execute(
        f"""
        ALTER TABLE {TABLE_NAME}
        ALTER COLUMN {COLUMN_NAME}
        TYPE {ENUM_NAME}
        USING {COLUMN_NAME}::text::{ENUM_NAME};
    """
    )

    op.execute(f"DROP TYPE {temp_type};")

    op.alter_column(TABLE_NAME, COLUMN_NAME, server_default="PENDING")


def downgrade():
    op.alter_column(TABLE_NAME, COLUMN_NAME, server_default=None)

    temp_type = ENUM_NAME + "_new"
    op.execute(f"ALTER TYPE {ENUM_NAME} RENAME TO {temp_type};")

    old_enum = postgresql.ENUM(
        "PENDING", "PROCESSING", "SENT", "FAILED", name=ENUM_NAME
    )
    old_enum.create(op.get_bind())

    op.execute(
        f"""
        ALTER TABLE {TABLE_NAME}
        ALTER COLUMN {COLUMN_NAME}
        TYPE {ENUM_NAME}
        USING {COLUMN_NAME}::text::{ENUM_NAME};
    """
    )

    op.execute(f"DROP TYPE {temp_type};")

    op.alter_column(TABLE_NAME, COLUMN_NAME, server_default="PENDING")
