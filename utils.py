# add all helper functionality
from config import settings
from pathlib import Path
from pypdf import PdfReader
import docx2txt

# Default model for app
DEFAULT_MODEL = settings.GEMINI_MODEL if settings.GEMINI_MODEL else "gemini-2.5-pro"

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

    if not model_name:
        return DEFAULT_MODEL

    model_name = model_name.strip()

    if model_name not in ALLOWED_MODELS:
        return DEFAULT_MODEL

    return model_name

def read_files_text(file_path: str) -> str:
    """
    This function reads the user uploaded files.
    Currently only supports '.pdf' and '.txt' file format properly
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""
            text += "\n"

        return text

    if suffix == ".docx":
        return docx2txt.process(file_path)

    if suffix in [".txt", ".md", ".csv", ".py"]:
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Upload PDF, DOCX, TXT, MD, PY or CSV")

