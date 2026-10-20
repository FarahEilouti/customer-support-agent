
# Performance Evaluation Report

## 1. Project Overview

**Project:** Agentic AI Customer Support & Ticket Resolution System

The system is a Django-based customer support application that uses Google's Gemini model for conversational assistance and automatic tool selection.

The AI agent can interact with backend tools to:
- Search existing FAQ entries.
- Retrieve customer order information.
- Create support tickets for human assistance.

The system uses PostgreSQL to store application data, conversation history, support tickets, and agent action logs.

## 2. Evaluation Objectives

The evaluation focuses on:

1. Tool Selection Accuracy
2. Response Latency
3. Application Process Memory Usage
4. Backend Tool Correctness
5. API Reliability and Limitations

## 3. Evaluation Environment

- Backend: Django + Django REST Framework
- Database: PostgreSQL
- AI Provider: Google Gemini API
- AI Model: gemini-3.5-flash-lite
- Language: Python 3.10
- Evaluation Script: scripts/evaluate_agent.py
- Memory Measurement: psutil
- Operating System: Windows

The evaluation was performed against the development environment using predefined test questions and real Gemini API requests.

## 4. Tool Selection Accuracy

### Methodology

Eight predefined questions were sent to the AI agent.

Each question had an expected tool selection.

The selected tools were compared with the expected tools.

Repeated calls to the same tool were treated as one unique tool selection for accuracy calculation.

### Results

| Category | Test Cases | Correct |
|---|---:|---:|
| FAQ Search | 3 | 3 |
| Order Lookup | 3 | 3 |
| General Conversation (No Tool) | 2 | 2 |
| **Total** | **8** | **8** |

### Accuracy Formula

Tool Selection Accuracy = (Correct Selections / Total Cases) × 100

Tool Selection Accuracy = (8 / 8) × 100 = **100%**

### Interpretation

The agent selected the expected tools in all eight successful evaluation cases.

This demonstrates correct tool routing for the tested scenarios.

However, the evaluation dataset is small and does not establish that the agent will achieve 100% accuracy across all possible customer requests.

One FAQ test triggered two calls to the same tool. This did not affect unique-tool selection accuracy but indicates an opportunity to reduce redundant tool calls.

## 5. Response Latency

Response latency was measured using Python's time.perf_counter() around each run_agent() call.

The recorded times represent evaluation-process execution time, including the agent workflow and Gemini API communication.

### Successful Evaluation Results

| Test Case | Latency (seconds) |
|---|---:|
| FAQ-01 | 2.138 |
| FAQ-02 | 1.333 |
| FAQ-03 | 1.933 |
| ORDER-01 | 1.454 |
| ORDER-02 | 1.430 |
| ORDER-03 | 1.425 |
| GENERAL-01 | 0.659 |
| GENERAL-02 | 0.754 |

**Average Response Latency: 1.391 seconds**

### Interpretation

General conversational requests were faster than requests involving backend tools.

Tool-based requests require additional processing, including tool execution and potentially multiple model interactions.

Latency may vary depending on network conditions, Gemini API performance, and request complexity.

## 6. Memory Usage

Memory was measured using psutil.

The script recorded the resident set size (RSS) of the local Python evaluation process after each test.

**Average Process Memory Snapshot: 80.79 MB**

This represents memory usage of the local evaluation process, not memory consumption of the remote Gemini model.

The measurement is an average of snapshots rather than peak memory usage or the isolated memory cost of each request.

## 7. Backend Automated Tests

The backend support tools were tested using Django's automated testing framework.

A total of eight tests passed.

The tests covered:

- Existing and missing FAQ results
- Existing and missing orders
- Order lookup with an incorrect customer email
- Successful ticket creation
- Empty ticket title validation
- Invalid ticket priority validation

**Result: 8 tests passed, 0 failed.**

These tests validate backend tool behavior independently of Gemini's tool-selection decisions.

## 8. API Reliability and Rate Limits

A second evaluation attempt failed because the Gemini API returned:

**HTTP 429 RESOURCE_EXHAUSTED**

The error indicated that the free-tier request quota had been exceeded for the configured model.

All eight requests in the second run failed due to API quota restrictions.

These failures are not evidence of incorrect tool selection, because the model did not successfully complete the requests.

The original evaluation script reported 0% accuracy for this run because failed API requests were counted as incorrect selections.

The evaluation script was subsequently revised to distinguish completed cases from API failures and stop after an API error.

The revised script has not yet been re-evaluated against Gemini.

### Reliability Limitations

- The system depends on availability of the external Gemini API.
- Free-tier rate limits can interrupt requests.
- External service failures can affect response completion.
- Duplicate ticket prevention and failure recovery require additional verification.

