"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

DO-178C Traceability: Migration ${up_revision}
${config.get_main_option('purpose', '')}
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """
    Apply forward migration.

    This function applies database schema changes for this migration.
    All changes must be reversible (see downgrade() function).
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Revert migration.

    This function reverts all changes made by upgrade().
    IMPORTANT: Test downgrade() to ensure reversibility.
    """
    ${downgrades if downgrades else "pass"}
