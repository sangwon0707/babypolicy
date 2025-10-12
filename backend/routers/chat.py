import uuid
import json
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from .. import crud, schemas
from ..database import get_supabase
from ..services.rag_system import get_chat_service
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

    # Retrieve recent conversation history for context (last 10 messages, excluding the just-added user message)
    # This gives the AI context about previous exchanges in the conversation
    recent_messages = crud.get_recent_conversation_messages(
        supabase=supabase,
        conversation_id=conversation_id,
        limit=10
    )

    # Format conversation history for the chat service
    # Exclude the last message (the one we just added) to avoid duplication
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in recent_messages[:-1]  # Exclude the just-added user message
    ] if len(recent_messages) > 1 else []

    chat_service = get_chat_service(supabase=supabase)
    service_response = chat_service.answer(
        request.message,
        conversation_history=conversation_history,
        enable_function_calling=True  # Explicitly enable function calling
    )

    # Debug logging
    print(f"[DEBUG] Service response keys: {service_response.keys()}")
    if "function_call" in service_response:
        print(f"[DEBUG] Function call detected: {service_response['function_call']}")

    sources = [
        schemas.RagSource(
            chunk_id=source.get("id"),
            doc_id=source.get("source", ""),
            page=source.get("page"),
            content=source.get("text", ""),
        )
        for source in service_response.get("sources", [])
    ]

    # Handle function call if present
    function_call = None
    if "function_call" in service_response:
        fc = service_response["function_call"]
        print(f"[DEBUG] Processing function_call: name={fc['name']}, arguments={fc['arguments']}")
        function_call = schemas.FunctionCall(
            name=fc["name"],
            arguments=json.loads(fc["arguments"]) if isinstance(fc["arguments"], str) else fc["arguments"]
        )
        print(f"[DEBUG] Created FunctionCall schema: {function_call}")

    rag_response = schemas.ChatResponse(
        answer=service_response.get("answer", ""),
        conversation_id=request.conversation_id or uuid.uuid4(),
        sources=sources,
        function_call=function_call
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

@router.get("/conversations", response_model=List[schemas.Conversation])
def get_user_conversations(
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all conversations for the current user, ordered by most recent activity.
    """
    user_id = current_user["user_id"]
    conversations = crud.get_user_conversations(supabase=supabase, user_id=user_id)
    return conversations

@router.get("/conversations/{conversation_id}/messages", response_model=List[schemas.Message])
def get_conversation_messages(
    conversation_id: str,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all messages for a specific conversation.
    Verifies that the conversation belongs to the current user.
    """
    user_id = current_user["user_id"]

    # Verify conversation belongs to user
    conversation = crud.get_conversation(supabase, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = crud.get_conversation_messages(supabase=supabase, conversation_id=conversation_id)
    return messages

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a conversation and all its messages.
    Verifies that the conversation belongs to the current user.
    """
    user_id = current_user["user_id"]

    # Verify conversation belongs to user
    conversation = crud.get_conversation(supabase, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete conversation (messages will be cascade deleted)
    supabase.table("conversations").delete().eq("id", conversation_id).execute()

    return {"message": "Conversation deleted successfully"}

@router.post("/chat/execute-function")
def execute_function(
    request: schemas.ExecuteFunctionRequest,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a function call approved by the user.
    Currently supports: add_calendar_event
    """
    user_id = current_user["user_id"]

    if request.function_name == "add_calendar_event":
        try:
            # Parse arguments
            args = request.arguments
            title = args.get("title")
            date_str = args.get("date")
            description = args.get("description", "")

            if not title or not date_str:
                raise HTTPException(status_code=400, detail="Missing required arguments: title and date")

            # Parse datetime
            try:
                event_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)")

            # Create calendar event
            event = schemas.CalendarEventCreate(
                title=title,
                description=description,
                event_date=event_date,
                is_policy_related=True
            )

            result = crud.create_calendar_event(supabase, event, user_id)

            if not result:
                raise HTTPException(status_code=500, detail="Failed to create calendar event")

            return {
                "status": "success",
                "message": f"✅ '{title}' 일정이 캘린더에 추가되었습니다.",
                "event": result
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to execute function: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail=f"Unknown function: {request.function_name}")
