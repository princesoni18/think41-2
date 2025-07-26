
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI




# Load environment variables from .env file
load_dotenv()
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def get_gemini_response(message: str) -> str:
    try:
        system_instruction = (
            "You are a helpful AI assistant chatbot for an e-commerce site named Think41. "
            "Answer user queries about products, orders, inventory, and general support as if you are the official chatbot of Think41. "
            "Be friendly, concise, and always refer to the company as Think41."
        )
        chat = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_GEMINI_API_KEY,
            temperature=0.2,
        )
        prompt = f"{system_instruction}\nUser: {message}"
        response = chat.invoke(prompt)
        return str(response.content)
    except Exception as e:
        return f"Error: {str(e)}"
