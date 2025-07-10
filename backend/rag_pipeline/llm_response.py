from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from pathlib import Path
import re

# Load token
env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)

def get_answer(vectorstore, query):
    """Get answer using retrieval and LLM"""
    try:
        # Get relevant documents with better search
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        relevant_docs = retriever.get_relevant_documents(query)
        
        if not relevant_docs:
            return "I couldn't find any relevant information in the documents."
        
        # Try with a working model first
        try:
            return get_answer_with_llm(relevant_docs, query)
        except Exception as e:
            print(f"LLM failed: {e}")
            return get_answer_with_context(relevant_docs, query)
            
    except Exception as e:
        print(f"Error in get_answer: {e}")
        return "I encountered an error while processing your query."

def get_answer_with_llm(relevant_docs, query):
    """Try to get answer using LLM"""
    try:
        # Use a simpler, more reliable model
        llm = HuggingFaceEndpoint(
            repo_id="google/flan-t5-large",
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            temperature=0.2,
            max_new_tokens=200,
            timeout=60
        )
        
        # Create context from relevant documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Create a simple prompt
        prompt = f"""Based on the following context, answer the question. Be concise and accurate.

Context:
{context}

Question: {query}

Answer:"""
        
        # Get response from LLM
        response = llm.invoke(prompt)
        
        if response and len(response.strip()) > 10:
            return response.strip()
        else:
            # If LLM response is too short, fall back to context
            return get_answer_with_context(relevant_docs, query)
            
    except Exception as e:
        print(f"LLM error: {e}")
        raise e

def get_answer_with_context(relevant_docs, query):
    """Fallback method using smart context extraction"""
    try:
        query_lower = query.lower()
        query_terms = [term.strip() for term in query_lower.split() if len(term.strip()) > 2]
        
        # Find the most relevant content
        best_content = ""
        best_score = 0
        
        for doc in relevant_docs:
            content = doc.page_content
            content_lower = content.lower()
            
            # Score based on query terms
            score = 0
            for term in query_terms:
                if term in content_lower:
                    score += content_lower.count(term)
            
            if score > best_score:
                best_score = score
                best_content = content
        
        if best_content:
            # Try to extract the most relevant paragraph/section
            answer = extract_relevant_section(best_content, query_terms)
            return f"Based on the document:\n\n{answer}"
        else:
            # Return first document if no good match
            return f"Based on the document:\n\n{relevant_docs[0].page_content[:500]}..."
            
    except Exception as e:
        print(f"Context extraction error: {e}")
        return "I found relevant information but couldn't extract a clear answer."

def extract_relevant_section(content, query_terms):
    """Extract the most relevant section from content"""
    try:
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Find sentences that contain query terms
        relevant_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Skip very short sentences
                sentence_lower = sentence.lower()
                if any(term in sentence_lower for term in query_terms):
                    relevant_sentences.append(sentence)
        
        if relevant_sentences:
            # Return first few relevant sentences
            return '. '.join(relevant_sentences[:3]) + '.'
        else:
            # If no specific sentences found, return first part
            return content[:400] + '...'
            
    except Exception as e:
        print(f"Section extraction error: {e}")
        return content[:400] + '...'