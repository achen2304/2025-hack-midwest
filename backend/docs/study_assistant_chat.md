# Study Assistant Chat - RAG-Powered Conversational Tutor

The Study Assistant Chat provides students with an AI-powered tutor that answers questions based on their uploaded course materials using Retrieval-Augmented Generation (RAG).

---

## Overview

### What is the Study Assistant?

The Study Assistant is a conversational AI agent that:

- Answers questions about course materials (PDFs, PowerPoints)
- Provides explanations with source citations
- Maintains conversation context
- Adapts to student's understanding level
- Suggests follow-up questions

### How It Works (RAG Pattern)

```
1. Student asks: "What is recursion?"
   ↓
2. System searches uploaded documents for relevant content
   ↓
3. Top 5 most relevant chunks retrieved (vector search)
   ↓
4. AI generates answer using document context
   ↓
5. Answer includes source citations (filename, page number)
   ↓
6. Student receives answer + follow-up suggestions
```

---

## Key Features

### 1. **Document-Grounded Answers**

- All answers based on student's uploaded materials
- Sources cited with filename and page numbers
- Explicitly states when information isn't in documents

### 2. **Conversation Context**

- Maintains chat history (last 10 messages)
- Understands follow-up questions
- Builds on previous exchanges

### 3. **Source Citations**

- Every answer references specific documents
- Page numbers and chunk locations provided
- Relevance scores for each source

### 4. **Smart Follow-Ups**

- AI suggests related questions
- Encourages deeper exploration
- Checks prerequisite understanding

### 5. **Document Summaries**

- Generate summaries of entire documents
- Extract key topics
- Quick overview of course materials

---

## API Endpoints

### Create Chat Session

Start a new conversation with the study assistant.

```bash
POST /chat/sessions
```

**Request Body:**

```json
{
  "course_id": "CS101", // Optional: filter documents by course
  "initial_message": "What is recursion?" // Optional: first question
}
```

**Response:**

```json
{
  "id": "session_123",
  "user_id": "user_456",
  "course_id": "CS101",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "message_count": 2 // 2 if initial_message provided, 0 otherwise
}
```

---

### Send Message

Send a question to the study assistant in an existing session.

```bash
POST /chat/sessions/{session_id}/messages
```

**Request Body:**

```json
{
  "message": "Can you explain recursion with an example?",
  "course_id": "CS101" // Optional: override session course_id
}
```

**Response:**

```json
{
  "id": "msg_789",
  "session_id": "session_123",
  "role": "assistant",
  "content": "According to [Source 1: lecture_notes.pdf, page 5]:\n\nRecursion is when a function calls itself to solve smaller instances of the same problem...",
  "sources": [
    {
      "document_id": "doc_123",
      "filename": "lecture_notes.pdf",
      "page_number": 5,
      "chunk_index": 12,
      "relevance_score": 0.89
    }
  ],
  "needs_clarification": false,
  "follow_up_suggestions": [
    "Can you explain this concept in more detail?",
    "How does this relate to other topics in the course?",
    "Can you give me an example of this?"
  ],
  "documents_found": 5,
  "timestamp": "2025-01-15T10:31:00Z"
}
```

**Key Fields:**

- `content`: The AI's answer
- `sources`: Documents referenced (with page numbers)
- `needs_clarification`: True if AI needs more context
- `follow_up_suggestions`: Related questions to ask
- `documents_found`: Number of relevant docs found

---

### Get Chat History

Retrieve full conversation history for a session.

```bash
GET /chat/sessions/{session_id}/history?limit=50
```

**Response:**

