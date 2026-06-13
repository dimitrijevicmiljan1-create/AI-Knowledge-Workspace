from pathlib import Path

from app.chunking.extractors.base import TextExtractor
from app.chunking.extractors.docx import DocxExtractor
from app.chunking.extractors.markdown import MarkdownExtractor
from app.chunking.extractors.pdf import PdfExtractor
from app.chunking.extractors.txt import TxtExtractor

_EXTRACTORS: dict[str, TextExtractor] = {
    ".txt": TxtExtractor(),
    ".md": MarkdownExtractor(),
    ".pdf": PdfExtractor(),
    ".docx": DocxExtractor(),
}


def extract_text_from_file(file_path: str, extension: str | None = None) -> str:
    normalized_extension = (extension or Path(file_path).suffix).lower()
    extractor = _EXTRACTORS.get(normalized_extension)
    if extractor is None:
        raise ValueError(f"Unsupported file type for text extraction: {normalized_extension or 'unknown'}")
    text = extractor.extract(file_path)
    if not text.strip():
        raise ValueError("No extractable text found in file")
    return text
