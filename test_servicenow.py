from dotenv import load_dotenv
load_dotenv()

from app.servicenow_client import write_respond, write_ask, write_escalate

# Replace these with real sys_ids from incidents you created in the PDI
RESPOND_SYS_ID = "ebb273fac34b0b10180b78edd40131a7"
ASK_SYS_ID = "9d9337b2c38b0b10180b78edd40131fd"
ESCALATE_SYS_ID = "10b6377ec38b0b10180b78edd40131e5"

print("Testing respond...")
print(write_respond(RESPOND_SYS_ID, "Restart the printer and unplug the cable for 30 seconds."))

print("Testing ask...")
print(write_ask(ASK_SYS_ID, "Could you share any error messages you're seeing?"))

print("Testing escalate...")
print(write_escalate(ESCALATE_SYS_ID, "No knowledge base article covers this request."))