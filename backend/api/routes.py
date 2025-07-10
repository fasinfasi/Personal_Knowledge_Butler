from fastapi import APIRouter, UploadFile, File, HTTPException
from rag_pipeline.document_loader import load_docs
from rag_pipeline.vectorstore import create_vector_store, load_existing_vector_store
from rag_pipeline.llm_response import get_answer
import os
import hashlib
import time

rag_router = APIRouter()

# Use absolute paths based on current working directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "data_pipeline", "uploads")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "..", "data_pipeline", "vector_db")
LATEST_FILE_PATH = os.path.join(BASE_DIR, "..", "data_pipeline", "uploads", "latest.txt")

@rag_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Create directories with absolute paths
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)
        
        # Save the uploaded file
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Create a unique directory name using timestamp and filename
        timestamp = str(int(time.time()))
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        vector_dir_name = f"{safe_filename}_{timestamp}"
        vector_dir = os.path.join(VECTOR_DB_DIR, vector_dir_name)
        
        # Save file info
        with open(LATEST_FILE_PATH, "w") as f:
            f.write(f"{file.filename}|{vector_dir_name}")
        
        # Process the document
        print(f"Loading document: {file.filename}")
        docs = load_docs(save_path)
        
        if not docs:
            raise HTTPException(status_code=400, detail="Failed to process the document")
        
        print(f"Creating vector store with {len(docs)} chunks")
        vector_store = create_vector_store(docs, vector_dir)
        
        if not vector_store:
            raise HTTPException(status_code=500, detail="Failed to create vector store")
        
        return {
            "message": f"Successfully uploaded and processed {file.filename}",
            "chunks_created": len(docs),
            "vector_store_path": vector_dir
        }
        
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@rag_router.get("/query")
def ask(query: str):
    try:
        # Read latest uploaded file info
        if not os.path.exists(LATEST_FILE_PATH):
            return {"answer": "No document has been uploaded yet. Please upload a PDF first."}
        
        with open(LATEST_FILE_PATH, "r") as f:
            file_info = f.read().strip().split("|")
            if len(file_info) != 2:
                return {"answer": "Invalid file information. Please re-upload your document."}
            
            filename, vector_dir_name = file_info
        
        # Load the vector store
        vector_dir = os.path.join(VECTOR_DB_DIR, vector_dir_name)
        
        if not os.path.exists(vector_dir):
            return {"answer": "Vector store not found. Please re-upload your document."}
        
        vector_store = load_existing_vector_store(vector_dir)
        
        if not vector_store:
            return {"answer": "Failed to load vector store. Please re-upload your document."}
        
        # Get the answer
        print(f"Processing query: {query}")
        answer = get_answer(vector_store, query)
        
        return {"answer": answer}
        
    except Exception as e:
        print(f"Query error: {e}")
        return {"answer": f"I encountered an error while processing your query: {str(e)}"}

@rag_router.get("/health")
def health_check():
    return {"status": "healthy"}

@rag_router.get("/")
def root():
    return {"message": "Personal Knowledge Butler API is running!"}