import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    "Settings class which will manage the environment variables for the application."

    # Required API keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    # LLM models
    GEMINI_MODEL= "gemini-2.5-flash"
    GEMINI_FALLBACK_MODEL = ""
    GROQ_MODEL = "llama-3.3-70b-versatile"
    GROQ_FALLBACK_MODEL = ""

    # Observability settings
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

    # Threading (for database storage)
    CURRENT_THREAD_ID = "default"
    DATABASE_URL = "sqlite:///data/chatbot_memory.db"

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "ChatGPT-Agent")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

settings = Settings()