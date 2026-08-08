# add all helper functionality
from config import settings
from pathlib import Path
from pypdf import PdfReader
import docx2txt
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