```json
{
  "session_id": "session_123",
  "course_id": "CS101",
  "messages": [
    {
      "id": "msg_001",
      "session_id": "session_123",
      "role": "user",
      "content": "What is recursion?",
      "sources": [],
      "timestamp": "2025-01-15T10:30:00Z"
    },
    {
      "id": "msg_002",
      "session_id": "session_123",
      "role": "assistant",
      "content": "According to [lecture_notes.pdf, page 5]...",
      "sources": [...],
      "timestamp": "2025-01-15T10:30:05Z"
    }
  ],
  "total_messages": 6,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

---

### List Chat Sessions

Get all chat sessions for the current user.

```bash
GET /chat/sessions?limit=20
```

**Response:**

```json
[
  {
    "id": "session_123",
    "user_id": "user_456",
    "course_id": "CS101",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:35:00Z",
    "message_count": 6
  },
  {
    "id": "session_124",
    "user_id": "user_456",
    "course_id": "MATH201",
    "created_at": "2025-01-14T14:20:00Z",
    "updated_at": "2025-01-14T14:45:00Z",
    "message_count": 12
  }
]
```

---

### Delete Chat Session

Delete a chat session and all its messages.

```bash
DELETE /chat/sessions/{session_id}
```

**Response:**

```json
{
  "success": true,
  "message": "Chat session and all messages deleted successfully"
}
```

---

### Summarize Document

Generate an AI summary of a specific document.

```bash
POST /chat/documents/summarize
```

**Request Body:**

```json
{
  "document_id": "doc_123"
}
```

**Response:**

```json
{
  "document_id": "doc_123",
  "filename": "lecture_notes.pdf",
  "summary": "This document covers fundamental concepts of recursion in computer science...",
  "key_topics": ["Recursion", "Base Cases", "Recursive Cases", "Call Stack"],
  "chunks_analyzed": 10
}
```

---

## Usage Examples

### Example 1: Start a Conversation

```bash
curl -X POST http://localhost:8000/chat/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "CS101",
    "initial_message": "What are the key topics in this course?"
  }'
```

**Expected Response:**

```json
{
  "id": "65abc123def456...",
  "user_id": "user_789",
  "course_id": "CS101",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:05Z",
  "message_count": 2
}
```

---

### Example 2: Ask Follow-Up Questions

```bash
curl -X POST http://localhost:8000/chat/sessions/65abc123def456.../messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you explain recursion in more detail?"
  }'
```

**Expected Response:**

```json
{
  "id": "msg_xyz789",
  "session_id": "65abc123def456...",
  "role": "assistant",
  "content": "According to [Source 1: lecture_notes.pdf, page 5]:\n\nRecursion is a programming technique where...",
  "sources": [
    {
      "document_id": "doc_abc",
      "filename": "lecture_notes.pdf",
      "page_number": 5,
      "relevance_score": 0.92
    }
  ],
  "follow_up_suggestions": [
    "Can you give me an example of recursion?",
    "What are the base case and recursive case?"
  ],
  "documents_found": 3
}
```

---

### Example 3: Get Conversation History

```bash
curl http://localhost:8000/chat/sessions/65abc123def456.../history \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## How RAG Works

### Step-by-Step Process

#### 1. **Query Processing**

```python
# User asks a question
question = "What is the chain rule in calculus?"
```

#### 2. **Document Retrieval (Vector Search)**

```python
# System generates embedding for query
query_embedding = embedding_service.generate_embedding(question)

# Searches user's documents using MongoDB vector search
results = vector_agent.search_documents(
    query=question,
    user_id=user_id,  # CRITICAL: User isolation
    course_id="MATH201",
    limit=5  # Top 5 most relevant chunks
)
```

#### 3. **Context Building**

```python
# System builds context from retrieved documents
context = """
[Source 1: calculus_notes.pdf, page 12]
The chain rule is used when differentiating composite functions...

[Source 2: lecture_slides.pptx, slide 8]
Chain rule formula: d/dx[f(g(x))] = f'(g(x)) * g'(x)
"""
```

#### 4. **AI Response Generation**

```python
# AI uses context to generate informed answer
prompt = f"""Student question: {question}

Relevant course materials:
{context}

Provide a clear answer based on these materials, citing sources."""

response = agent.run_async(prompt)
```

#### 5. **Answer Delivery**

```python
# System returns answer with source citations
{
  "answer": "According to [calculus_notes.pdf, page 12]...",
  "sources": [...],
  "follow_up_suggestions": [...]
}
```

