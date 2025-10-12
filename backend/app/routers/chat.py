"""
Study Assistant Chat Routes - RAG-powered conversational tutor

Provides a chatbot interface where students can:
- Ask questions about their course materials
- Get explanations based on uploaded documents
- Receive study help with source citations
- Maintain conversation context
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId
from typing import List, Optional

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.agents import get_study_assistant, create_vector_agent
from app.util.embed import EmbeddingService
from app.models.schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    DocumentSource,
    ChatMessageRole,
    DocumentSummaryRequest,
    DocumentSummaryResponse
)

router = APIRouter(prefix="/chat", tags=["Study Assistant Chat"])


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_request: ChatSessionCreate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Create a new chat session with the study assistant.

    A session groups related messages together and maintains conversation context.
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Create chat session
        session_doc = {
            "user_id": db_user_id,
            "course_id": session_request.course_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0,
            "is_active": True
        }

        result = await db.chat_sessions.insert_one(session_doc)
        session_id = str(result.inserted_id)

        # Process initial message if provided
        if session_request.initial_message:
            # Get vector agent and study assistant
            embedding_service = EmbeddingService()
            vector_agent = create_vector_agent(db, embedding_service)
            assistant = get_study_assistant()

            # Answer the initial question
            response = await assistant.answer_question(
                question=session_request.initial_message,
                user_id=db_user_id,
                course_id=session_request.course_id,
                conversation_history=[],
                vector_agent=vector_agent,
                db=db
            )

            # Store user message
            user_message = {
                "session_id": session_id,
                "role": "user",
                "content": session_request.initial_message,
                "timestamp": datetime.utcnow()
            }
            await db.chat_messages.insert_one(user_message)

            # Store assistant response
            assistant_message = {
                "session_id": session_id,
                "role": "assistant",
                "content": response["answer"],
                "sources": response.get("sources", []),
                "needs_clarification": response.get("needs_clarification", False),
                "follow_up_suggestions": response.get("follow_up_suggestions", []),
                "documents_found": response.get("documents_found", 0),
                "timestamp": datetime.utcnow()
            }
            await db.chat_messages.insert_one(assistant_message)

            # Update message count
            await db.chat_sessions.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"message_count": 2, "updated_at": datetime.utcnow()}}
            )

            session_doc["message_count"] = 2

        return ChatSessionResponse(
            id=session_id,
            user_id=db_user_id,
            course_id=session_request.course_id,
            created_at=session_doc["created_at"],
            updated_at=session_doc["updated_at"],
            message_count=session_doc["message_count"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat session: {str(e)}"
        )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: str,
    message_request: ChatMessageRequest,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Send a message to the study assistant and get a response.

    The assistant will:
    1. Search relevant documents (RAG)
    2. Use conversation history for context
    3. Generate an informed answer
    4. Provide source citations
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Verify session belongs to user
        session = await db.chat_sessions.find_one({
            "_id": ObjectId(session_id),
            "user_id": db_user_id
        })

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )

        # Get conversation history (last 10 messages)
        cursor = db.chat_messages.find({
            "session_id": session_id
        }).sort("timestamp", -1).limit(10)

        conversation_history = []
        async for msg in cursor:
            conversation_history.insert(0, {
                "role": msg.get("role"),
                "content": msg.get("content"),
                "timestamp": msg.get("timestamp")
            })

        # Get vector agent and study assistant
        embedding_service = EmbeddingService()
        vector_agent = create_vector_agent(db, embedding_service)
        assistant = get_study_assistant()

        # Use course_id from request, or fall back to session course_id
        course_id = message_request.course_id or session.get("course_id")

        # Get AI response
        response = await assistant.answer_question(
            question=message_request.message,
            user_id=db_user_id,
            course_id=course_id,
            conversation_history=conversation_history,
            vector_agent=vector_agent,
            db=db
        )

        # Store user message
        user_message = {
            "session_id": session_id,
            "role": "user",
            "content": message_request.message,
            "timestamp": datetime.utcnow()
        }
        await db.chat_messages.insert_one(user_message)

        # Store assistant response
        assistant_message_doc = {
            "session_id": session_id,
            "role": "assistant",
            "content": response["answer"],
            "sources": response.get("sources", []),
            "needs_clarification": response.get("needs_clarification", False),
            "follow_up_suggestions": response.get("follow_up_suggestions", []),
            "documents_found": response.get("documents_found", 0),
            "timestamp": datetime.utcnow()
        }
        result = await db.chat_messages.insert_one(assistant_message_doc)

        # Update session
        await db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$inc": {"message_count": 2},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        # Format sources
        sources = [
            DocumentSource(
                document_id=src["document_id"],
                filename=src["filename"],
                page_number=src.get("page_number"),
                chunk_index=src["chunk_index"],
                relevance_score=src["relevance_score"]
            )
            for src in response.get("sources", [])
        ]

        return ChatMessageResponse(
            id=str(result.inserted_id),
            session_id=session_id,
            role=ChatMessageRole.ASSISTANT,
            content=response["answer"],
            sources=sources,
            needs_clarification=response.get("needs_clarification", False),
            follow_up_suggestions=response.get("follow_up_suggestions", []),
            documents_found=response.get("documents_found", 0),
            timestamp=assistant_message_doc["timestamp"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Get the full conversation history for a chat session.
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Verify session belongs to user
        session = await db.chat_sessions.find_one({
            "_id": ObjectId(session_id),
            "user_id": db_user_id
        })

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )

        # Get all messages
        cursor = db.chat_messages.find({
            "session_id": session_id
        }).sort("timestamp", 1).limit(limit)

        messages = []
        async for msg in cursor:
            # Format sources if present
            sources = []
            if msg.get("sources"):
                sources = [
                    DocumentSource(**src) if isinstance(src, dict) else src
                    for src in msg["sources"]
                ]

            messages.append(ChatMessageResponse(
                id=str(msg["_id"]),
                session_id=session_id,
                role=ChatMessageRole(msg["role"]),
                content=msg["content"],
                sources=sources,
                needs_clarification=msg.get("needs_clarification", False),
                follow_up_suggestions=msg.get("follow_up_suggestions", []),
                documents_found=msg.get("documents_found", 0),
                timestamp=msg["timestamp"]
            ))

        return ChatHistoryResponse(
            session_id=session_id,
            course_id=session.get("course_id"),
            messages=messages,
            total_messages=len(messages),
            created_at=session["created_at"],
            updated_at=session["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    limit: int = 20,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    List all chat sessions for the current user.
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Get sessions
        cursor = db.chat_sessions.find({
            "user_id": db_user_id
        }).sort("updated_at", -1).limit(limit)

        sessions = []
        async for session in cursor:
            sessions.append(ChatSessionResponse(
                id=str(session["_id"]),
                user_id=db_user_id,
                course_id=session.get("course_id"),
                created_at=session["created_at"],
                updated_at=session["updated_at"],
                message_count=session.get("message_count", 0)
            ))

        return sessions

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list chat sessions: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Delete a chat session and all its messages.
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Delete session (with user verification)
        result = await db.chat_sessions.delete_one({
            "_id": ObjectId(session_id),
            "user_id": db_user_id
        })

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )

        # Delete all messages in the session
        await db.chat_messages.delete_many({"session_id": session_id})

        return {
            "success": True,
            "message": "Chat session and all messages deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat session: {str(e)}"
        )


@router.post("/documents/summarize", response_model=DocumentSummaryResponse)
async def summarize_document(
    request: DocumentSummaryRequest,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Generate a summary of a specific document using AI.
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Verify document belongs to user
        document = await db.documents.find_one({
            "_id": ObjectId(request.document_id),
            "user_id": db_user_id
        })

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Get study assistant
        assistant = get_study_assistant()

        # Generate summary
        summary_result = await assistant.summarize_document(
            document_id=request.document_id,
            user_id=db_user_id,
            db=db
        )

        return DocumentSummaryResponse(
            document_id=request.document_id,
            filename=document.get("filename", "Unknown"),
            summary=summary_result["summary"],
            key_topics=summary_result.get("key_topics", []),
            chunks_analyzed=summary_result.get("chunks_analyzed", 0)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize document: {str(e)}"
        )
