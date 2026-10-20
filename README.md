# Agentic AI Customer Support & Ticket Resolution System

An AI-powered customer support application built with Django, Django REST Framework, PostgreSQL, and Google Gemini.

The system helps customers retrieve order information, find answers to frequently asked questions, and create support tickets when additional assistance is needed.

The AI agent uses tool/function calling to select and execute appropriate backend operations based on customer requests.

## 1. Problem Statement

Customer support teams frequently handle repetitive inquiries, such as order-status requests, shipping questions, and issues requiring human assistance.

Manually handling these requests can increase response times and support workload.

This project explores how an AI agent can automate common support tasks while preserving conversation history and recording tool execution activity.

## 2. Features

- Conversational AI customer support
- Automatic tool selection using Gemini function calling
- Order lookup using order number and customer email
- FAQ search using stored knowledge-base entries
- Support ticket creation
- Conversation and message history
- Agent action logging
- Ticket management through REST APIs
- Browser-based chat interface
- Automated backend tests
- Agent evaluation and performance measurements

## 3. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Django |
| REST API | Django REST Framework |
| Database | PostgreSQL |
| AI Model Provider | Google Gemini |
| AI Integration | Google Gen AI Python SDK |
| Frontend | HTML, JavaScript |
| Testing | Django Test Framework |
| Performance Evaluation | Python, psutil |
| Version Control | Git and GitHub |

## 4. System Architecture

```text
Customer
   |
   v
Web Chat Interface
   |
   v
Django REST API
   |
   v
AI Agent Service
   |
   +---- Google Gemini
   |        |
   |        v
   |    Tool Selection
   |
   +---- lookup_order()
   |
   +---- search_faq()
   |
   +---- create_support_ticket()
   |
   v
PostgreSQL Database
   |
   +---- Orders
   +---- FAQ Entries
   +---- Conversations
   +---- Messages
   +---- Support Tickets
   +---- Agent Actions
```

### Agent Workflow

1. A customer submits a message through the chat interface.
2. The Django API validates the request.
3. The agent receives the message and relevant conversation history.
4. Gemini determines whether a backend tool is required.
5. The selected tool interacts with the application database.
6. The tool execution is recorded in the agent action log.
7. The agent generates a customer-facing response.
8. The response and conversation history are stored.

## 5. AI Agent Tools

### `lookup_order`

Retrieves order information using an order number and customer email.

Example request:

> What is the status of order ORD-1001?

### `search_faq`

Searches stored FAQ entries for relevant answers.

Example request:

> How long does standard shipping take?

### `create_support_ticket`

Creates a support ticket associated with a conversation.

Example request:

> I have a problem with my order and need support.

The agent can select these tools through Gemini's function-calling functionality.

## 6. Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version
- PostgreSQL
- Git
- A Gemini API key

### Clone the Repository

```bash
git clone https://github.com/FarahEilouti/customer-support-agent.git
cd customer-support-agent
```

### Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Configure PostgreSQL

Create a PostgreSQL database and an application database user.

The default example configuration uses:

- Database: `customer_support_db`
- User: `support_user`
- Host: `localhost`
- Port: `5432`

The database user must have the permissions required to connect to the database and run Django migrations.

### Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

Example:

```dotenv
DJANGO_SECRET_KEY=replace_with_your_secret_key
DJANGO_DEBUG=True

DB_NAME=customer_support_db
DB_USER=support_user
DB_PASSWORD=replace_with_your_database_password
DB_HOST=localhost
DB_PORT=5432

GEMINI_API_KEY=replace_with_your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

The model name above reflects the model used in the recorded evaluation. Configure a model that is available to your Gemini API account.

Never commit `.env`, API keys, or database passwords to GitHub.

### Apply Database Migrations

```powershell
python manage.py migrate
```

### Start the Development Server

```powershell
python manage.py runserver
```

Open the application at:

http://127.0.0.1:8000/

The Django admin interface is available at:

http://127.0.0.1:8000/admin/

## 7. REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat/` | Send a customer message to the AI agent |
| GET | `/api/tickets/` | Retrieve support tickets |
| GET | `/api/tickets/<ticket_id>/` | Retrieve a support ticket |
| PATCH | `/api/tickets/<ticket_id>/` | Update a support ticket |

Ticket management endpoints require Django staff/admin authorization.

### Chat API Example

**POST `/api/chat/`**

```json
{
  "customer_email": "customer@example.com",
  "message": "What is the status of order ORD-1001?"
}
```

Example response structure:

```json
{
  "conversation_id": "conversation-uuid",
  "response": "Customer-facing AI response",
  "latency_seconds": 1.5,
  "tools_used": ["lookup_order"]
}
```

The values above illustrate the response structure and are not a recorded API response.

To continue an existing conversation, include its valid `conversation_id` in the request body.

## 8. Database Models

The application uses the following models:

- **Order:** Stores customer order information.
- **FAQEntry:** Stores FAQ questions, answers, and categories.
- **Conversation:** Represents a customer support conversation.
- **Message:** Stores user and assistant messages.
- **SupportTicket:** Stores support requests, priorities, and statuses.
- **AgentAction:** Records tool execution details and outcomes.

## 9. Testing

### Django System Check

```powershell
python manage.py check
```


### Automated Backend Tests

Run the complete Django test suite:

```powershell
python manage.py test
```

Latest verified local test run:

**17 tests passed, 0 failures.**

