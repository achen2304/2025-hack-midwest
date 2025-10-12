# MongoDB Atlas Vector Search Setup

This guide explains how to set up vector search for CampusMind's document RAG system.

---

## Prerequisites

- MongoDB Atlas cluster (M10 or higher for vector search)
- Database: `campusmind`
- Collection: `document_chunks`
- Documents must have `embedding` field with vector data

---

## Collection Schema

The `document_chunks` collection stores vectorized document chunks with this structure:

```javascript
{
  _id: ObjectId,
  user_id: string,           // CRITICAL: User isolation
  document_id: string,        // References parent document
  course_id: string,          // Course this document belongs to
  filename: string,
  chunk_index: int,           // Position in original document
  text: string,               // The actual content
  char_count: int,
  embedding: [float],         // Vector embedding (1536 dimensions for OpenAI)
  page_number: int,          // Optional: page number
  created_at: datetime,
  metadata: object            // Additional metadata
}
```

---

## Creating the Vector Search Index

### Step 1: Access MongoDB Atlas

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Select your cluster
3. Navigate to **Search** tab
4. Click **Create Search Index**
5. Choose **JSON Editor**

### Step 2: Index Configuration

Use this JSON configuration for the vector search index:

```json
{
  "name": "vector_search_index",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1536,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "user_id"
      },
      {
        "type": "filter",
        "path": "course_id"
      }
    ]
  }
}
```

### Configuration Explanation

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `vector_search_index` | Index name used in queries |
| `type` | `vectorSearch` | Enables vector similarity search |
| `path` | `embedding` | Field containing vector embeddings |
| `numDimensions` | `1536` | OpenAI text-embedding-ada-002 dimension |
| `similarity` | `cosine` | Similarity metric (cosine/euclidean/dotProduct) |
| `filter.user_id` | - | **CRITICAL**: Enables user isolation filtering |
| `filter.course_id` | - | Optional: Filter by course |

**IMPORTANT**: The `user_id` filter is **mandatory** for security. It ensures users can only search their own documents.

### Step 3: Select Collection

- **Database**: `campusmind`
- **Collection**: `document_chunks`

### Step 4: Create Index

Click **Create Search Index** and wait for the index to build (usually 1-5 minutes).

---

## Alternative: Using Atlas CLI

You can also create the index using the Atlas CLI or MongoDB Shell:

```bash
# Install Atlas CLI
brew install mongodb-atlas-cli  # macOS
# or download from: https://www.mongodb.com/try/download/atlascli

# Login
atlas auth login

# Create vector search index
atlas clusters search indexes create \
  --clusterName YOUR_CLUSTER_NAME \
  --file vector_search_index.json
```

**vector_search_index.json:**
```json
{
  "name": "vector_search_index",
  "type": "vectorSearch",
  "collectionName": "document_chunks",
  "database": "campusmind",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1536,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "user_id"
      },
      {
        "type": "filter",
        "path": "course_id"
      }
    ]
  }
}
```

---

## Embedding Configuration

### OpenAI Embeddings (Default)

CampusMind uses OpenAI's `text-embedding-ada-002` model by default:

- **Dimensions**: 1536
- **Max input**: 8,191 tokens
- **Cost**: ~$0.0001 per 1K tokens

Add to `.env`:
```bash
OPENAI_API_KEY=sk-...
```

### Alternative: AWS Bedrock Titan Embeddings

If using AWS Bedrock instead:

```python
# Update app/util/embed.py
embedding_dimension = 1024  # Titan embeddings
```

Update index configuration:
```json
{
  "numDimensions": 1024,  // Changed from 1536
  ...
}
```

---

## Verifying the Index

### Check Index Status

In MongoDB Atlas:
1. Go to **Search** tab
2. Find `vector_search_index`
3. Status should be **Active**

### Test Vector Search

Use MongoDB Compass or Shell:

```javascript
db.document_chunks.aggregate([
  {
    $vectorSearch: {
      index: "vector_search_index",
      path: "embedding",
      queryVector: [...],  // Your query embedding
      numCandidates: 100,
      limit: 5
    }
  },
  {
    $match: {
      user_id: "user_123"  // User isolation
    }
  },
  {
    $project: {
      text: 1,
      filename: 1,
      score: { $meta: "vectorSearchScore" }
    }
  }
])
```

Expected result: Documents sorted by relevance score.

---

## Security Considerations

### 1. User Isolation (CRITICAL)

**ALWAYS** include `user_id` in the `$match` stage:

```javascript
// CORRECT ✅
{
  $match: { user_id: "current_user_id" }
}

// WRONG ❌ - DATA LEAKAGE!
{
  $match: {}  // No user filter - returns ALL users' data!
}
```

The API automatically enforces this in:
- `app/routers/documents.py` - `search_documents()`
- `app/agents/vector_agent.py` - `search_documents()`

### 2. Query Validation

