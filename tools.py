# Tools for agent
import math

from config import settings
from database import search_memory, save_memory
from rag import retrieve_context

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

# to load previous interactions of user
CURRENT_THREAD_ID = settings.CURRENT_THREAD_ID

def set_current_thread(thread_id: str):
    "not provided use 'default' otherwise thread_id"
    global CURRENT_THREAD_ID 
    CURRENT_THREAD_ID = thread_id


# create tools
web_search = TavilySearch( # no tool decorator because Tavily is inherientaly a tool
    max_results = 5,
    topic = "general",
    search_depth = "advanced"
)

@tool
def calculator(expression: str) -> str:
    """
    Useful for simple math calculation.
    Inputs should be a valid math experssion.
    Example: 2+2, math.sqrt(16), 10*5
    """
    try:
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum" : sum
        }

        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)

    except Exception as e:
        return f"Calculation error: {str(e)}"

@tool
def remember_this(memory: str):
    "Save am important user preference or fact into long-termm memory"
    "Use this when the user asks you to remember something"
    return save_memory(
        thread_id=CURRENT_THREAD_ID,
        memory = memory
    )

@tool
def recall_memory(query: str):
    """
    Recall saved long-term memories about the user or this conversation
    """
    return search_memory(
        thread_id=CURRENT_THREAD_ID,
        query= query
    )

@tool
def search_uploaded_documnets(query: str) -> str:
    "Search uploaded documnets for revelant information"
    "Use this when the user asks about uploaded PDFs, TXT, notes, files or documents"
    return retrieve_context(
        query = query,
        thread_id=CURRENT_THREAD_ID
    )

tools = [
    calculator,
    remember_this,
    recall_memory,
    search_uploaded_documnets,
    web_search
]