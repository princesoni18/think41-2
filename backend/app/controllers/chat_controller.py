
import os

import google.generativeai as genai


# Load environment variables from .env file

GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key="AIzaSyBAI1mSy91uLfZOf6N-5S3yPJSh54HE42Q")

def get_gemini_response(message: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        system_instruction = (
            "You are a helpful AI assistant chatbot for an e-commerce site named Think41. "
            "Answer user queries about products, orders, inventory, and general support as if you are the official chatbot of Think41. "
            "Be friendly, concise, and always refer to the company as Think41."
        )
        prompt = f"{system_instruction}\nUser: {message}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
