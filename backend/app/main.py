from app.services.load_csv_to_mongo import load_csv_to_mongo
from fastapi import FastAPI
from app.routers import chat_router


app = FastAPI()
# # Load CSV data into MongoDB on startup
# @app.on_event("startup")
# def startup_event():
#     load_csv_to_mongo()

app.include_router(chat_router.router, prefix="/api", tags=["Chatbot"])

@app.get("/")
def root():
    return {"message": "Welcome to the Think41 Chatbot API!"}
