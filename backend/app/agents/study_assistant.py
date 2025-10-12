"""
Study Assistant Agent - RAG-powered conversational tutor for students

This agent helps students study by:
1. Answering questions about their uploaded course materials
2. Providing explanations and examples
3. Referencing study guides and documents
4. Maintaining conversation context
"""
from typing import List, Dict, Any, Optional
from strands import Agent


class StudyAssistantAgent:
    """
    Conversational AI tutor that uses RAG (Retrieval-Augmented Generation)
    to help students study their course materials.

    Features:
    - Answers questions based on user's documents
    - Provides explanations and examples
    - References specific pages/slides
    - Maintains conversation history
    - Adapts to student's understanding level
    """

    def __init__(self):
        """Initialize the Study Assistant Agent"""
        self.agent = Agent(
            name="StudyAssistantAgent",
            system_prompt="""You are an expert study assistant and tutor for college students.

Your role is to help students understand their course materials by:
1. Answering questions based on their uploaded documents (lecture notes, slides, textbooks)
2. Providing clear, concise explanations
3. Breaking down complex concepts into simpler terms
4. Giving relevant examples when helpful
5. Referencing specific parts of their documents
6. Encouraging critical thinking

Guidelines:
- ALWAYS base your answers on the provided document context when available
- If information is not in the documents, say so clearly
- Reference specific documents, pages, or slides when relevant
- Ask clarifying questions if the student's question is unclear
- Adjust explanation complexity based on student's responses
- Be encouraging and supportive
- If a concept builds on prior knowledge, check if the student understands the prerequisites

Format your responses to be:
- Clear and well-structured
- Academic but approachable
- Helpful for exam preparation
- Focused on understanding, not just memorization

When referencing documents, use this format:
"According to [filename, page X]: [relevant content]"
"""
        )

    async def answer_question(
        self,
        question: str,
        user_id: str,
        course_id: Optional[str],
        conversation_history: List[Dict[str, Any]],
        vector_agent,
        db
    ) -> Dict[str, Any]:
        """
        Answer a student's question using RAG.

        Args:
            question: Student's question
            user_id: User's MongoDB ID (for document retrieval)
            course_id: Optional course filter
            conversation_history: Recent messages for context
            vector_agent: Vector agent instance for document retrieval
            db: Database instance

        Returns:
            {
                "answer": str,
                "sources": List[Dict],
                "needs_clarification": bool,
                "follow_up_suggestions": List[str]
            }
        """
        try:
            # Step 1: Retrieve relevant documents using vector search
            search_results = await vector_agent.search_documents(
                query=question,
                user_id=user_id,
                course_id=course_id,
                limit=5  # Top 5 most relevant chunks
            )

            # Step 2: Build context from retrieved documents
            context_parts = []
            sources = []

            for idx, result in enumerate(search_results, 1):
                # Format: [Source 1: filename, page X] content
                source_ref = f"[Source {idx}: {result['filename']}"
                if result.get('page_number'):
                    source_ref += f", page {result['page_number']}"
                source_ref += "]"

                context_parts.append(f"{source_ref}\n{result['content']}\n")

                sources.append({
                    "document_id": result.get("document_id"),
                    "filename": result.get("filename"),
                    "page_number": result.get("page_number"),
                    "chunk_index": result.get("chunk_index"),
                    "relevance_score": result.get("relevance_score", 0.0)
                })

            # Step 3: Build conversation context
            conversation_context = ""
            if conversation_history:
                conversation_context = "\n\nPrevious conversation:\n"
                for msg in conversation_history[-5:]:  # Last 5 messages
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    conversation_context += f"{role.upper()}: {content}\n"

            # Step 4: Build the prompt
            if context_parts:
                context_text = "\n".join(context_parts)
                prompt = f"""The student is asking: "{question}"

Here are relevant excerpts from their course materials:

{context_text}
{conversation_context}

Based on this context, provide a helpful answer to the student's question.
- Cite specific sources when referencing information
- If the answer isn't fully covered in the materials, acknowledge that
- Provide clear explanations suitable for a college student
- Suggest follow-up questions if relevant

Your response:"""
            else:
                # No relevant documents found
                prompt = f"""The student is asking: "{question}"
{conversation_context}

Note: No relevant documents were found in the student's uploaded materials for this question.

Respond helpfully by:
- Acknowledging that this isn't covered in their materials
- Providing a general explanation if appropriate
- Suggesting they upload relevant course materials
- Asking if they meant something else

Your response:"""

            # Step 5: Get AI response
            response = await self.agent.run_async(prompt)

            # Step 6: Parse response and extract metadata
            answer_text = self._extract_text_from_response(response)

            # Check if answer suggests clarification is needed
            needs_clarification = self._check_needs_clarification(answer_text)

            # Generate follow-up suggestions
            follow_ups = self._generate_follow_ups(question, answer_text, search_results)

            return {
                "answer": answer_text,
                "sources": sources,
                "needs_clarification": needs_clarification,
                "follow_up_suggestions": follow_ups,
                "documents_found": len(search_results)
            }

        except Exception as e:
            print(f"Error in study assistant: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your question. Please try again.",
                "sources": [],
                "needs_clarification": False,
                "follow_up_suggestions": [],
                "documents_found": 0
            }

    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text from agent response"""
        if isinstance(response, str):
            return response
        elif hasattr(response, 'content'):
            return response.content
        elif hasattr(response, 'message'):
            return response.message
        elif isinstance(response, dict) and 'content' in response:
            return response['content']
        else:
            return str(response)

    def _check_needs_clarification(self, answer: str) -> bool:
        """Check if the answer suggests clarification is needed"""
        clarification_phrases = [
            "could you clarify",
            "what do you mean by",
            "can you be more specific",
            "which part",
            "can you elaborate",
            "not sure what you're asking"
        ]
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in clarification_phrases)

    def _generate_follow_ups(
        self,
        question: str,
        answer: str,
        search_results: List[Dict]
    ) -> List[str]:
        """Generate relevant follow-up question suggestions"""
        follow_ups = []

        # Based on search results, suggest diving deeper
        if search_results:
            # Suggest exploring related topics
            follow_ups.append("Can you explain this concept in more detail?")
            follow_ups.append("How does this relate to other topics in the course?")
            follow_ups.append("Can you give me an example of this?")
        else:
            # No context found, suggest uploading materials
            follow_ups.append("What materials should I upload to get better answers?")

        return follow_ups[:3]  # Return max 3 suggestions

    async def summarize_document(
        self,
        document_id: str,
        user_id: str,
        db
    ) -> Dict[str, Any]:
        """
        Generate a summary of a specific document.

        Args:
            document_id: Document to summarize
            user_id: User's MongoDB ID
            db: Database instance

        Returns:
            {
                "summary": str,
                "key_topics": List[str],
                "page_count": int
            }
        """
        try:
            # Fetch document chunks
            cursor = db.document_chunks.find({
                "document_id": document_id,
                "user_id": user_id  # Security: user isolation
            }).sort("chunk_index", 1).limit(10)  # First 10 chunks for summary

            chunks = []
            async for chunk in cursor:
                chunks.append(chunk.get("text", ""))

            if not chunks:
                return {
                    "summary": "No content found for this document.",
                    "key_topics": [],
                    "page_count": 0
                }

            # Build prompt for summarization
            content = "\n\n".join(chunks)
            prompt = f"""Please analyze this document excerpt and provide:

1. A concise summary (2-3 paragraphs)
2. Key topics covered (bullet points)

Document content:
{content[:3000]}  # Limit to avoid token overflow

Your analysis:"""

            response = await self.agent.run_async(prompt)
            answer = self._extract_text_from_response(response)

            # Simple parsing (could be improved with structured output)
            return {
                "summary": answer,
                "key_topics": [],  # Could extract from response
                "chunks_analyzed": len(chunks)
            }

        except Exception as e:
            print(f"Error summarizing document: {e}")
            return {
                "summary": "Error generating summary.",
                "key_topics": [],
                "chunks_analyzed": 0
            }


# Singleton instance
_study_assistant = None


def get_study_assistant() -> StudyAssistantAgent:
    """Get the study assistant instance (singleton)"""
    global _study_assistant
    if _study_assistant is None:
        _study_assistant = StudyAssistantAgent()
    return _study_assistant
