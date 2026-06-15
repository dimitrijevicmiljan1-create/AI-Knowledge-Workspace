from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.chats import router as chats_router
from app.api.v1.chunks import router as chunks_router
from app.api.v1.documents import router as documents_router
from app.api.v1.embeddings import router as embeddings_router
from app.api.v1.github import router as github_router
from app.api.v1.search import router as search_router
from app.api.v1.settings import router as settings_router
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
api_router.include_router(chunks_router)
api_router.include_router(embeddings_router)
api_router.include_router(search_router)
api_router.include_router(chat_router)
api_router.include_router(chats_router)
api_router.include_router(settings_router)
api_router.include_router(github_router)
api_router.include_router(uploads_router)
