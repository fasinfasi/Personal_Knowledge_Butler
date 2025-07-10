from fastapi import APIRouter, UploadFile, File
from rag_pipeline.document_loader import load_docs
from rag_pipeline.vectorstore import create_vector_store
from rag_pipeline.llm_response import get_answer

import os

rag_router = APIRouter()

LATEST_FILE_PATH = "data_pipeline/uploads/latest.txt"

@rag_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = "data_pipeline/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    save_path = os.path.join(upload_dir, file.filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # ✅ Save the filename for later queries
    with open(LATEST_FILE_PATH, "w") as f:
        f.write(file.filename)

    return {"message": f"Uploaded and saved {file.filename} successfully."}


@rag_router.get("/query")
def ask(query: str):
    # ✅ Read latest uploaded file name
    try:
        with open(LATEST_FILE_PATH, "r") as f:
            latest_filename = f.read().strip()
    except FileNotFoundError:
        return {"answer": "No document has been uploaded yet."}

    file_path = f"data_pipeline/uploads/{latest_filename}"

    if not os.path.exists(file_path):
        return {"answer": "Uploaded document not found. Please re-upload."}

    docs = load_docs(file_path)
    vector_store = create_vector_store(docs)
    answer = get_answer(vector_store, query)
    return {"answer": answer}
