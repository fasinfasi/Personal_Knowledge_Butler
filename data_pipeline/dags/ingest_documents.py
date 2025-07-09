from airflow import DAG
from airflow.operators import PythonOperator
from datetime import datetime
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma


UPLOAD_DIR = "data_pipeline/uploads"
VECTOR_DIR = "data_pipeline/vector_store"

def ingest_documents():
    all_docs = []

    #Load pdf and text files
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath)
        else:
            continue

        docs = loader.load()
        all_docs.extend(docs)

    # Chunk documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(all_docs)

    # Embed and store to chroma
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding_model=embedding_model,
        persist_directory=VECTOR_DIR
    )
    vectorstore.persist()
    print(f"Ingested {len(chunks)} chunks into vector store.")

    default_args = {
        'start_date': datetime(2025, 1, 1)
    }

    with DAG("ingest_documents",
             schedule_interval=None,
             catchup=False,
             default_args=default_args, tags=["butler"]) as dag:
        ingest_task = PythonOperator(
            task_id="ingest_docs",
            python_callable=ingest_documents
    )
        