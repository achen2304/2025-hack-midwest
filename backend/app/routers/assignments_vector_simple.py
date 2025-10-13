# app/routers/assignments_vector_simple.py
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from typing import List
from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.services.embedder import embed_text

router = APIRouter(prefix="/assignments", tags=["Assignments"])

async def _resolve_user_id(db, user) -> str:
    user_doc = None
    try:
        user_doc = await db.users.find_one({"_id": ObjectId(user.get("sub"))})
    except Exception:
        pass
    if not user_doc:
        user_doc = await db.users.find_one({"email": user.get("email")})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return str(user_doc["_id"])

@router.get("/search/vector-simple")
async def vector_simple_search(
    q: str = Query(..., min_length=1, description="Semantic text query"),
    limit: int = Query(10, ge=1, le=50),
    user = Depends(verify_backend_token),
    db = Depends(get_database),
):
    uid = await _resolve_user_id(db, user)
    qvec = embed_text(q)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "assignments_vs",
                "path": "embedding",
                "queryVector": qvec,
                "numCandidates": max(100, limit * 8),
                "limit": limit,
                "filter": { "user_id": uid }
            }
        },
        { "$project": {
            "_id": 0,
            "id": "$canvas_id",
            "name": "$title",
            "due_at": "$due_date",
            "course_id": 1,
            "_score": { "$meta": "vectorSearchScore" }
        }}
    ]

    docs = await db.assignments.aggregate(pipeline).to_list(length=limit)
    # return only what the UI needs
    return docs