---

## MongoDB Collections

### `chat_sessions`

Stores chat sessions.

```javascript
{
  _id: ObjectId,
  user_id: string,           // User who owns this session
  course_id: string,          // Optional course context
  created_at: datetime,
  updated_at: datetime,
  message_count: int,
  is_active: bool
}
```

**Indexes:**

```javascript
db.chat_sessions.createIndex({ user_id: 1, updated_at: -1 });
```

---

### `chat_messages`

Stores individual messages in chat sessions.

```javascript
{
  _id: ObjectId,
  session_id: string,         // References chat session
  role: string,               // "user" | "assistant" | "system"
  content: string,            // Message text
  sources: [                  // Sources cited (only for assistant messages)
    {
      document_id: string,
      filename: string,
      page_number: int,
      chunk_index: int,
      relevance_score: float
    }
  ],
  needs_clarification: bool,  // Whether assistant needs more info
  follow_up_suggestions: [string],
  documents_found: int,
  timestamp: datetime
}
```

**Indexes:**

```javascript
db.chat_messages.createIndex({ session_id: 1, timestamp: 1 });
```

---

## Security

### User Isolation

**CRITICAL**: All queries filter by `user_id` to prevent data leakage.

```python
# CORRECT ✅
# Vector search always filters by user_id
results = vector_agent.search_documents(
    query=question,
    user_id=user_id,  # User can ONLY search their own documents
    limit=5
)

# WRONG ❌ - Would expose other users' documents
results = vector_agent.search_documents(
    query=question,
    limit=5  # NO user_id filter - security vulnerability!
)
```

### Chat Session Verification

```python
# Verify session belongs to user before allowing access
session = await db.chat_sessions.find_one({
    "_id": ObjectId(session_id),
    "user_id": db_user_id  # Security check
})

if not session:
    raise HTTPException(404, "Chat session not found")
```

---

## Integration with Other Features

### 1. **Study Guides**

Students can ask the assistant to explain topics from their study guides:

```json
{
  "message": "Can you help me understand topic 3 from my study guide?"
}
```

The assistant will:

- Search relevant documents
- Provide explanations with citations
- Suggest practice problems

### 2. **Document Upload Flow**

```
1. Student uploads lecture notes
   ↓
2. Document processed and vectorized
   ↓
3. Student starts chat session
   ↓
4. Student asks: "What are the key concepts?"
   ↓
5. Assistant searches lecture notes and responds
```

### 3. **Wellness Integration**

If a student reports feeling stressed in a health check-in, they can:

- Use the chat to get quick help
- Ask targeted questions before exams
- Get explanations without scheduling office hours

---

## Best Practices

### For Students

1. **Upload Materials First**

   - Upload all relevant PDFs and PowerPoints before chatting
   - More documents = better answers

2. **Be Specific**

   - ❌ "Tell me about this"
   - ✅ "What is the chain rule and how do I apply it?"

3. **Use Course Context**

   - Specify course_id to filter relevant documents
   - Creates focused conversations

4. **Follow Suggestions**
   - AI suggests relevant follow-up questions
   - Help deepen understanding

### For Developers

1. **Always Use User Isolation**

   ```python
   # Every vector search MUST include user_id
   results = vector_agent.search_documents(
       query=query,
       user_id=user_id,  # REQUIRED
       course_id=course_id
   )
   ```

2. **Limit Conversation History**

   ```python
   # Use last 10 messages for context (token efficiency)
   conversation_history = messages[-10:]
   ```

3. **Handle Empty Results**
   ```python
   if not search_results:
       # Tell user no relevant documents found
       # Suggest uploading materials
   ```

---

## Performance Considerations

### Response Times

- **Vector Search**: ~100-300ms
- **AI Response Generation**: ~2-5 seconds
- **Total Response Time**: ~2-6 seconds

### Optimization Tips

