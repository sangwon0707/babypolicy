from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader

from .types import ChunkInput, DocumentMetadata


def read_pdf(path: Path) -> List[str]:
    reader = PdfReader(str(path))
    pages: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        cleaned = text.replace(chr(0), " ").strip()
        pages.append(cleaned)
    return pages


def chunk_text(text: str, *, chunk_size: int = 1200, overlap: int = 200) -> Iterable[str]:
    if not text:
        return []
    tokens = text.split()
    if not tokens:
        return []

    window = chunk_size
    stride = max(chunk_size - overlap, 1)
    chunks = []
    for start in range(0, len(tokens), stride):
        end = min(start + window, len(tokens))
        chunk = " ".join(tokens[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(tokens):
            break
    return chunks


def build_chunks(path: Path, *, chunk_size: int = 1200, overlap: int = 200) -> List[ChunkInput]:
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    chunks: List[ChunkInput] = []
    pages = read_pdf(path)

    for page_index, text in enumerate(pages, start=1):
        for local_idx, chunk_text_value in enumerate(
            chunk_text(text, chunk_size=chunk_size, overlap=overlap), start=1
        ):
            chunk_id = f"{path.stem}-p{page_index}-c{local_idx}"
            metadata = DocumentMetadata(
                source=str(path),
                page=page_index,
                extra={"chunk_index": local_idx},
            )
            chunks.append(ChunkInput(id=chunk_id, text=chunk_text_value, metadata=metadata))

    return chunks
