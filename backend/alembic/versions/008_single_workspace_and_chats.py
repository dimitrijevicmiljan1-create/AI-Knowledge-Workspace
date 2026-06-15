"""Rename chat sessions to chats and add user settings.

Revision ID: 008
Revises: 007
Create Date: 2026-06-14

"""

from typing import Sequence, Union
import uuid

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("chat_sessions", "chats")
    op.execute("ALTER INDEX IF EXISTS ix_chat_sessions_user_id RENAME TO ix_chats_user_id")
    op.execute(
        "ALTER INDEX IF EXISTS ix_chat_sessions_workspace_id RENAME TO ix_chats_workspace_id"
    )

    op.alter_column("chat_messages", "session_id", new_column_name="chat_id")
    op.execute(
        "ALTER INDEX IF EXISTS ix_chat_messages_session_id RENAME TO ix_chat_messages_chat_id"
    )

    op.create_table(
        "user_settings",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("default_model", sa.String(length=128), nullable=False, server_default="gpt-4.1-mini"),
        sa.Column("temperature", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("response_length", sa.String(length=32), nullable=False, server_default="medium"),
        sa.Column("chunk_size", sa.Integer(), nullable=False, server_default="512"),
        sa.Column("chunk_overlap", sa.Integer(), nullable=False, server_default="64"),
        sa.Column("auto_index_uploads", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    connection = op.get_bind()
    users_without_workspace = connection.execute(
        sa.text(
            """
            SELECT u.id, u.email, u.full_name
            FROM users u
            LEFT JOIN workspaces w ON w.owner_id = u.id
            WHERE w.id IS NULL
            """
        )
    ).fetchall()

    for user_id, email, full_name in users_without_workspace:
        workspace_name = full_name or email.split("@")[0]
        workspace_id = uuid.uuid4()
        connection.execute(
            sa.text(
                """
                INSERT INTO workspaces (id, name, description, owner_id, created_at, updated_at)
                VALUES (:id, :name, :description, :owner_id, now(), now())
                """
            ),
            {
                "id": workspace_id,
                "name": workspace_name,
                "description": "Personal knowledge workspace",
                "owner_id": user_id,
            },
        )

    all_users = connection.execute(sa.text("SELECT id FROM users")).fetchall()
    for (user_id,) in all_users:
        connection.execute(
            sa.text(
                """
                INSERT INTO user_settings (user_id)
                VALUES (:user_id)
                ON CONFLICT (user_id) DO NOTHING
                """
            ),
            {"user_id": user_id},
        )


def downgrade() -> None:
    op.drop_table("user_settings")

    op.alter_column("chat_messages", "chat_id", new_column_name="session_id")
    op.execute(
        "ALTER INDEX IF EXISTS ix_chat_messages_chat_id RENAME TO ix_chat_messages_session_id"
    )

    op.rename_table("chats", "chat_sessions")
    op.execute("ALTER INDEX IF EXISTS ix_chats_user_id RENAME TO ix_chat_sessions_user_id")
    op.execute(
        "ALTER INDEX IF EXISTS ix_chats_workspace_id RENAME TO ix_chat_sessions_workspace_id"
    )
