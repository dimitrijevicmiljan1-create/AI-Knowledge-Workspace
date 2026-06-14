import time
import uuid

from sqlalchemy.orm import Session

from app.ai.chat.provider import ChatProvider
from app.ai.chat.schemas import ChatMessage
from app.ai.chat import get_chat_provider
from app.models.user import User
from app.rag.citation_builder import CitationBuilder
from app.rag.context_builder import RetrievalContextBuilder
from app.rag.conversation_memory import ConversationMemoryLoader
from app.rag.prompt_builder import PromptBuilder
from app.rag.retrieval_context import ContextChunk
from app.repositories.chat_exchange_repository import ChatExchangeRepository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    RetrievedChunk,
    SessionMessageRequest,
    SessionMessageResponse,
)
from app.schemas.search import SearchRequest
from app.services.chat_session_service import ChatSessionService
from app.services.search_service import SearchService


class RAGService:
    NO_CONTEXT_ANSWER = (
        "I could not find relevant information in your knowledge base to answer this question."
    )

    def __init__(
        self,
        db: Session,
        search_service: SearchService | None = None,
        chat_provider: ChatProvider | None = None,
        chat_session_service: ChatSessionService | None = None,
    ) -> None:
        self.db = db
        self.search_service = search_service or SearchService(db)
        self.chat_provider = chat_provider or get_chat_provider()
        self.chat_session_service = chat_session_service or ChatSessionService(db)
        self.context_builder = RetrievalContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.citation_builder = CitationBuilder()
        self.memory_loader = ConversationMemoryLoader()
        self.chat_exchange_repository = ChatExchangeRepository(db)

    def chat_workspace(
        self,
        user: User,
        workspace_id: uuid.UUID,
        chat_in: ChatRequest,
    ) -> ChatResponse:
        search_response = self.search_service.search_workspace(
            user,
            workspace_id,
            SearchRequest(query=chat_in.question, top_k=chat_in.top_k),
        )
        return self._generate_response(
            user=user,
            workspace_id=workspace_id,
            question=chat_in.question,
            top_k=chat_in.top_k,
            search_response_results=search_response.results,
        )

    def chat_source(
        self,
        user: User,
        source_id: uuid.UUID,
        chat_in: ChatRequest,
    ) -> ChatResponse:
        from app.repositories.source_repository import SourceRepository

        search_response = self.search_service.search_source(
            user,
            source_id,
            SearchRequest(query=chat_in.question, top_k=chat_in.top_k),
        )
        source = SourceRepository(self.db).get_by_id(source_id)
        assert source is not None

        return self._generate_response(
            user=user,
            workspace_id=source.workspace_id,
            question=chat_in.question,
            top_k=chat_in.top_k,
            search_response_results=search_response.results,
            source_id=source_id,
        )

    def chat_document(
        self,
        user: User,
        document_id: uuid.UUID,
        chat_in: ChatRequest,
    ) -> ChatResponse:
        from app.repositories.document_repository import DocumentRepository
        from app.repositories.source_repository import SourceRepository

        search_response = self.search_service.search_document(
            user,
            document_id,
            SearchRequest(query=chat_in.question, top_k=chat_in.top_k),
        )
        document = DocumentRepository(self.db).get_by_id(document_id)
        assert document is not None
        source = SourceRepository(self.db).get_by_id(document.source_id)
        assert source is not None

        return self._generate_response(
            user=user,
            workspace_id=source.workspace_id,
            question=chat_in.question,
            top_k=chat_in.top_k,
            search_response_results=search_response.results,
            document_id=document_id,
        )

    def chat_session_message(
        self,
        user: User,
        session_id: uuid.UUID,
        message_in: SessionMessageRequest,
    ) -> SessionMessageResponse:
        session, history = self.chat_session_service.load_conversation_history(user, session_id)
        retrieval_query = self.memory_loader.build_retrieval_query(message_in.message, history)

        search_response = self.search_service.search_workspace(
            user,
            session.workspace_id,
            SearchRequest(query=retrieval_query, top_k=message_in.top_k),
        )

        response = self._generate_response(
            user=user,
            workspace_id=session.workspace_id,
            question=message_in.message,
            top_k=message_in.top_k,
            search_response_results=search_response.results,
            history=history,
        )

        self.chat_session_service.persist_exchange(
            session_id=session_id,
            user_message=message_in.message,
            assistant_message=response.answer,
        )

        return SessionMessageResponse(
            answer=response.answer,
            citations=response.citations,
        )

    def _generate_response(
        self,
        *,
        user: User,
        workspace_id: uuid.UUID,
        question: str,
        top_k: int,
        search_response_results: list,
        source_id: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
        history: list | None = None,
    ) -> ChatResponse:
        started_at = time.perf_counter()

        context = self.context_builder.build(search_response_results)
        citations = self.citation_builder.build(context)
        retrieved_chunks = self._to_retrieved_chunks(context.chunks)

        if context.is_empty:
            answer = self.NO_CONTEXT_ANSWER
        else:
            messages = self.prompt_builder.build(question, context, history=history)
            answer = self.chat_provider.generate_answer(
                [ChatMessage(**message) for message in messages]
            )

        exchange = self.chat_exchange_repository.create(
            user_id=user.id,
            workspace_id=workspace_id,
            source_id=source_id,
            document_id=document_id,
            question=question,
            answer=answer,
        )

        processing_time = round(time.perf_counter() - started_at, 4)
        return ChatResponse(
            answer=answer,
            citations=citations,
            retrieved_chunks=retrieved_chunks,
            processing_time=processing_time,
            exchange_id=exchange.id,
        )

    def _to_retrieved_chunks(self, chunks: list[ContextChunk]) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                source_id=chunk.source_id,
                document_title=chunk.document_title,
                content=chunk.content,
                similarity_score=chunk.similarity_score,
            )
            for chunk in chunks
        ]
