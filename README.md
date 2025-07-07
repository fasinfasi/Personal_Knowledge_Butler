# Personal Knowledge Butler
Chat app that answers your questions using your own PDFs, notes, e‑mails, Jira tickets, etc

### User flow may like this:
# System Architecture

## 🖥️ UI
1. **Upload Docs**  
   Supported formats: `.pdf`, `.txt`, `.md`, `.eml`

2. **Ask a Question**  
   Interaction via chat box

3. **See Answer + Citations**  
   Response includes answer and document references

➡️ Communication via **REST** or **SSE**

---

## 🚀 FastAPI Backend
- **Auth** – Handles user authentication
- **Ingest** – Processes and chunks uploaded documents
- **Chat** – Interfaces with the LLM for responses
- **Search** – Queries the vector database

---

## 📦 Vector Database (Chroma / LanceDB)
- Stores:  
  `{ chunk, embedding, metadata }`
- Retrieves:  
  **k-nearest** documents for a given query

---

## 🧠 LLM (Gemma 2‑9B or LLaMA 3‑8B)
- **Prompt = user input + retrieved chunks**
- Fine-tuned with **LoRA adapters** via **QLoRA**