## 9. Evaluation Limitations

The following limitations apply:

- Only eight successful tool-selection scenarios were evaluated.
- The test questions were predefined rather than sampled from real customer traffic.
- Tool-selection accuracy does not directly measure answer quality or task completion.
- Memory measurements cover the local evaluation process only.
- Latency measurements were collected from one successful evaluation run.
- Ticket creation was not included in the eight-case live agent evaluation.
- Production load testing and concurrent-user testing were not performed.

## Reliability Testing

Two additional automated tests were implemented using mocked Gemini API failures.

| Scenario | Result |
|---|---|
| Gemini fails after successful support ticket creation | Passed |
| Gemini fails before support ticket creation | Passed |

**Result: 2 tests passed in 0.135 seconds.**

The tests confirmed that a successfully created support ticket remains recorded and that the agent returns its confirmation even if Gemini subsequently fails.

When Gemini fails before any ticket is created, the agent propagates the API error rather than falsely reporting success.

The tests used mocks and did not consume real Gemini API requests.

**Limitation:** These tests do not establish full idempotency or prevent duplicate tickets across repeated customer requests.

## 10. Updated Evaluation — October 19, 2026

### Evaluation Scope

An updated evaluation was conducted using 11 predefined scenarios:

- 3 FAQ search scenarios
- 3 order lookup scenarios
- 2 support ticket creation scenarios
- 1 ambiguous customer request
- 2 general conversation scenarios

Real Gemini API requests were used to evaluate tool selection.

Ticket creation was mocked during this evaluation to prevent
the creation of real support tickets. Therefore, the ticket
creation scenarios measure tool selection, not successful
database ticket creation.

### Results

| Metric | Result |
|---|---|
| Planned scenarios | 11 |
| Attempted scenarios | 8 |
| Completed scenarios | 7 |
| Correct tool selections | 7 |
| Tool selection accuracy (completed cases only) | 100% |
| Gemini API failures | 1 |
| Average completed-request latency | 3.256 seconds |
| Average local process memory | 81.36 MB |

The three FAQ scenarios, three order lookup scenarios, and
TICKET-01 completed with the expected tool selections.

FAQ-03 invoked the FAQ search tool twice. Repeated calls to the
same tool were treated as one unique tool selection for accuracy.

TICKET-02 failed due to Gemini API error 429 (RESOURCE_EXHAUSTED).
The evaluation stopped automatically to avoid further API failures.

AMBIGUOUS-01, GENERAL-01, and GENERAL-02 were not executed
during this run.

### Ticket Creation Verification

Ticket creation was also verified separately through the actual
web interface and PostgreSQL database.

Ticket ID 40 was successfully created with:

- Title: Ticket creation verification
- Priority: medium
- Status: open

The corresponding successful create_support_ticket action was
recorded in AgentAction, and the related conversation contained
four saved messages.

This verifies actual ticket creation separately from the
mocked tool-selection evaluation.

### Interpretation and Limitations

The agent selected the expected tools in all seven completed
scenarios. However, this result does not demonstrate 100%
accuracy across all 11 planned scenarios or across real-world
customer requests.

The incomplete evaluation was caused by an external Gemini API
quota error, not an observed incorrect tool selection.

The evaluation uses a small predefined dataset and does not
measure production concurrency, end-to-end answer quality,
or guaranteed ticket idempotency.

The earlier evaluation results remain documented above for
historical comparison.


## 11. Conclusion

The Agentic AI Customer Support & Ticket Resolution System demonstrated correct tool selection across the successfully completed evaluation scenarios.

The initial evaluation completed 8 out of 8 predefined scenarios, with 100% tool-selection accuracy, an average response latency of 1.391 seconds, and average local process memory usage of 80.79 MB.

The updated evaluation on October 19, 2026, expanded the dataset to 11 planned scenarios. Seven scenarios completed successfully, with 100% tool-selection accuracy among completed cases. The average successful-request latency was 3.256 seconds, and average local process memory usage was 81.36 MB.

The eighth attempted scenario was interrupted by a Gemini API HTTP 429 quota error, leaving three scenarios unexecuted. Therefore, the updated evaluation does not establish accuracy across all 11 planned scenarios.

Actual support ticket creation was separately verified through the web interface and PostgreSQL database using Ticket ID 40. Automated Django testing also passed all 17 tests after the project refactoring.

Overall, the results demonstrate reliable backend tool execution and correct tool routing in the tested scenarios. The main limitations are the small evaluation dataset, external Gemini API quota restrictions, unverified customer identity, and the absence of guaranteed ticket idempotency.

Future improvements should focus on customer authentication, broader evaluation coverage, duplicate-ticket prevention, and production-level reliability testing.
