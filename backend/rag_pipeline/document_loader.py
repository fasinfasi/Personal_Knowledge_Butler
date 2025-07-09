from langchain_community.document_loaders import PyPDFLoader

def load_docs(path):
    loader = PyPDFLoader(path)
    return loader.load()