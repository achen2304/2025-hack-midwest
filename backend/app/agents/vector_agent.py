"""
Vector Agent - Provides contextual data via vector search
"""
from typing import List, Dict, Any, Optional


class VectorAgent:
    """
    Foundational agent that provides contextual data via vector search.
    - Performs similarity searches on vectorized data
    - Provides context to other agents
    - Helps prioritize topics based on content analysis
    """

    def __init__(self, db, embedding_service):
        self.db = db
        self.embedding_service = embedding_service

    async def search_documents(
        self,
        query: str,
        user_id: str,
        course_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Build MongoDB aggregation pipeline for vector search
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_search_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": 100,
                        "limit": limit
                    }
                },
                {
                    "$match": {"user_id": user_id}
                }
            ]

            if course_id:
                pipeline[1]["$match"]["course_id"] = course_id

            # Execute search
            results = []
            async for doc in self.db.documents.aggregate(pipeline):
                results.append({
                    "id": str(doc["_id"]),
                    "content": doc.get("rawText", ""),
                    "course_id": doc.get("course_id"),
                    "document_type": doc.get("documentType"),
                    "file_name": doc.get("fileName"),
                    "relevance_score": doc.get("score", 0)
                })

            return results

        except Exception as e:
            print(f"Error in vector search: {e}")
            return []

    async def get_course_context(
        self,
        user_id: str,
        course_id: str,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive context about a course"""
        try:
            if topic:
                docs = await self.search_documents(topic, user_id, course_id, limit=10)
            else:
                # Get all recent documents for course
                cursor = self.db.documents.find({
                    "user_id": user_id,
                    "course_id": course_id
                }).sort("_id", -1).limit(10)

                docs = []
                async for doc in cursor:
                    docs.append({
                        "id": str(doc["_id"]),
                        "content": doc.get("rawText", ""),
                        "document_type": doc.get("documentType"),
                        "file_name": doc.get("fileName")
                    })

            return {
                "course_id": course_id,
                "documents_found": len(docs),
                "documents": docs
            }

        except Exception as e:
            print(f"Error getting course context: {e}")
            return {
                "course_id": course_id,
                "documents_found": 0,
                "documents": []
            }


def create_vector_agent(db, embedding_service):
    """Create vector agent with database and embedding dependencies"""
    return VectorAgent(db, embedding_service)
