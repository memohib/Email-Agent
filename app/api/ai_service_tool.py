from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()
def get_llm():
    model=ChatGroq(
        model = "openai/gpt-oss-120b",
        api_key = os.getenv("GROQ_REASON_API_KEY"),
    )
    return model

def get_structured_llm():
    model=ChatGroq(
        model = "meta-llama/llama-4-maverick-17b-128e-instruct",
        api_key = os.getenv("GROQ_REASON_API_KEY"),
    )
    return model