All vector search queries go through:
1. **Authentication** - `verify_backend_token()`
2. **User ID extraction** - From JWT token
3. **User isolation filter** - Automatically added to `$match`

### 3. Index Permissions

The `user_id` filter in the index definition allows MongoDB to optimize queries while enforcing security.

---

## Performance Optimization

### Index Size Considerations

- Each 1536-dimension embedding: ~6KB
- 1000 chunks: ~6MB of index data
- 100,000 chunks: ~600MB of index data

### Query Performance

- `numCandidates`: Controls accuracy vs speed
  - Lower (50-100): Faster, slightly less accurate
  - Higher (200-500): Slower, more accurate
- `limit`: Number of results to return

**Recommended values:**
```python
{
  "numCandidates": 100,  # Good balance
  "limit": 5             # Top 5 results
}
```

### Monitoring

Check query performance in Atlas:
1. **Performance Advisor** - Identifies slow queries
2. **Profiler** - Shows vector search execution times
3. **Metrics** - Tracks index usage

---

## Troubleshooting

### Index Not Found

**Error**: `No index found with name: vector_search_index`

**Solution**:
1. Verify index was created in correct database/collection
2. Check index status is **Active** (not Building)
3. Ensure index name matches exactly: `vector_search_index`

### Wrong Dimensions

**Error**: `Vector size mismatch`

**Solution**:
1. Check embedding model dimensions:
   - OpenAI ada-002: 1536
   - Cohere embed-v3: 1024
   - Bedrock Titan: 1024
2. Update `numDimensions` in index configuration
3. Rebuild index

### No Results Returned

**Possible causes**:
1. **No documents in collection** - Upload some documents first
2. **Wrong user_id filter** - Check user is authenticated
3. **Embedding mismatch** - Query and documents use same model?
4. **Empty embeddings** - Check documents have valid embeddings

**Debug**:
```python
# Check if embeddings exist
count = await db.document_chunks.count_documents({
    "user_id": user_id,
    "embedding": {"$exists": True, "$ne": []}
})
print(f"Documents with embeddings: {count}")
```

### Slow Queries

**Solutions**:
1. Reduce `numCandidates` to 50-100
2. Add course_id filter to narrow search
3. Upgrade cluster tier (M10 → M20)
4. Monitor index size and rebuild if needed

---

## Required Dependencies

Install these Python packages for document processing:

```bash
pip install pymupdf              # PDF processing
pip install python-pptx          # PowerPoint processing
pip install openai               # OpenAI embeddings (if using OpenAI)
# or
pip install boto3                # AWS Bedrock (if using AWS)
```

---

## Complete Setup Checklist

- [ ] MongoDB Atlas cluster (M10+)
- [ ] Created `document_chunks` collection
- [ ] Created `vector_search_index` with user_id filter
- [ ] Index status is **Active**
- [ ] OPENAI_API_KEY or AWS credentials in .env
- [ ] Installed pymupdf and python-pptx
- [ ] Tested document upload: `POST /documents/upload`
- [ ] Tested vector search: `POST /documents/search`
- [ ] Verified user isolation (can't see other users' docs)

---

## Example: End-to-End Flow

### 1. Upload Document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@lecture_notes.pdf" \
  -F "course_id=calc_101" \
  -F "document_type=lecture_notes"
```

**Response:**
```json
{
  "id": "doc_123",
  "user_id": "user_456",
  "course_id": "calc_101",
  "filename": "lecture_notes.pdf",
  "total_chunks": 42,
  "pages": 10,
  "message": "Successfully processed 42 chunks from 10 pages"
}
```

### 2. Search Documents

```bash
curl -X POST http://localhost:8000/documents/search \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the chain rule for derivatives?",
    "course_id": "calc_101",
    "limit": 5
  }'
```

**Response:**
```json
[
  {
    "chunk_id": "chunk_789",
    "document_id": "doc_123",
    "filename": "lecture_notes.pdf",
    "course_id": "calc_101",
    "text": "The chain rule states that if y = f(g(x)), then dy/dx = f'(g(x)) * g'(x)...",
    "relevance_score": 0.89,
    "chunk_index": 15,
    "page_number": 4
  }
]
```

### 3. Use in Study Planner Agent

The vector search is automatically used by the Study Planner Agent:

```python
# In app/agents/study_planner.py
vector_agent = create_vector_agent(db, embedding_service)

# Searches only user's documents
results = await vector_agent.search_documents(
    query="derivatives",
    user_id=user_id,  # Enforces user isolation
    course_id="calc_101",
    limit=10
)

# Generate study guide from relevant materials
study_guide = await study_planner.create_study_guide(
    exam_info={"title": "Midterm", "course": "Calculus"},
    course_materials=results
)
```

---

## Additional Resources

- [MongoDB Atlas Vector Search Docs](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Vector Search Best Practices](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-best-practices/)

---

**Last Updated**: January 2025
