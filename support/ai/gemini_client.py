
from django.conf import settings
from google import genai


def get_client():
    """Create a Gemini client using Django settings."""
    return genai.Client(
        api_key=settings.GEMINI_API_KEY
    )
