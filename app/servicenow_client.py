import os
import logging
import httpx

logger = logging.getLogger("incident-agent")

SN_INSTANCE_URL = os.environ["SERVICENOW_INSTANCE_URL"].rstrip("/")
SN_USERNAME = os.environ["SERVICENOW_USERNAME"]
SN_PASSWORD = os.environ["SERVICENOW_PASSWORD"]


def _patch_incident(sys_id: str, fields: dict) -> bool:
    """
    Sends a PATCH to update the given incident's fields.
    Returns True on success, False on failure (never raises, per NFR3).
    """
    url = f"{SN_INSTANCE_URL}/api/now/table/incident/{sys_id}"
    try:
        response = httpx.patch(
            url,
            json=fields,
            auth=(SN_USERNAME, SN_PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        response.raise_for_status()
        logger.info(f"[SERVICENOW] Updated {sys_id} with fields: {list(fields.keys())}")
        return True
    except httpx.HTTPStatusError as e:
        logger.error(f"[SERVICENOW] Failed to update {sys_id}: "
                     f"{e.response.status_code} — {e.response.text}")
        return False
    except httpx.RequestError as e:
        logger.error(f"[SERVICENOW] Request error updating {sys_id}: {e}")
        return False


def write_respond(sys_id: str, solution_message: str) -> bool:
    """respond: write solution + resolve the ticket."""
    fields = {
        "work_notes": solution_message,
        "state": "6",  # Resolved
        "close_notes": solution_message,
        "close_code": "Solved (Permanently)",
    }
    return _patch_incident(sys_id, fields)


def write_ask(sys_id: str, question_message: str) -> bool:
    """ask: add a customer-visible clarifying question."""
    fields = {
        "comments": question_message,
    }
    return _patch_incident(sys_id, fields)


def write_escalate(sys_id: str, reason_message: str) -> bool:
    """escalate: add an internal work note explaining the escalation."""
    fields = {
        "work_notes": f"Escalated: {reason_message}",
    }
    return _patch_incident(sys_id, fields)