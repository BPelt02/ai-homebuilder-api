from datetime import datetime
import json
import requests

ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/27469070/uvnc2cb/"

def sync_lead_to_jobtread(lead_data):
    payload = {
        "name": lead_data["name"],
        "phone": lead_data.get("phone"),
        "email": lead_data.get("email"),
        "message": lead_data["message"],
        "score": lead_data["qualification"]["score"],
        "priority": lead_data["qualification"]["priority"],
        "route_action": lead_data["route"]["action"],
        "source": "AI Homebuilder API",
        "synced_at": datetime.now().isoformat()
    }

    with open("jobtread_sync_log.json", "a") as f:
        f.write(json.dumps(payload) + "\n")

    response = requests.post(ZAPIER_WEBHOOK_URL, json=payload, timeout=10)

    return {
        "status": "sent_to_zapier",
        "zapier_status_code": response.status_code,
        "payload": payload
    }