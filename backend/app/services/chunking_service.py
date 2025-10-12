"""
Chunking Service - Smart text splitting for better embeddings and retrieval
"""
from typing import List, Dict, Any, Optional
import re


class ChunkingService:
    """
    Splits text into optimal chunks for embeddings and vector search.

    Strategies:
    - Fixed size chunking with overlap
    - Sentence-based chunking
    - Paragraph-based chunking
    - Semantic chunking (for future enhancement)
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separator: str = "\n\n"
    ):
        """
        Initialize chunking service.

        Args:
            chunk_size: Target size of each chunk (in tokens/characters)
            chunk_overlap: Number of characters to overlap between chunks
            separator: Primary separator for splitting (default: paragraphs)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator

    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        strategy: str = "recursive"
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            strategy: "recursive", "fixed", "sentences", or "paragraphs"

        Returns:
            List of chunks with metadata:
            [
                {
                    "text": "chunk content",
                    "chunk_index": 0,
                    "start_char": 0,
                    "end_char": 512,
                    "metadata": {...}
                }
            ]
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}

        if strategy == "recursive":
            chunks = self._recursive_split(text)
        elif strategy == "fixed":
            chunks = self._fixed_size_split(text)
        elif strategy == "sentences":
            chunks = self._sentence_split(text)
        elif strategy == "paragraphs":
            chunks = self._paragraph_split(text)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        # Add metadata and position info
        result = []
        current_pos = 0

        for idx, chunk_text in enumerate(chunks):
            # Find position in original text
            start_pos = text.find(chunk_text, current_pos)
            if start_pos == -1:
                start_pos = current_pos

            end_pos = start_pos + len(chunk_text)
            current_pos = end_pos

            result.append({
                "text": chunk_text.strip(),
                "chunk_index": idx,
                "start_char": start_pos,
                "end_char": end_pos,
                "char_count": len(chunk_text.strip()),
                "metadata": {**metadata}
            })

        return result

    def _recursive_split(self, text: str) -> List[str]:
        """
        Recursively split text using multiple separators.
        Best for general-purpose chunking.
        """
        # Try splitting by paragraphs first
        separators = ["\n\n", "\n", ". ", " ", ""]

        return self._split_with_separators(text, separators)

    def _split_with_separators(
        self,
        text: str,
        separators: List[str]
    ) -> List[str]:
        """Split text using a hierarchy of separators"""
        if not separators:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            # Last resort: split by character
            return self._fixed_size_split(text)

        splits = text.split(separator)
        chunks = []
        current_chunk = ""

        for split in splits:
            if len(current_chunk) + len(split) + len(separator) < self.chunk_size:
                current_chunk += split + separator
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # If split is too large, recursively split it
                if len(split) > self.chunk_size:
                    sub_chunks = self._split_with_separators(split, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = split + separator

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _fixed_size_split(self, text: str) -> List[str]:
        """Split text into fixed-size chunks with overlap"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def _sentence_split(self, text: str) -> List[str]:
        """Split text by sentences, grouping into chunks"""
        # Simple sentence splitting (can be improved with NLTK)
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_endings.split(text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _paragraph_split(self, text: str) -> List[str]:
        """Split text by paragraphs, grouping into chunks"""
        paragraphs = text.split("\n\n")

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # If paragraph is too large, split it further
                if len(para) > self.chunk_size:
                    sub_chunks = self._fixed_size_split(para)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_documents(
        self,
        documents: List[Dict[str, Any]],
        text_key: str = "text",
        metadata_key: str = "metadata"
    ) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents at once.

        Args:
            documents: List of documents with text and metadata
            text_key: Key for text content in each document
            metadata_key: Key for metadata in each document

        Returns:
            Flattened list of chunks from all documents
        """
        all_chunks = []

        for doc_idx, doc in enumerate(documents):
            text = doc.get(text_key, "")
            metadata = doc.get(metadata_key, {})

            # Add document index to metadata
            doc_metadata = {
                **metadata,
                "document_index": doc_idx
            }

            chunks = self.chunk_text(text, doc_metadata)
            all_chunks.extend(chunks)

        return all_chunks


# Singleton instance
_chunking_service = None


def get_chunking_service(
    chunk_size: int = 512,
    chunk_overlap: int = 50
) -> ChunkingService:
    """Get the chunking service instance"""
    global _chunking_service
    if _chunking_service is None:
        _chunking_service = ChunkingService(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    return _chunking_service
