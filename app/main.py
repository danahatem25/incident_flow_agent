from dotenv import load_dotenv
load_dotenv()
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from app.gemini_client import get_decision
from app.servicenow_client import write_respond, write_ask, write_escalate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("incident-agent")

app = FastAPI()
processed_incidents: set[str] = set()


class IncidentPayload(BaseModel):
    incident_sys_id: str
    number: str
    short_description: str
    description: str = ""      
    priority: int = Field(ge=1, le=5)


def process_incident(payload: IncidentPayload):
    if payload.incident_sys_id in processed_incidents:
        logger.info(f"[SKIP] {payload.number} (sys_id={payload.incident_sys_id}) already processed")
        return

    processed_incidents.add(payload.incident_sys_id)

    logger.info(f"[BACKGROUND] Processing incident {payload.number} "
                f"(sys_id={payload.incident_sys_id}): "
                f"'{payload.short_description}' (priority {payload.priority})")

    result = get_decision(payload.short_description, payload.description)
    decision = result["decision"]
    message = result["message"]

    logger.info(f"[DECISION] {payload.number} → {decision}: {message}")

    if decision == "respond":
        success = write_respond(payload.incident_sys_id, message)
    elif decision == "ask":
        success = write_ask(payload.incident_sys_id, message)
    else:  # escalate
        success = write_escalate(payload.incident_sys_id, message)

    if success:
        logger.info(f"[DONE] {payload.number} updated successfully")
    else:
        logger.error(f"[DONE] {payload.number} update FAILED")
        

@app.post("/webhook", status_code=202)
async def webhook(payload: IncidentPayload, background_tasks: BackgroundTasks):
    logger.info(f"[RECEIVED] {payload.number}")
    background_tasks.add_task(process_incident, payload)
    return {"status": "accepted", "number": payload.number}


@app.get("/health")
async def health():
    return {"status": "ok"}