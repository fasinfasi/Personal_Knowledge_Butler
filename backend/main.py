from fastapi import FastAPI
from api.routes import rag_router

app = FastAPI()
app.include_router(rag_router)