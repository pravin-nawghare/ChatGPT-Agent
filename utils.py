# add all helper functionality
from config import settings


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