The automated tests cover:
- Order lookup and customer-email matching
- FAQ search and input validation
- Support ticket creation
- Agent reliability when Gemini API requests fail
- Chat API throttling
- Safe handling of unexpected server errors
- FAQ keyword matching, ranking, and inactive-entry filtering

The tests use mocks for Gemini-dependent scenarios, allowing the automated suite to run without making real Gemini API requests.


### AI Agent Evaluation

```powershell
python -m scripts.evaluate_agent
```

The evaluation sends predefined questions to the Gemini-powered agent and compares actual tool selections with expected selections.

Running this script makes real Gemini API requests and may consume available API quota.

Evaluation output is stored in the `evaluation/` directory.

## 10. Performance Evaluation

A successful evaluation run produced the following results:

| Metric | Recorded Result |
|---|---:|
| Tool Selection Test Cases | 8 |
| Correct Tool Selections | 8 |
| Tool Selection Accuracy | 100% |
| Average Response Latency | 1.391 seconds |
| Average Local Process Memory Snapshot | 80.79 MB |
| Backend Automated Tests | 8 passed |

The tool-selection result is based on eight predefined scenarios and should not be interpreted as a general accuracy guarantee.

Memory measurements represent the local evaluation process, not the remotely hosted Gemini model.

A later evaluation attempt encountered HTTP 429 `RESOURCE_EXHAUSTED` because of Gemini API quota restrictions. This is an external API availability limitation, not a completed tool-selection result.

For the methodology, analysis, and limitations, see:

[Performance Evaluation Report](docs/PERFORMANCE_EVALUATION.md)

## 11. Error Handling and Limitations

The system depends on Gemini API availability and configured usage quotas.

Potential limitations include:

- External API rate limits and temporary service failures
- Variation in AI-generated responses
- A limited initial evaluation dataset
- No production load-testing results
- The need for additional verification of duplicate-ticket prevention and recovery after interrupted requests

- The chat API is currently anonymous and uses a request throttle of 20 requests per hour. Throttling limits usage but does not verify customer identity.
- Customer email addresses are provided in requests and are not authenticated. A production version should require customer login and derive the customer's identity from the authenticated user rather than trusting a submitted email address.

This project is intended as an educational prototype rather than a production-ready customer support platform.

## 12. Project Structure

```text

customer-support-agent/
│
├── config/
│   ├── settings.py
│   └── urls.py
│
├── support/
│   ├── models/
│   │   ├── order.py
│   │   ├── faq_entry.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── support_ticket.py
│   │   └── agent_action.py
│   │
│   ├── ai/
│   │   ├── gemini_client.py
│   │   └── prompts/
│   │       └── support_agent.md
│   │
│   ├── services/
│   │   ├── chat/
│   │   │   ├── agent_service.py
│   │   │   ├── agent_tools.py
│   │   │   └── conversation_service.py
│   │   │
│   │   └── support/
│   │       ├── order_lookup.py
│   │       ├── faq_search.py
│   │       └── ticket_creation.py
│   │
│   ├── views/
│   │   ├── chat/
│   │   │   ├── chat_view.py
│   │   │   └── frontend_view.py
│   │   │
│   │   └── support/
│   │       ├── ticket_list_view.py
│   │       └── ticket_detail_view.py
│   │
│   ├── serializers/
│   ├── templates/
│   │   └── support/
│   │       └── chat.html
│   ├── tests/
│   ├── admin.py
│   └── urls.py
│
├── scripts/
│   └── evaluate_agent.py
│
├── evaluation/
│
├── docs/
│   └── PERFORMANCE_EVALUATION.md
│
├── .env.example
├── requirements.txt
├── manage.py
└── README.md

```

## 13. Future Improvements

Potential improvements include:

- Larger and more diverse agent evaluation datasets
- Automated ticket categorization and priority assignment
- Stronger ticket-creation idempotency
- More robust retry and rate-limit handling
- Additional administrative workflows
- Production deployment and monitoring
- Load testing with concurrent requests

## 14. Repository

GitHub: https://github.com/FarahEilouti/customer-support-agent

## 15. Project Context

Developed as a final project for an Agentic AI training course.

The project demonstrates the integration of a conversational AI model, backend business tools, persistent data storage, REST APIs, and practical evaluation techniques.

## Quick Start — First-Time Demo

After installing the dependencies, configuring PostgreSQL, and creating your `.env` file, follow these steps.

### 1. Set up the database

```powershell
python manage.py migrate
```

### 2. Load sample data

```powershell
python manage.py seed_demo_data
```

This command creates a sample order and FAQ entries so you can test the application without manually entering database records.

The demo uses fictional data and is intended for local development.

### 3. Start the application

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

### 4. Use the demo customer

Enter the following customer email in the chat interface:

```text
customer@example.com
```

### 5. Try these example messages

**Example 1 — FAQ Search**

```text
How long does standard shipping take?
```

The agent should use the FAQ search tool to retrieve the shipping information.

**Example 2 — Order Lookup**

```text
What is the status of order ORD-1001?
```

The agent should retrieve the demo order information from PostgreSQL.

**Example 3 — Create a Support Ticket**

```text
My order arrived damaged. Please create a support ticket.
```

The agent should create a support ticket and return its ID.

### 6. View the results

Successful requests should produce customer-facing responses in the chat interface.

Support ticket records and tool execution logs are stored in PostgreSQL. Authorized staff users can access ticket management functionality through the application's protected endpoints.

### Important Notes

- A valid Gemini API key is required for live AI responses.
- API quotas and model availability depend on the Gemini account.
- The demo data contains fictional records only.
- This application is a development prototype, not a publicly deployed service.