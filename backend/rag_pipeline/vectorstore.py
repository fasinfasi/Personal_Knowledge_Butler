from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def create_vector_store(docs, persist_dir="./chroma_db"):
    return Chroma.from_documents(docs, embedding, persist_directory=persist_dir)
