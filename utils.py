# add all helper functionality
from config import settings
from pathlib import Path
from pypdf import PdfReader
import docx2txt
import json
from langchain_core.messages import ToolMessage,AIMessage, AIMessageChunk
print("inside utils.py file\n")
# Default model for app
DEFAULT_MODEL = settings.GEMINI_MODEL if settings.GEMINI_MODEL else "gemini-2.5-pro"
print("default llm model set\n")
# Define list of models to show to user:
ALLOWED_MODELS = {
    "gemini-2.5-flash",
    "gemini-3.0-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-3.0-pro",
}

# Normalialize the model name to match the name according to docs
def normalize_model_name(model_name: str | None) -> str:
    """
    Validate selected model name from frontend.
    If model name is missing or not matching to required name, fallback to default model
    """
    print("inside normalize_model_name method\n")
    if not model_name:
        return DEFAULT_MODEL

    model_name = model_name.strip()
    print("model initialize\n")
    if model_name not in ALLOWED_MODELS:
        return DEFAULT_MODEL

    return model_name

def read_files_text(file_path: str) -> str:
    """
    This function reads the user uploaded files.
    Currently only supports '.pdf' and '.txt' file format properly
    """
    print("inside read_files_text method\n")
    path = Path(file_path)
    suffix = path.suffix.lower()
    print("reading path and suffix\n")
    if suffix == ".pdf":
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""
            text += "\n"

        return text
    print("reading pdf files\n")
    if suffix == ".docx":
        return docx2txt.process(file_path)
    print("reading docx files\n")
    if suffix in [".txt", ".md", ".csv", ".py"]:
        return path.read_text(encoding="utf-8", errors="ignore")
    print("reading other files\n")
    raise ValueError("Unsupported file type. Upload PDF, DOCX, TXT, MD, PY or CSV")

def sse_data(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

def should_stream_chunk(chunk, metadata) -> bool:
    """
    This prevents raw tool/search/RAG JSON from appearing in the frontend
    We only stream normal AI text chunks.
    We do not stream:
    - ToolMessage
    - messages from tool nodes
    - tool call chunks
    - raw tool outputs
    """

    metadata = metadata or {}

    node_name = str(metadata.get("langgraph_node", "").lower())

    if "tool" in node_name:
        return False

    if isinstance(chunk, ToolMessage):
        return False
    if not isinstance(chunk, (AIMessage, AIMessageChunk)):
        return False
    if getattr(chunk, "invalid_tool_calls", None):
        return False
    if getattr(chunk, "tool_calls", None):
        return False

    additional_kwargs = getattr(chunk, "additional_kwargs", {}) or {}

    if additional_kwargs.get("tool_calls"):
        return False

    return True

def extract_text_from_chunk(chunk) -> str:
    """
    to stream the text from the chunk, we need to extract the text from the chunk object
    """
    content =  getattr(chunk, "content", "")

    if not content:
        return ""

    if isinstance(content, str):
        return content

    if isinstance(content,  list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                if item.get("type") == "text" and isinstance(item.get("text"),str):
                    text_parts.append(item["text"])
                elif isinstance(item.get("text"),str):
                    text_parts.append(item["text"])
                elif isinstance(item.get("content"),str):
                    text_parts.append(item["content"])

        return "".join(text_parts)
    return ""