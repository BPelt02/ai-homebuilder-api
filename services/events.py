from datetime import datetime
import json

def log_event(event_type, data):
    event = {
        "type": event_type,
        "data": data,
        "created_at": datetime.now().isoformat()
    }

    with open("events.json", "a") as f:
        f.write(json.dumps(event) + "\n")

    return event