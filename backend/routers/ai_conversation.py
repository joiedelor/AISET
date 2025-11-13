"""
AI Conversation Router
DO-178C Traceability: REQ-API-005
Purpose: AI chat and requirements elicitation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database.connection import get_db
from models.ai_conversation import AIConversation, AIMessage, MessageRole
from services.ai_service import ai_service

router = APIRouter()


class ChatMessage(BaseModel):
    """Schema for chat message."""
    conversation_id: int
    content: str


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    project_id: int
    title: str = "Requirements Elicitation Session"
    purpose: str = "requirements_elicitation"
    created_by: str = "system"


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    role: MessageRole
    content: str

    class Config:
        from_attributes = True


@router.post("/conversations")
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new AI conversation.

    Traceability: REQ-AI-011 - Conversation creation
    """
    db_conversation = AIConversation(
        project_id=conversation.project_id,
        title=conversation.title,
        purpose=conversation.purpose,
        ai_service=ai_service.provider.__class__.__name__.replace("Provider", "").lower(),
        model_name=ai_service.get_current_model(),
        created_by=conversation.created_by
    )

    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return {
        "conversation_id": db_conversation.id,
        "title": db_conversation.title,
        "model": db_conversation.model_name
    }


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    message: str,
    db: Session = Depends(get_db)
):
    """
    Send a message in a conversation and get AI response.

    Traceability: REQ-AI-012 - Message exchange
    """
    # Get conversation
    conversation = db.query(AIConversation).filter(AIConversation.id == conversation_id).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    user_message = AIMessage(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=message
    )
    db.add(user_message)
    db.commit()

    # Get conversation history
    messages = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation_id
    ).order_by(AIMessage.created_at).all()

    # Format messages for AI
    ai_messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in messages
    ]

    try:
        # Get AI response
        response = await ai_service.requirements_elicitation(message)

        # Save AI response
        ai_message = AIMessage(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response
        )
        db.add(ai_message)
        db.commit()

        return {
            "message": response,
            "conversation_id": conversation_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    """
    Get all messages in a conversation.

    Traceability: REQ-AI-013 - Message retrieval
    """
    messages = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation_id
    ).order_by(AIMessage.created_at).all()

    return messages


@router.post("/conversations/{conversation_id}/extract")
async def extract_requirements(conversation_id: int, db: Session = Depends(get_db)):
    """
    Extract requirements from conversation.

    Traceability: REQ-AI-014 - Requirements extraction API
    """
    # Get all messages
    messages = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation_id
    ).order_by(AIMessage.created_at).all()

    # Combine conversation text
    conversation_text = "\n".join([
        f"{msg.role.value}: {msg.content}"
        for msg in messages
    ])

    try:
        # Extract requirements
        extracted = await ai_service.extract_requirements(conversation_text)

        return {
            "extracted_count": len(extracted),
            "requirements": extracted
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")
