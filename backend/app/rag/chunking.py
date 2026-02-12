"""
Text chunking module for splitting documents into smaller pieces.
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TextChunker:
    """Split text into chunks with configurable size and overlap."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]

    def chunk(self, text: str) -> List[Dict]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk

        Returns:
            List of dicts with 'content' and 'chunk_index'
        """
        if not text or not text.strip():
            return []

        chunks = self._recursive_split(text, self.separators)
        result = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                result.append({
                    "content": chunk.strip(),
                    "chunk_index": i,
                })
        return result

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators."""
        if not separators:
            return self._split_by_length(text)

        sep = separators[0]
        remaining_seps = separators[1:]

        parts = text.split(sep)

        chunks = []
        current_chunk = ""

        for part in parts:
            # If adding this part would exceed chunk size
            if len(current_chunk) + len(part) + len(sep) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    # Add overlap
                    overlap_text = current_chunk[-self.chunk_overlap:] if self.chunk_overlap else ""
                    current_chunk = overlap_text + part
                else:
                    # Part itself is too large, split further
                    if remaining_seps:
                        sub_chunks = self._recursive_split(part, remaining_seps)
                        chunks.extend(sub_chunks)
                    else:
                        chunks.extend(self._split_by_length(part))
            else:
                if current_chunk:
                    current_chunk += sep + part
                else:
                    current_chunk = part

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _split_by_length(self, text: str) -> List[str]:
        """Split text by maximum length."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap if self.chunk_overlap else end
        return chunks
