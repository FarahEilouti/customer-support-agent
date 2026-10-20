import re
from django.db import DatabaseError
from support.models import FAQEntry


def search_faq(query: str) -> dict:
    """
    Search active FAQ entries using weighted keyword matching.
    """

    query = query.strip().lower()

    if not query:
        return {
            "success": False,
            "error": "A search query is required.",
        }

    # Ignore common words that add little meaning.
    stop_words = {
        "a", "an", "the", "is", "are", "am",
        "was", "were", "do", "does", "did",
        "how", "what", "when", "where", "why",
        "can", "could", "would", "should",
        "i", "me", "my", "you", "your",
        "we", "our", "it", "this", "that",
        "to", "for", "of", "in", "on",
        "at", "with", "and", "or", "from",
        "please", "tell", "about",
    }

    def tokenize(text: str) -> set:
        """Extract whole-word tokens, excluding stop words."""
        words = re.findall(r"\b\w+\b", text.lower())
        return set(words) - stop_words

    keywords = tokenize(query)

    if not keywords:
        return {
            "success": False,
            "error": "No relevant FAQ was found.",
        }

    try:
        faqs = list(
            FAQEntry.objects.filter(is_active=True).values(
                "id",
                "question",
                "answer",
                "category",
            )
        )
    except DatabaseError:
        return {
            "success": False,
            "error": "FAQ search is temporarily unavailable.",
        }

    matches = []

    for faq in faqs:
        question_words = tokenize(faq["question"])
        answer_words = tokenize(faq["answer"])
        category_words = tokenize(faq["category"])

        # Give higher weight to question matches.
        score = (
            3 * len(keywords & question_words)
            + 2 * len(keywords & category_words)
            + len(keywords & answer_words)
        )

        if score > 0:
            matches.append((score, faq))

    # Stable ranking: score, then question, then ID.
    matches.sort(
        key=lambda item: (
            -item[0],
            item[1]["question"].lower(),
            item[1]["id"],
        )
    )

    if not matches:
        return {
            "success": False,
            "error": "No relevant FAQ was found.",
        }

    results = [
        {
            "question": faq["question"],
            "answer": faq["answer"],
            "category": faq["category"],
        }
        for _, faq in matches[:3]
    ]

    return {
        "success": True,
        "results": results,
    }
