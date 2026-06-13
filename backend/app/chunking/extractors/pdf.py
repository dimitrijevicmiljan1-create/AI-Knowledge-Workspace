from app.chunking.extractors.base import TextExtractor


class PdfExtractor(TextExtractor):
    def extract(self, file_path: str) -> str:
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(page for page in pages if page).strip()
