# Incident Flow Agent

An automated support ticket triage agent built for the AI Engineering Internship (Task 0). When a new incident is created on a ServiceNow developer instance (PDI), this service automatically decides what to do with it — respond with a known fix, ask a clarifying question, or escalate to a human — using Google's Gemini API grounded strictly in a small knowledge base. The result is written back onto the same ticket automatically, with no manual steps.

## How it works

1. A new incident is created on ServiceNow (manually by a user, or via automation).
2. A ServiceNow Business Rule fires automatically and sends the incident's details to this service as JSON.
3. This service (FastAPI) validates the payload, responds immediately, and processes the ticket in the background.
4. The background task sends the ticket text and five knowledge base articles to Gemini, asking for one of three decisions: `respond`, `ask`, or `escalate`.
5. The service writes the decision back onto the same incident via the ServiceNow REST API:
   - **respond** → resolves the ticket and writes the solution as close notes
   - **ask** → adds a clarifying question as a customer-visible comment
   - **escalate** → adds an internal work note explaining why it needs human review

## Tech stack

- **Python 3.11+** with **FastAPI** — webhook service
- **Google Gemini API** (`gemini-3.5-flash-lite`) — decision-making
- **ServiceNow PDI** — ticketing system (source and destination of data)
- **ngrok** — exposes the local service to ServiceNow's Business Rule
- **httpx** — HTTP client for the ServiceNow REST API

## Project structure

```
IncidentFlowAgent/
├── app/
│   ├── main.py                # FastAPI app: /webhook endpoint, validation, background task
│   ├── gemini_client.py       # Gemini API call, prompt loading, response parsing, retries
│   ├── servicenow_client.py   # ServiceNow REST API write-back (respond/ask/escalate)
│   └── prompt.txt             # Exact prompt template sent to Gemini
├── test_gemini.py             # Standalone test script for the 3 sample tickets (Gemini logic only)
├── test_servicenow.py         # Standalone test script for write-back logic (ServiceNow only)
├── requirements.txt
├── .env.example                # Lists required environment variables (no real values)
├── .gitignore
└── README.md
```

## Setup and installation

### Prerequisites
- Python 3.11+ installed and available as `python` on your PATH
- A free [ServiceNow developer account](https://developer.servicenow.com) with a requested PDI instance
- A free [Gemini API key](https://aistudio.google.com) (no credit card required)
- [ngrok](https://ngrok.com) installed and authenticated with a free account

### 1. Clone the repository
```powershell
git clone https://github.com/danahatem25/incident_flow_agent.git
cd incident_flow_agent
```

### 2. Create and activate a virtual environment
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
*(On macOS/Linux: `source venv/bin/activate`)*

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to a new file called `.env`, and fill in your real values:
```
GEMINI_API_KEY=your_gemini_api_key
SERVICENOW_INSTANCE_URL=https://devXXXXXX.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=your_pdi_admin_password
```
`.env` is git-ignored and should never be committed.

### 5. Run the service
```powershell
uvicorn app.main:app --reload --port 8000
```
Confirm you see `Application startup complete.`

### 6. Expose the service publicly with ngrok
In a separate terminal:
```powershell
ngrok http 8000
```
Copy the `https://....ngrok-free.dev` (or `.app`) URL shown in the output.

### 7. Connect ServiceNow to your service
1. In your ServiceNow PDI, search **"All"** for **Business Rules** and create a new one:
   - Name: `Task0 - Send Incident to Agent`
   - Table: `Incident [incident]`
   - Advanced: checked
   - When: `after`, with **Insert** checked
2. In the **Advanced** tab, paste the script from `AI_Engineering_Task0_Assets/business_rule.js`, replacing `YOUR_ENDPOINT` with your ngrok URL from Step 6 (keep `/webhook` at the end).
3. Click **Submit**.

### 8. Test it
Create a new incident on your PDI (any short description). Within a few seconds, your service's terminal should log the full chain (`[RECEIVED]` → `[BACKGROUND]` → `[DECISION]` → `[DONE]`), and the same incident on ServiceNow will be updated automatically.

## Testing the core logic in isolation

Two standalone scripts let you test the Gemini decision logic and the ServiceNow write-back independently of the full webhook flow:

```powershell
python test_gemini.py       # Tests all 3 sample tickets against the Gemini prompt
python test_servicenow.py   # Tests write-back for respond/ask/escalate against real sys_ids you provide
```

## Known limitations

- **ngrok URLs change on every restart** (free tier). If you stop and restart ngrok, you must update the endpoint URL in the ServiceNow Business Rule script to match the new URL, or the automatic trigger will silently fail to reach your service.
- **PDI instances sleep after inactivity.** If your instance seems unreachable, visit the ServiceNow developer portal and wake it up.
- **Duplicate-processing protection is in-memory only.** If the service restarts, its record of already-processed incidents is cleared. This is acceptable for this project's scope but would need a persistent store (e.g. a database) for production use.
- **Gemini free-tier rate limits vary by model and can change.** This project uses `gemini-3.5-flash-lite` for its generous free-tier quota; if you hit rate limit errors, check your current limits at [aistudio.google.com/rate-limit](https://aistudio.google.com/rate-limit).

## Author

Built by Dana Hatem for the Sprints × BARQ Systems AI Engineering Internship, Task 0.
