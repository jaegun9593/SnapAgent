"""
OCR module for extracting text from images in documents.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OCRService:
    """Extract text from images using Tesseract OCR."""

    def __init__(self, language: str = "eng+kor"):
        self.language = language

    async def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image file using Tesseract.

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text
        """
        try:
            import pytesseract
            from PIL import Image

            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=self.language)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {e}")
            return ""

    async def extract_text_from_pdf_images(self, pdf_path: str) -> str:
        """
        Extract text from images within a PDF using PyMuPDF + Tesseract.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text from all images
        """
        try:
            import fitz  # PyMuPDF
            import pytesseract
            from PIL import Image
            import io

            doc = fitz.open(pdf_path)
            all_text = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    image = Image.open(io.BytesIO(image_bytes))
                    text = pytesseract.image_to_string(image, lang=self.language)
                    if text.strip():
                        all_text.append(text.strip())

            doc.close()
            return "\n\n".join(all_text)
        except Exception as e:
            logger.error(f"PDF OCR extraction failed for {pdf_path}: {e}")
            return ""
