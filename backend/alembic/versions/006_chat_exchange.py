"""Add chat exchange history table.

Revision ID: 006
Revises: 005
Create Date: 2026-06-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_exchanges",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("document_id", sa.UUID(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_exchanges_user_id", "chat_exchanges", ["user_id"], unique=False)
    op.create_index("ix_chat_exchanges_workspace_id", "chat_exchanges", ["workspace_id"], unique=False)
    op.create_index("ix_chat_exchanges_source_id", "chat_exchanges", ["source_id"], unique=False)
    op.create_index("ix_chat_exchanges_document_id", "chat_exchanges", ["document_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chat_exchanges_document_id", table_name="chat_exchanges")
    op.drop_index("ix_chat_exchanges_source_id", table_name="chat_exchanges")
    op.drop_index("ix_chat_exchanges_workspace_id", table_name="chat_exchanges")
    op.drop_index("ix_chat_exchanges_user_id", table_name="chat_exchanges")
    op.drop_table("chat_exchanges")
