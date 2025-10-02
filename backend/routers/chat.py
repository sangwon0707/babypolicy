import uuid

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from .. import crud, schemas
from ..database import get_supabase
from ..services.babypolicy_chat import get_chat_service
from ..auth.utils import get_current_user

router = APIRouter()

@router.post("/chat", response_model=schemas.ChatResponse)
def chat_with_rag(
    request: schemas.ChatRequest,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    # Get or create conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation = crud.create_conversation(supabase=supabase, user_id=user_id, title=request.message[:50])
        conversation_id = conversation["id"]
    else:
        conversation = crud.get_conversation(supabase, conversation_id)
        if not conversation or conversation["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    crud.create_message(
        supabase=supabase,
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )

    chat_service = get_chat_service(supabase=supabase)
    service_response = chat_service.answer(request.message)

    sources = [
        schemas.RagSource(
            chunk_id=source.get("id"),
            doc_id=source.get("source", ""),
            page=source.get("page"),
            content=source.get("text", ""),
        )
        for source in service_response.get("sources", [])
    ]

    rag_response = schemas.ChatResponse(
        answer=service_response.get("answer", ""),
        conversation_id=request.conversation_id or uuid.uuid4(),
        sources=sources,
    )

    # Save AI message
    crud.create_message(
        supabase=supabase,
        conversation_id=conversation_id,
        role="assistant",
        content=rag_response.answer,
        rag_sources=[source.dict() for source in rag_response.sources]
    )

    # Update conversation_id in the final response
    rag_response.conversation_id = conversation_id

    return rag_response
