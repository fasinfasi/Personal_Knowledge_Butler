from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub

def get_answer(vectorstore, query):
    retriever = vectorstore.as_retriever()
    llm = HuggingFaceHub(repo_id="google/flan-t5-base", model_kwargs={"temperature": 0.5})
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa.run(query)