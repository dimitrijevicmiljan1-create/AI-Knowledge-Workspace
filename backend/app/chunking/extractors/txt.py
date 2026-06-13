from app.chunking.extractors.base import TextExtractor


class TxtExtractor(TextExtractor):
    def extract(self, file_path: str) -> str:
        with open(file_path, encoding="utf-8") as handle:
            return handle.read()
