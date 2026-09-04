import os
import json
import logging
from google import genai
import time
from google.genai import errors as genai_errors

logger = logging.getLogger("incident-agent")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_NAME = "gemini-3.5-flash-lite"

# Load prompt template and KB articles once at startup
_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.txt")
with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

_KB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "AI_Engineering_Task0_Assets", "kb_articles.json"
)
with open(_KB_PATH, "r", encoding="utf-8") as f:
    _kb_data = json.load(f)

KB_ARTICLES_TEXT = "\n".join(
    f"[Article {a['id']}] {a['text']}" for a in _kb_data["articles"]
)


import time
from google.genai import errors as genai_errors

def get_decision(short_description: str, description: str, max_retries: int = 3) -> dict:
    """
    Calls Gemini with the ticket text + KB articles.
    Returns a dict: {"decision": "respond"|"ask"|"escalate", "message": str}
    Retries on transient server errors (503). Falls back to "escalate"
    if Gemini's response can't be parsed or all retries are exhausted.
    """
    prompt = PROMPT_TEMPLATE.format(
        kb_articles=KB_ARTICLES_TEXT,
        short_description=short_description,
        description=description or "(no additional description provided)",
    )

    raw_text = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            raw_text = response.text.strip()
            break
        except genai_errors.ServerError as e:
            logger.warning(f"Gemini server error (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(2 * attempt)  # 2s, 4s, ... simple backoff
            else:
                logger.error("Gemini unavailable after retries; escalating by default.")
                return {
                    "decision": "escalate",
                    "message": "AI service temporarily unavailable; escalated for manual review.",
                }

    # Defensive cleanup in case Gemini wraps output in markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        parsed = json.loads(raw_text)
        decision = parsed.get("decision")
        message = parsed.get("message", "")
        if decision not in ("respond", "ask", "escalate"):
            raise ValueError(f"Invalid decision value: {decision}")
        return {"decision": decision, "message": message}
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse Gemini response: {raw_text!r} — error: {e}")
        return {
            "decision": "escalate",
            "message": "Could not automatically process this ticket; escalated for manual review.",
        }