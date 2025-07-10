from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

def load_docs(file_path):
    """Load and process PDF documents with better chunking"""
    try:
        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Combine all pages into one text
        full_text = ""
        for doc in documents:
            full_text += doc.page_content + "\n\n"
        
        # Clean the text
        full_text = clean_text(full_text)
        
        # Split into better chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Larger chunks for better context
            chunk_overlap=100,  # Some overlap to maintain context
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
        )
        
        # Split the text
        texts = text_splitter.split_text(full_text)
        
        # Create document objects
        docs = []
        for i, text in enumerate(texts):
            # Create document with metadata
            doc = type('Document', (), {
                'page_content': text,
                'metadata': {'chunk_id': i, 'source': file_path}
            })()
            docs.append(doc)
        
        return docs
        
    except Exception as e:
        print(f"Error loading document: {e}")
        return []

def clean_text(text):
    """Clean and preprocess text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common PDF extraction issues
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between words
    text = re.sub(r'(\d+)\.(\s*[A-Z])', r'\1. \2', text)  # Fix numbered lists
    
    # Remove page numbers and headers/footers (basic cleaning)
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip very short lines that might be page numbers
        if len(line) > 10:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)