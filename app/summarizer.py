from __future__ import annotations

import re
from pathlib import Path


def split_text(text: str, max_chars: int) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        while len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            cut = paragraph.rfind(" ", 0, max_chars)
            cut = cut if cut >= max_chars // 2 else max_chars
            chunks.append(paragraph[:cut].strip())
            paragraph = paragraph[cut:].strip()
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = ""
        current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(current)
    return chunks


def extract_text(path: str | Path) -> tuple[str, int | None]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = []
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = (page.extract_text() or "").strip()
                if page_text:
                    pages.append(page_text)
                page.close()
        return "\n\n".join(pages), page_count
    if suffix == ".docx":
        from docx import Document
        doc = Document(path)
        blocks = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                blocks.append(" | ".join(cell.text.strip() for cell in row.cells))
        return "\n\n".join(blocks), None
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace"), None
    raise ValueError("Format non pris en charge.")
