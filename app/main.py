from __future__ import annotations

import os
import re
import tempfile
from io import BytesIO
from pathlib import Path

from docx import Document
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from app.summarizer import extract_text
from app.local_model import summarize_with_sumy, model_status

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "250"))
CHUNK_CHARS = int(os.getenv("CHUNK_CHARS", "36000"))
ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt", ".md"}
LENGTHS = {"court", "moyen", "detaille"}
app = FastAPI(title="Clair — résumés locaux")


class DocxExport(BaseModel):
    filename: str
    summary: str
    pages: int | None = None
    model: str = "Sumy LSA (local)"


@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
async def health():
    return {"mode": "local", "model": "Sumy LSA", **model_status(), "max_upload_mb": MAX_UPLOAD_MB}


@app.post("/api/summarize")
async def summarize(file: UploadFile = File(...), length: str = Form("court")):
    filename = file.filename or "document"
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Formats acceptés : PDF, Word .docx, texte .txt et Markdown .md.")
    if length not in LENGTHS:
        raise HTTPException(status_code=422, detail="Longueur de résumé non reconnue.")
    data = await file.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Fichier trop volumineux (limite actuelle : {MAX_UPLOAD_MB} Mo).")
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(data)
            temp_path = Path(temp_file.name)
        text, page_count = await run_in_threadpool(extract_text, temp_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Impossible de lire ce document : {exc}")
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
    if len(text.strip()) < 100:
        raise HTTPException(status_code=422, detail="Aucun texte exploitable. Un PDF scanné nécessite une étape OCR.")
    try:
        summary, sections = await run_in_threadpool(summarize_with_sumy, text, length)
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Le moteur local n'est pas installé. Installe les dépendances indiquées dans README.md puis relance le serveur.") from exc
    source_words = len(text.split())
    summary_words = len(summary.split())
    reduction = min(99.9, max(0, round((1 - summary_words / max(source_words, 1)) * 100, 1)))
    return {"filename": filename, "pages": page_count, "characters": len(text), "words": source_words,
            "summary_words": summary_words, "reduction_percent": reduction, "chunks": sections,
            "model": "Traitement local", "summary": summary}


@app.post("/api/export/docx")
async def export_docx(payload: DocxExport):
    document = Document()
    document.core_properties.title = f"Résumé — {Path(payload.filename).stem}"
    document.add_heading("Résumé du document", level=0)
    document.add_paragraph(Path(payload.filename).name, style="Subtitle")
    details = [payload.model]
    if payload.pages:
        details.append(f"{payload.pages} pages")
    document.add_paragraph(" · ".join(details))
    for paragraph in re.split(r"\n\s*\n", payload.summary.strip()):
        if paragraph.strip():
            document.add_paragraph(paragraph.strip())
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    safe_stem = re.sub(r"[^\w-]+", "-", Path(payload.filename).stem, flags=re.UNICODE).strip("-") or "document"
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="resume-{safe_stem}.docx"'})

