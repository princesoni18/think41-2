from fastapi import FastAPI
from app.routers import chat_router

app = FastAPI()

app.include_router(chat_router.router, prefix="/think41", tags=["Chatbot"])

@app.get("/")
def root():
    return {"message": "Welcome to the Think41 Chatbot API!"}
