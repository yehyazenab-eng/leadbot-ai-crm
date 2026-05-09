# AI Lead Bot (Python)

Modern lead-bot backend for businesses:
- Lead saving (SQLite)
- Smart responses (rules by default, optional LLM provider)
- Notification system (console + optional webhook/email/macOS notification)
- Simple CRM (stages, notes, interactions)
- Clean structure (FastAPI + service layer)

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## CRM UI

Open:

- `http://127.0.0.1:8000/crm/leads`
- `http://127.0.0.1:8000/crm/notifications`

## Environment

Copy/paste and adjust:

```bash
export DATABASE_URL="sqlite:///./leadbot.db"

# Optional: send webhook on lead create/update
export NOTIFY_WEBHOOK_URL=""

# Optional: SMTP email notifications
export SMTP_HOST=""
export SMTP_PORT="587"
export SMTP_USERNAME=""
export SMTP_PASSWORD=""
export SMTP_FROM=""
export SMTP_TO=""

# Optional: OpenAI smart responses
export AI_PROVIDER="rules"   # rules | openai
export OPENAI_API_KEY=""
export OPENAI_MODEL="gpt-4.1-mini"
```

## API overview

- `POST /chat/respond`: Smart response + optionally save lead if detected
- `POST /leads`: Create lead
- `GET /leads`: List leads
- `GET /leads/{lead_id}`: Lead details
- `PATCH /leads/{lead_id}`: Update lead (stage/status/fields)
- `POST /leads/{lead_id}/notes`: Add note
- `POST /leads/{lead_id}/interactions`: Log interaction
- `GET /notifications`: List in-app notifications
- `PATCH /notifications/{notification_id}`: Mark read/unread

## Import old CSV

If you have an existing `leads.csv`, you can import it:

```bash
python3 -m app.scripts.import_csv leads.csv
```