1. **Cache Embeddings**: Don't regenerate embeddings for same query
2. **Limit Context**: Use top 5 chunks (balance accuracy vs speed)
3. **Async Operations**: All database and AI calls are async
4. **Index Performance**: Ensure MongoDB indexes exist

---

## Troubleshooting

### Issue: "No relevant documents found"

**Causes:**

- User hasn't uploaded any documents
- Query doesn't match document content
- Wrong course_id filter

**Solutions:**

1. Check if user has uploaded documents
2. Try broader queries
3. Remove course_id filter for cross-course search

---

### Issue: AI says "I don't have information about this"

**Causes:**

- Topic not covered in uploaded materials
- Vector search returned low-relevance results

**Solutions:**

1. Ask user to upload relevant materials
2. Adjust similarity threshold in vector search
3. Try rephrasing the question

---

### Issue: Slow response times

**Causes:**

- Large number of document chunks to search
- Slow embedding generation
- MongoDB cluster performance

**Solutions:**

1. Reduce `limit` in vector search (default: 5)
2. Check MongoDB Atlas performance metrics
3. Optimize embedding service (batch requests)

---

## Example Frontend Integration

### React Component Example

```typescript
// ChatInterface.tsx
const ChatInterface = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');

  // Create session on mount
  useEffect(() => {
    createChatSession({
      course_id: 'CS101',
      initial_message: 'What topics are covered in this course?',
    }).then((session) => {
      setSessionId(session.id);
      // Fetch initial response
      fetchChatHistory(session.id);
    });
  }, []);

  // Send message
  const sendMessage = async () => {
    const response = await fetch(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ message: input }),
    });
    const data = await response.json();
    setMessages([...messages, data]);
    setInput('');
  };

  return (
    <div className="chat-interface">
      <div className="messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.sources.length > 0 && (
              <div className="sources">
                Sources:{' '}
                {msg.sources
                  .map((s) => `${s.filename} (p.${s.page_number})`)
                  .join(', ')}
              </div>
            )}
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
    </div>
  );
};
```

---

## Future Enhancements

### Potential Features

1. **Multi-Turn Reasoning**

   - Break complex questions into steps
   - Ask clarifying questions

2. **Practice Problem Generation**

   - Generate practice questions from materials
   - Check student answers

3. **Concept Mapping**

   - Visualize relationships between topics
   - Show prerequisites

4. **Voice Interface**

   - Speech-to-text for questions
   - Text-to-speech for answers

5. **Collaborative Study**
   - Group chat sessions
   - Shared document pools

---

## Implementation Details

### Agent Architecture

The Study Assistant is implemented using the AWS Strands SDK, which provides:

1. **Managed AI Infrastructure**: Handles token management, rate limiting, and model selection
2. **Context Management**: Efficiently manages conversation history
3. **Prompt Engineering**: Optimized prompts for academic assistance

The core implementation is in `app/agents/study_assistant.py`, which:

- Creates an agent with academic-focused system prompt
- Implements RAG pattern with document retrieval
- Formats responses with source citations
- Generates follow-up suggestions

### Key Methods

```python
# Main method for answering questions
async def answer_question(
    self,
    question: str,
    user_id: str,
    course_id: Optional[str],
    conversation_history: List[Dict[str, Any]],
    vector_agent,
    db
) -> Dict[str, Any]

# Document summarization
async def summarize_document(
    self,
    document_id: str,
    user_id: str,
    db
) -> Dict[str, Any]
```

### API Routes

The API routes in `app/routers/chat.py` handle:

- Session management
- Message processing
- History retrieval
- Document summarization

All routes enforce user isolation and proper authentication.

---

## Summary

The Study Assistant Chat provides:

- ✅ RAG-powered answers grounded in student's materials
- ✅ Source citations with page numbers
- ✅ Conversation context and follow-ups
- ✅ User-isolated security
- ✅ MongoDB-based conversation storage
- ✅ Integration with document upload system

Perfect for:

- Quick study help before exams
- Understanding complex topics
- Exploring course materials efficiently
- Getting personalized explanations

---

**Last Updated**: October 2025
