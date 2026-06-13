from app.chunking.extractors.base import TextExtractor


class DocxExtractor(TextExtractor):
    def extract(self, file_path: str) -> str:
        from docx import Document as DocxDocument

        document = DocxDocument(file_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs).strip()
