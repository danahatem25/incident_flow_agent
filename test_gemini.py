from dotenv import load_dotenv
load_dotenv()

from app.gemini_client import get_decision
import time


test_cases = [
    {
        "short_description": "Printer not printing after office move",
        "description": "It was working yesterday. I tried turning it off and on.",
        "expected": "respond",
    },
    {
        "short_description": "Cannot send email",
        "description": "It just doesn't work.",
        "expected": "ask",
    },
    {
        "short_description": "Request: annual leave approval",
        "description": "I would like to take next week off.",
        "expected": "escalate",
    },
]

for case in test_cases:
    result = get_decision(case["short_description"], case["description"])
    status = "✅ PASS" if result["decision"] == case["expected"] else "❌ FAIL"
    print(f"{status} — expected: {case['expected']}, got: {result['decision']}")
    print(f"   message: {result['message']}\n")
    time.sleep(4)