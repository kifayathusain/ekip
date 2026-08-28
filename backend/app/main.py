from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import Base, engine, get_db
from app.models.models import Chunk, Document
from app.services.ai_service import embed, generate_answer
from app.services.document_service import chunk_text, extract_text

app = FastAPI(title="Enterprise Knowledge Intelligence Platform", version="0.1.0")


@app.on_event("startup")
def initialize_database() -> None:
    """Enable pgvector and create the local MVP database schema."""
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ekip-api"}


@app.post("/api/v1/documents")
async def upload_document(
    file: UploadFile = File(...), database: Session = Depends(get_db)
) -> dict[str, int | str]:
    """Store an uploaded document and index its text chunks."""
    file_contents = await file.read()
    filename = file.filename or "document.txt"

    try:
        pages = extract_text(filename, file_contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    content = "\n".join(page_text for page_text, _ in pages)
    document = Document(name=filename, content=content)
    database.add(document)
    database.flush()

    for page_text, page_number in pages:
        for text_chunk in chunk_text(page_text):
            database.add(
                Chunk(
                    document_id=document.id,
                    content=text_chunk,
                    page_number=page_number,
                    embedding=embed(text_chunk),
                )
            )

    database.commit()
    return {"id": document.id, "name": document.name, "status": "ready"}


@app.get("/api/v1/documents")
def list_documents(database: Session = Depends(get_db)) -> list[dict[str, object]]:
    documents = database.query(Document).order_by(Document.id.desc()).all()
    return [
        {"id": document.id, "name": document.name, "created_at": document.created_at}
        for document in documents
    ]


@app.post("/api/v1/search")
def search(payload: dict[str, object], database: Session = Depends(get_db)) -> list[dict[str, object]]:
    raw_query = payload.get("query", "")
    if not isinstance(raw_query, str) or not (query := raw_query.strip()):
        raise HTTPException(status_code=400, detail="query is required")

    top_k = payload.get("top_k", 5)
    if not isinstance(top_k, int) or top_k < 1:
        raise HTTPException(status_code=400, detail="top_k must be a positive integer")

    query_embedding = embed(query)
    chunks = (
        database.query(Chunk)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )
    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "content": chunk.content,
            "page_number": chunk.page_number,
        }
        for chunk in chunks
    ]


@app.post("/api/v1/chat")
def chat(payload: dict[str, object], database: Session = Depends(get_db)) -> dict[str, object]:
    raw_question = payload.get("question", "")
    if not isinstance(raw_question, str) or not (question := raw_question.strip()):
        raise HTTPException(status_code=400, detail="question is required")

    question_embedding = embed(question)
    chunks = (
        database.query(Chunk)
        .order_by(Chunk.embedding.cosine_distance(question_embedding))
        .limit(5)
        .all()
    )
    contexts = [
        {
            "content": chunk.content,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
        }
        for chunk in chunks
    ]
    answer = generate_answer(question, contexts)
    citations = [
        {"document_id": context["document_id"], "page_number": context["page_number"]}
        for context in contexts
    ]
    return {"answer": answer, "citations": citations}
