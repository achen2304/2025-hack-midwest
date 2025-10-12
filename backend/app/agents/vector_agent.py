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
        """
        Search for relevant documents using vector similarity.

        SECURITY: This method ALWAYS filters by user_id to ensure users can only
        access their own documents. Never remove this filter.

        Args:
            query: Search query text
            user_id: User's MongoDB ID (REQUIRED - enforces user isolation)
            course_id: Optional course filter
            limit: Maximum number of results

        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # Generate embedding for query
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Build user isolation filter (CRITICAL - prevents data leakage)
            match_filter = {"user_id": user_id}  # ALWAYS filter by user_id

            if course_id:
                match_filter["course_id"] = course_id

            # Build MongoDB aggregation pipeline for vector search
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_search_index",  # Must be created in Atlas
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": 100,
                        "limit": limit
                    }
                },
                {
                    "$match": match_filter  # User isolation - DO NOT REMOVE
                },
                {
                    "$project": {
                        "_id": 1,
                        "document_id": 1,
                        "text": 1,
                        "course_id": 1,
                        "filename": 1,
                        "chunk_index": 1,
                        "page_number": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]

            # Execute search on document_chunks collection
            results = []
            async for doc in self.db.document_chunks.aggregate(pipeline):
                results.append({
                    "id": str(doc["_id"]),
                    "document_id": doc.get("document_id"),
                    "content": doc.get("text", ""),
                    "course_id": doc.get("course_id"),
                    "filename": doc.get("filename"),
                    "chunk_index": doc.get("chunk_index", 0),
                    "page_number": doc.get("page_number"),
                    "relevance_score": doc.get("score", 0.0)
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
        """
        Get comprehensive context about a course.

        SECURITY: This method ALWAYS filters by user_id to ensure users can only
        access their own course materials.

        Args:
            user_id: User's MongoDB ID (REQUIRED - enforces user isolation)
            course_id: Course to get context for
            topic: Optional specific topic to search for

        Returns:
            Dictionary with course context and documents
        """
        try:
            if topic:
                # Use vector search for specific topic
                docs = await self.search_documents(topic, user_id, course_id, limit=10)
            else:
                # Get all recent document chunks for course
                # CRITICAL: ALWAYS filter by user_id
                cursor = self.db.document_chunks.find({
                    "user_id": user_id,  # User isolation
                    "course_id": course_id
                }).sort("_id", -1).limit(10)

                docs = []
                async for doc in cursor:
                    docs.append({
                        "id": str(doc["_id"]),
                        "document_id": doc.get("document_id"),
                        "content": doc.get("text", ""),
                        "filename": doc.get("filename"),
                        "chunk_index": doc.get("chunk_index", 0),
                        "page_number": doc.get("page_number")
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
