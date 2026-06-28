import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.obsidian_vault import ObsidianVault, ObsidianVaultSyncStatus
from app.models.workspace import Workspace


class ObsidianVaultRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        workspace_id: uuid.UUID,
        source_id: uuid.UUID,
        vault_name: str,
        sync_status: ObsidianVaultSyncStatus = ObsidianVaultSyncStatus.pending,
    ) -> ObsidianVault:
        vault = ObsidianVault(
            workspace_id=workspace_id,
            source_id=source_id,
            vault_name=vault_name,
            sync_status=sync_status,
        )
        self.db.add(vault)
        self.db.commit()
        self.db.refresh(vault)
        return vault

    def get_by_id(self, vault_id: uuid.UUID) -> ObsidianVault | None:
        statement = (
            select(ObsidianVault)
            .options(joinedload(ObsidianVault.source))
            .where(ObsidianVault.id == vault_id)
        )
        return self.db.scalars(statement).unique().first()

    def get_by_id_for_user(self, vault_id: uuid.UUID, user_id: uuid.UUID) -> ObsidianVault | None:
        statement = (
            select(ObsidianVault)
            .join(Workspace, ObsidianVault.workspace_id == Workspace.id)
            .options(joinedload(ObsidianVault.source))
            .where(
                ObsidianVault.id == vault_id,
                Workspace.owner_id == user_id,
            )
        )
        return self.db.scalars(statement).unique().first()

    def get_by_workspace_and_name(
        self,
        workspace_id: uuid.UUID,
        vault_name: str,
    ) -> ObsidianVault | None:
        statement = select(ObsidianVault).where(
            ObsidianVault.workspace_id == workspace_id,
            ObsidianVault.vault_name == vault_name,
        )
        return self.db.scalar(statement)

    def list_by_workspace(self, workspace_id: uuid.UUID) -> list[ObsidianVault]:
        statement = (
            select(ObsidianVault)
            .options(joinedload(ObsidianVault.source))
            .where(ObsidianVault.workspace_id == workspace_id)
            .order_by(ObsidianVault.created_at.desc())
        )
        return list(self.db.scalars(statement).unique().all())

    def update(self, vault: ObsidianVault, **fields: object) -> ObsidianVault:
        for field, value in fields.items():
            if value is not None:
                setattr(vault, field, value)
        self.db.commit()
        self.db.refresh(vault)
        return vault

    def delete(self, vault: ObsidianVault) -> None:
        self.db.delete(vault)
        self.db.commit()
