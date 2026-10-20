
import csv
import os
import time
from datetime import datetime
from pathlib import Path
from statistics import mean
from unittest.mock import patch

import django
import psutil
from google.genai.errors import ClientError, ServerError


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)
django.setup()

from support.services.agent_service import run_agent


TEST_CASES = [
    {
        "id": "FAQ-01",
        "question": "How long does standard shipping take?",
        "expected_tools": ["search_faq"],
    },
    {
        "id": "FAQ-02",
        "question": "Please search your FAQ for shipping information.",
        "expected_tools": ["search_faq"],
    },
    {
        "id": "FAQ-03",
        "question": "What does your FAQ say about delivery times?",
        "expected_tools": ["search_faq"],
    },
    {
        "id": "ORDER-01",
        "question": "What is the status of order ORD-1001?",
        "expected_tools": ["lookup_order"],
    },
    {
        "id": "ORDER-02",
        "question": "Please look up my order ORD-1001.",
        "expected_tools": ["lookup_order"],
    },
    {
        "id": "ORDER-03",
        "question": "Can you check order ORD-9999?",
        "expected_tools": ["lookup_order"],
    },
    {
        "id": "TICKET-01",
        "question": (
            "Please create a support ticket titled "
            "'Damaged delivery' because my package arrived damaged."
        ),
        "expected_tools": ["create_support_ticket"],
    },
    {
        "id": "TICKET-02",
        "question": (
            "I need human assistance with order ORD-1001. "
            "Please open a support ticket for me."
        ),
        "expected_tools": ["create_support_ticket"],
    },
    {
        "id": "AMBIGUOUS-01",
        "question": "I have a problem with my order.",
        "expected_tools": [],
    },
    {
        "id": "GENERAL-01",
        "question": "Hello!",
        "expected_tools": [],
    },
    {
        "id": "GENERAL-02",
        "question": "Thank you for your help!",
        "expected_tools": [],
    },
]


def memory_mb():
    """Measure memory of the local evaluation process."""
    process = psutil.Process(os.getpid())
    return round(
        process.memory_info().rss / (1024 * 1024),
        2,
    )


def run_evaluation():
    results = []
    api_failure_count = 0

    output_dir = Path("evaluation")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"agent_evaluation_{timestamp}.csv"

    print("=" * 60)
    print("AGENT EVALUATION")
    print("=" * 60)

    with patch(
        "support.services.agent_tools.create_support_ticket",
        return_value={
            "success": False,
            "error": "Ticket creation disabled during evaluation.",
        },
    ):
        for case in TEST_CASES:
            print(f"\nRunning {case['id']}...")

            start = time.perf_counter()
            actual_tools = []
            answer = ""
            error = ""

            try:
                response = run_agent(
                    customer_email="customer@example.com",
                    user_message=case["question"],
                )
                actual_tools = response["tools_used"]
                answer = response["response"]

            except (ClientError, ServerError) as exc:
                error = f"Gemini API error {exc.code}"
                api_failure_count += 1
                print(error)

            except Exception as exc:
                error = type(exc).__name__
                print(f"Unexpected error: {error}")

            latency = round(time.perf_counter() - start, 3)

            completed = not bool(error)
            correct = (
                completed
                and set(actual_tools) == set(case["expected_tools"])
            )

            results.append(
                {
                    "case_id": case["id"],
                    "question": case["question"],
                    "expected_tools": ", ".join(
                        case["expected_tools"]
                    ) or "none",
                    "actual_tools": ", ".join(
                        actual_tools
                    ) or "none",
                    "completed": completed,
                    "correct": correct,
                    "latency_seconds": latency,
                    "memory_mb": memory_mb(),
                    "error": error,
                    "response": answer,
                }
            )

            print(f"Completed: {completed}")
            print(f"Correct: {correct}")
            print(f"Latency: {latency}s")

            if error.startswith("Gemini API error"):
                print("Stopping to avoid additional API failures.")
                break

            # Reduce request bursts against the Gemini free tier.
            time.sleep(5)

    if not results:
        print("No evaluation results collected.")
        return

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys(),
        )
        writer.writeheader()
        writer.writerows(results)

    completed_results = [
        result for result in results
        if result["completed"]
    ]

    correct_count = sum(
        result["correct"] for result in completed_results
    )

    accuracy = (
        correct_count / len(completed_results) * 100
        if completed_results
        else None
    )

    latencies = [
        result["latency_seconds"]
        for result in completed_results
    ]

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Planned cases: {len(TEST_CASES)}")
    print(f"Attempted cases: {len(results)}")
    print(f"Completed cases: {len(completed_results)}")
    print(f"API failures: {api_failure_count}")

    if accuracy is not None:
        print(f"Tool selection accuracy (completed cases only): {accuracy:.2f}%")
    else:
        print("Tool selection accuracy (completed cases only): N/A")

    if latencies:
        print(
            f"Average successful-request latency: "
            f"{mean(latencies):.3f}s"
        )

    print(
        f"Average process memory: "
        f"{mean(r['memory_mb'] for r in results):.2f} MB"
    )

    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    run_evaluation()
