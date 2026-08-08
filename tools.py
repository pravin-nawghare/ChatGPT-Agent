# Tools for agent
import math

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

# create tools

web_search = TavilySearch( # no tool decorator because Tavily is inherientaly a tool
    max_results = 5,
    topic = "general",
    search_depth = "advanced"
)

def calculator(expression: str) -> str:
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