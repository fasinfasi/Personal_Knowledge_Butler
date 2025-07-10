from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv
import os
from pathlib import Path

# Load token
env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)

def get_answer(vectorstore, query):
    retriever = vectorstore.as_retriever()

    # Try using a more reliable model
    llm = HuggingFaceEndpoint(
        repo_id="microsoft/DialoGPT-medium",  # Alternative model
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        temperature=0.6, 
        max_new_tokens=512
    )

    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    
    # Use invoke instead of deprecated run method
    try:
        result = qa.invoke({"query": query})
        return result["result"]
    except Exception as e:
        print(f"Error with primary model: {e}")
        # Fallback to a different approach
        return fallback_answer(vectorstore, query)

def fallback_answer(vectorstore, query):
    """Fallback method using a different model or approach"""
    try:
        # Try with a different model
        llm = HuggingFaceEndpoint(
            repo_id="google/flan-t5-small",  # Smaller, more reliable model
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            temperature=0.3,
            max_new_tokens=256
        )
        
        retriever = vectorstore.as_retriever()
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        result = qa.invoke({"query": query})
        return result["result"]
    except Exception as e:
        print(f"Fallback also failed: {e}")
        # Return a basic retrieval result
        docs = retriever.get_relevant_documents(query)
        if docs:
            return f"Based on the documents: {docs[0].page_content[:1600]}..."
        return "I couldn't find relevant information in the documents."