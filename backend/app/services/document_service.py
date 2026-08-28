from io import BytesIO
from pathlib import Path

import fitz
from docx import Document as DocxDocument


def extract_text(filename: str, data: bytes) -> list[tuple[str, int | None]]:
    """Extract non-empty text from a supported document format."""
    extension = Path(filename).suffix.lower()
    if extension == ".pdf":
        pdf = fitz.open(stream=data, filetype="pdf")
        return [
            (page_text, page_number)
            for page_number, page in enumerate(pdf, start=1)
            if (page_text := page.get_text()).strip()
        ]
    if extension == ".docx":
        document = DocxDocument(BytesIO(data))
        return [("\n".join(paragraph.text for paragraph in document.paragraphs), None)]
    if extension in {".txt", ".md"}:
        return [(data.decode("utf-8", errors="replace"), None)]
    raise ValueError("Supported formats: PDF, DOCX, TXT, MD")


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    """Split normalized text into overlapping chunks for retrieval."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = " ".join(text.split())
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks
