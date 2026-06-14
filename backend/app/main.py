from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
import os

app = FastAPI(
    title= "AI Compliance Assistant",
    version= "0.1.0"
 )

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


@app.get("/")
async def root():
    return {
        "Project": "AI Compliance Assistant",
        "status": "Running"
    }

@app .get("/health")
async def health_check():
    return {
        "healthy": True
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path,"wb") as f:
        f.write(await file.read())

    text = ""

    try:
        reader = PdfReader(file_path)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

    except Exception as e:
        return {"error": str(e)}

    chunks = chunk_text(text)
    
    return {
        "filename" : file.filename,
        "characters_extracted": len(text),
        "chunks_created": len(chunks),
        "preview": text[:500],
        "first_chunk": chunks[0] if chunks else ""
    }


@app.get("/documents")
async def list_documents():
    documents = []
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)

        if os.path.isfile(filepath):
            documents.append({
                "filename": filename,
                "size_bytes": os.path.getsize(filepath)
            })
    return documents