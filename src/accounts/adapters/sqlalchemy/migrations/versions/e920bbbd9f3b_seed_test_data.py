"""seed_test_data

Revision ID: e920bbbd9f3b
Revises: b46c0afb79da
Create Date: 2026-02-18 12:20:40.012750

"""

import asyncio
from decimal import Decimal
from typing import Sequence, Union

from dotenv import load_dotenv

from accounts.adapters.auth import generate_password_hash
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e920bbbd9f3b"
down_revision: Union[str, Sequence[str], None] = "b46c0afb79da"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def seed_data():
    ADMIN_PASSWORD = "admin_password"
    USER_PASSWORD = "user_password"

    admin_hash = generate_password_hash(ADMIN_PASSWORD)
    user_hash = generate_password_hash(USER_PASSWORD)

    admin_id = (
        op.get_bind()
        .execute(
            sa.text(
                "INSERT INTO base_user (email_address, full_name, password_hash, type) "
                f"VALUES ('admin@test.com', 'System Administrator', '{admin_hash}', 'admin')"
                "RETURNING id"
            )
        )
        .scalar()
    )

    op.execute(sa.text(f"INSERT INTO admin_user (id) VALUES ({admin_id})"))

    user_id = (
        op.get_bind().execute(
            sa.text(
                "INSERT INTO base_user (email_address, full_name, password_hash, type) "
                f"VALUES ('user@test.com', 'Test User', '{user_hash}', 'user')"
                "RETURNING id"
            )
        )
    ).scalar()

    op.execute(sa.text(f"INSERT INTO account_user (id) VALUES ({user_id})"))

    op.execute(
        sa.text(f"INSERT INTO account (user_id, balance) VALUES ({user_id}, 1000.0)")
    )


def upgrade() -> None:
    """Upgrade schema."""
    seed_data()


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM account")
    op.execute("DELETE FROM base_user")
