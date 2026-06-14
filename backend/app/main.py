from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
import os

app = FastAPI(
    title= "AI Compliance Assistant",
    version= "0.1.0"
 )

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    
    return {
        "filename" : file.filename,
        "characters_extracted": len(text),
        "preview": text[:500]
    }
