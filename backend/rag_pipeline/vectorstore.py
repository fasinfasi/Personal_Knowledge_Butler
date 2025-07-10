from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import shutil
import time
import tempfile
from pathlib import Path

# Use a better embedding model
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

def create_vector_store(docs, persist_dir=None):
    """Create vector store with better settings and file handling"""
    try:
        # If no persist_dir provided, use default
        if persist_dir is None:
            persist_dir = os.path.join(os.getcwd(), "chroma_db")
        
        # Convert to absolute path
        persist_dir = os.path.abspath(persist_dir)
        
        # Ensure the directory exists
        os.makedirs(persist_dir, exist_ok=True)
        
        # Remove existing database to avoid conflicts
        if os.path.exists(persist_dir):
            try:
                # Try to remove existing files
                for root, dirs, files in os.walk(persist_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                        except PermissionError:
                            pass  # Skip files that can't be removed
                
                # Remove empty directories
                for root, dirs, files in os.walk(persist_dir, topdown=False):
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            os.rmdir(dir_path)
                        except OSError:
                            pass  # Skip directories that can't be removed
                            
            except Exception as e:
                print(f"Warning: Could not fully clean existing database: {e}")
        
        # Create new vector store
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding,
            persist_directory=persist_dir
        )
        
        # Persist the database
        vectorstore.persist()
        
        return vectorstore
        
    except Exception as e:
        print(f"Error creating vector store: {e}")
        # Try creating with a temporary directory
        try:
            temp_dir = os.path.join(tempfile.gettempdir(), f"chroma_temp_{int(time.time())}")
            print(f"Trying with temporary directory: {temp_dir}")
            
            vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=embedding,
                persist_directory=temp_dir
            )
            
            vectorstore.persist()
            return vectorstore
            
        except Exception as e2:
            print(f"Even temporary directory failed: {e2}")
            return None

def load_existing_vector_store(persist_dir):
    """Load existing vector store"""
    try:
        # Convert to absolute path
        persist_dir = os.path.abspath(persist_dir)
        
        if os.path.exists(persist_dir):
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embedding
            )
            return vectorstore
        return None
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None