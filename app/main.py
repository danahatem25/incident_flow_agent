import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("incident-agent")

app = FastAPI()


class IncidentPayload(BaseModel):
    incident_sys_id: str
    number: str
    short_description: str
    description: str = ""      
    priority: int = Field(ge=1, le=5)


def process_incident(payload: IncidentPayload):
    """
    Placeholder for the real work: Gemini decision + ServiceNow write-back.
    For now, just log it so we can confirm the background task runs.
    """
    logger.info(f"[BACKGROUND] Processing incident {payload.number} "
                f"(sys_id={payload.incident_sys_id}): "
                f"'{payload.short_description}' (priority {payload.priority})")


@app.post("/webhook", status_code=202)
async def webhook(payload: IncidentPayload, background_tasks: BackgroundTasks):
    logger.info(f"[RECEIVED] {payload.number}")
    background_tasks.add_task(process_incident, payload)
    return {"status": "accepted", "number": payload.number}


@app.get("/health")
async def health():
    return {"status": "ok"}