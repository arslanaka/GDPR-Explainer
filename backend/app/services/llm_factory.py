import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature=0, provider=None):
    # If provider is not specified, check env, default to openai
    if not provider:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "gemini":
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            print("Warning: GOOGLE_API_KEY not found. Falling back to OpenAI or failing.")
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=temperature, google_api_key=google_api_key)
    
    # Default to OpenAI
    return ChatOpenAI(model="gpt-4-turbo-preview", temperature=temperature)
