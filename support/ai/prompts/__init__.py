
from pathlib import Path


PROMPT_PATH = Path(__file__).resolve().parent / "support_agent.md"


def load_system_instruction() -> str:
    """Load the customer support system instruction."""
    return PROMPT_PATH.read_text(encoding="utf-8").strip()
