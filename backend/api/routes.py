from fastapi import APIRouter, UploadFile, File
from rag_pipeline.document_loader import load_docs
from rag_pipeline.vectorstore import create_vector_store
from rag_pipeline.llm_response import get_answer

import os

rag_router = APIRouter()

@rag_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    import os
    upload_dir = "data_pipeline/uploads"
    os.makedirs(upload_dir, exist_ok=True)  # ✅ ensure folder exists

    save_path = os.path.join(upload_dir, file.filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    return {"message": f"Uploaded and saved {file.filename} successfully."}


# ✅ Query PDF for answers
@rag_router.get("/query")
def ask(query: str):
    docs = load_docs("data_pipeline/uploads/external-calicat-university-details.pdf")
    vector_store = create_vector_store(docs)
    answer = get_answer(vector_store, query)
    return {"answer": answer}
