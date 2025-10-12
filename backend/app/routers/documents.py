"""
Document Management Routes - Upload and search course materials

IMPORTANT: All documents are user-scoped. Users can ONLY access their own documents.
Vector search is automatically filtered by user_id to prevent data leakage.
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from datetime import datetime
from bson import ObjectId
from typing import List, Optional

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.util.embed import EmbeddingService
from app.services.document_processor import get_document_processor
from app.services.chunking_service import get_chunking_service
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentSearchRequest,
    DocumentSearchResult,
    DocumentType
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="PDF or PPTX file"),
    course_id: str = Form(..., description="Course ID this document belongs to"),
    document_type: DocumentType = Form(DocumentType.OTHER, description="Type of document"),
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Upload a course document (PDF or PPTX) for vectorization and RAG.

    Process:
    1. Validate user and file
    2. Extract text from document
    3. Chunk text into smaller pieces
    4. Generate embeddings for each chunk
    5. Store in MongoDB with user_id (ensures user isolation)

    **Security**: Only the uploading user can access this document.
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

        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Only PDF and PPTX are supported."
            )

        # Read file content
        file_content = await file.read()

        if len(file_content) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 50MB."
            )

        # Process document (extract text)
        doc_processor = get_document_processor()
        processed_doc = await doc_processor.process_document(
            file_content,
            file.filename,
            file.content_type
        )

        # Chunk the text
        chunking_service = get_chunking_service(chunk_size=512, chunk_overlap=50)
        chunks = chunking_service.chunk_text(
            processed_doc["text"],
            metadata={
                "filename": file.filename,
                "document_type": document_type,
                "pages": processed_doc["metadata"]["pages"]
            },
            strategy="recursive"
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content could be extracted from the document."
            )

        # Generate embeddings
        embedding_service = EmbeddingService()

        # Store main document record
        document_record = {
            "user_id": db_user_id,  # CRITICAL: User isolation
            "course_id": course_id,
            "filename": file.filename,
            "document_type": document_type,
            "mime_type": file.content_type,
            "file_size": len(file_content),
            "total_chunks": len(chunks),
            "pages": processed_doc["metadata"]["pages"],
            "raw_text": processed_doc["text"],
            "uploaded_at": datetime.utcnow(),
            "metadata": processed_doc["metadata"]
        }

        doc_result = await db.documents.insert_one(document_record)
        document_id = str(doc_result.inserted_id)

        # Store chunks with embeddings
        chunks_to_insert = []
        for chunk in chunks:
            # Generate embedding for this chunk
            embedding = await embedding_service.generate_embedding(chunk["text"])

            chunk_doc = {
                "user_id": db_user_id,  # CRITICAL: User isolation
                "document_id": document_id,
                "course_id": course_id,
                "filename": file.filename,
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "char_count": chunk["char_count"],
                "embedding": embedding,
                "page_number": chunk["metadata"].get("page"),
                "created_at": datetime.utcnow(),
                "metadata": chunk["metadata"]
            }
            chunks_to_insert.append(chunk_doc)

        if chunks_to_insert:
            await db.document_chunks.insert_many(chunks_to_insert)

        return DocumentUploadResponse(
            id=document_id,
            user_id=db_user_id,
            course_id=course_id,
            filename=file.filename,
            document_type=document_type,
            file_size=len(file_content),
            total_chunks=len(chunks),
            pages=processed_doc["metadata"]["pages"],
            uploaded_at=document_record["uploaded_at"],
            message=f"Successfully processed {len(chunks)} chunks from {processed_doc['metadata']['pages']} pages"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/", response_model=List[DocumentListResponse])
async def list_documents(
    course_id: Optional[str] = None,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    List all documents uploaded by the current user.

    **Security**: Only returns documents belonging to the authenticated user.
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

        # Build query (ALWAYS filter by user_id)
        query = {"user_id": db_user_id}

        if course_id:
            query["course_id"] = course_id

        # Fetch documents
        cursor = db.documents.find(query).sort("uploaded_at", -1)
        documents = await cursor.to_list(length=None)

        return [
            DocumentListResponse(
                id=str(doc["_id"]),
                course_id=doc["course_id"],
                filename=doc["filename"],
                document_type=doc["document_type"],
                file_size=doc["file_size"],
                total_chunks=doc["total_chunks"],
                pages=doc["pages"],
                uploaded_at=doc["uploaded_at"]
            )
            for doc in documents
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.post("/search", response_model=List[DocumentSearchResult])
async def search_documents(
    search_request: DocumentSearchRequest,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Semantic search through user's documents using vector similarity.

    **Security**: Only searches documents belonging to the authenticated user.
    **Uses**: MongoDB Atlas Vector Search with user_id filtering.
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

        # Generate embedding for query
        embedding_service = EmbeddingService()
        query_embedding = await embedding_service.generate_embedding(search_request.query)

        # Build vector search pipeline
        # CRITICAL: ALWAYS filter by user_id to prevent data leakage
        match_filter = {"user_id": db_user_id}

        if search_request.course_id:
            match_filter["course_id"] = search_request.course_id

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_search_index",  # Must be created in MongoDB Atlas
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": search_request.limit
                }
            },
            {
                "$match": match_filter  # User isolation filter
            },
            {
                "$project": {
                    "_id": 1,
                    "document_id": 1,
                    "filename": 1,
                    "course_id": 1,
                    "text": 1,
                    "chunk_index": 1,
                    "page_number": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        # Execute search
        results = []
        async for doc in db.document_chunks.aggregate(pipeline):
            results.append(DocumentSearchResult(
                chunk_id=str(doc["_id"]),
                document_id=doc["document_id"],
                filename=doc["filename"],
                course_id=doc["course_id"],
                text=doc["text"],
                relevance_score=doc.get("score", 0.0),
                chunk_index=doc["chunk_index"],
                page_number=doc.get("page_number")
            ))

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search documents: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Delete a document and all its chunks.

    **Security**: Can only delete own documents.
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

        # Delete document (with user_id check for security)
        doc_result = await db.documents.delete_one({
            "_id": ObjectId(document_id),
            "user_id": db_user_id  # Ensure user owns this document
        })

        if doc_result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or you don't have permission to delete it"
            )

        # Delete all chunks for this document
        await db.document_chunks.delete_many({
            "document_id": document_id,
            "user_id": db_user_id  # Extra safety
        })

        return {
            "success": True,
            "message": "Document and all chunks deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
