"""
Document parsing module for extracting text from various file formats.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parse documents of various formats into plain text."""

    async def parse(self, file_path: str, mime_type: Optional[str] = None) -> str:
        """
        Parse a document file and extract text content.

        Args:
            file_path: Path to the file
            mime_type: MIME type of the file

        Returns:
            Extracted text content
        """
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".pdf":
                return await self._parse_pdf(file_path)
            elif ext == ".docx":
                return await self._parse_docx(file_path)
            elif ext in (".txt", ".md"):
                return await self._parse_text(file_path)
            elif ext in (".csv",):
                return await self._parse_csv(file_path)
            elif ext in (".xls", ".xlsx"):
                return await self._parse_excel(file_path)
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return ""
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            raise

    async def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF file."""
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)

    async def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX file."""
        from docx import Document

        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    async def _parse_text(self, file_path: str) -> str:
        """Parse plain text file."""
        import aiofiles

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()

    async def _parse_csv(self, file_path: str) -> str:
        """Parse CSV file."""
        import pandas as pd

        df = pd.read_csv(file_path)
        return df.to_string()

    async def _parse_excel(self, file_path: str) -> str:
        """Parse Excel file."""
        import pandas as pd

        df = pd.read_excel(file_path)
        return df.to_string()
