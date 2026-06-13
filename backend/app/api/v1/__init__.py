from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.embeddings import router as embeddings_router
from app.api.v1.sources import router as sources_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.users import router as users_router
from app.api.v1.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(workspaces_router)
api_router.include_router(sources_router)
api_router.include_router(documents_router)
api_router.include_router(embeddings_router)
api_router.include_router(uploads_router)
