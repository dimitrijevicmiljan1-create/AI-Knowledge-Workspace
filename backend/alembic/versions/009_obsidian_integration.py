"""Add Obsidian vault integration tables.

Revision ID: 009
Revises: 008
Create Date: 2026-06-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "obsidian_vaults",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("vault_name", sa.String(length=255), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_status", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "vault_name", name="uq_obsidian_vaults_workspace_name"),
        sa.UniqueConstraint("source_id", name="uq_obsidian_vaults_source_id"),
    )
    op.create_index("ix_obsidian_vaults_workspace_id", "obsidian_vaults", ["workspace_id"])
    op.create_index("ix_obsidian_vaults_source_id", "obsidian_vaults", ["source_id"])

    op.create_table(
        "obsidian_sync_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("vault_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("files_scanned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("documents_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("documents_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("documents_deleted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["vault_id"], ["obsidian_vaults.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_obsidian_sync_jobs_vault_id", "obsidian_sync_jobs", ["vault_id"])


def downgrade() -> None:
    op.drop_index("ix_obsidian_sync_jobs_vault_id", table_name="obsidian_sync_jobs")
    op.drop_table("obsidian_sync_jobs")
    op.drop_index("ix_obsidian_vaults_source_id", table_name="obsidian_vaults")
    op.drop_index("ix_obsidian_vaults_workspace_id", table_name="obsidian_vaults")
    op.drop_table("obsidian_vaults")
