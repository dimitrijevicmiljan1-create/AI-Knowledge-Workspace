from app.chunking.extractors.txt import TxtExtractor


class MarkdownExtractor(TxtExtractor):
    def extract(self, file_path: str) -> str:
        return super().extract(file_path).strip()
