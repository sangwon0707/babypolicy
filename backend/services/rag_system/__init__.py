"""RAG (Retrieval-Augmented Generation) system for BabyPolicy chatbot."""

from .service import RagService, get_rag_service

# Backward compatibility aliases
BabyPolicyChatService = RagService
get_chat_service = get_rag_service
