import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from google import genai
from google.genai import types

from support.services.support_tools import search_faq


def find_shipping_information(query: str) -> dict:
    """Search the support knowledge base for shipping information."""
    print(f"[TOOL CALLED] find_shipping_information(query={query!r})")
    return search_faq(query)


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

chat = client.chats.create(
    model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
    config=types.GenerateContentConfig(
        system_instruction=(
            "You are a customer support assistant. "
            "Use the available tool to answer shipping questions. "
            "Do not invent shipping policies."
        ),
        tools=[find_shipping_information],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=False,
            maximum_remote_calls=3,
        ),
    ),
)

response = chat.send_message(
    "How long does shipping take? Please check the support FAQ."
)

print("\nGemini response:")
print(response.text)