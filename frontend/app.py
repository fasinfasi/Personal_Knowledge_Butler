import streamlit as slt
import requests

slt.set_page_config(
    page_title="Personal Knowledge Butler",
    layout="wide",
)

slt.title("🧣 Personal Knowledge Butler")

uploaded_file = slt.file_uploader("Upload a PDF file", type=["pdf"])

# ✅ Upload PDF to backend
if uploaded_file:
    with slt.spinner("Uploading and processing…"):
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }
        resp = requests.post("http://localhost:8000/upload", files=files)
        if resp.status_code == 200:
            slt.success("File uploaded and stored successfully.")
        else:
            slt.error(f"Failed to upload file: {resp.status_code}")

# ✅ Ask a question with button to the left of the input field
col1, col2 = slt.columns([5, 1])  # Adjust the ratio as needed

with col1:
    query = slt.text_input("Ask a question about your knowledge base:", label_visibility="collapsed")

with col2:
    send_clicked = slt.button("Send")

if send_clicked and query:
    with slt.spinner("Searching for answers..."):
        response = requests.get(
            "http://localhost:8000/query",
            params={"query": query}
        )
        if response.status_code == 200:
            result = response.json()
            if "answer" in result:
                slt.write("### 🙌🏻 Answer:")
                slt.write(result["answer"])
            else:
                slt.warning("No answer found.")
        else:
            slt.error("Failed to retrieve answer. Check backend logs.")

