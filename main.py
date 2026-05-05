from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json

from services.lead_scoring import score_lead
from services.events import log_event
from services.routing import route_lead
from services.jobtread import sync_lead_to_jobtread

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Lead(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    message: str


@app.get("/")
def home():
    return {"status": "API running"}


@app.post("/lead")
def create_lead(lead: Lead):
    lead_data = lead.dict()
    lead_data["created_at"] = datetime.now().isoformat()

    # ------------------------
    # Lead scoring
    # ------------------------
    lead_data["qualification"] = score_lead(lead)

    # ------------------------
    # Routing logic
    # ------------------------
    route = route_lead(lead_data)
    lead_data["route"] = route

    # ------------------------
    # JobTread sync (stub)
    # ------------------------
    jobtread_sync = sync_lead_to_jobtread(lead_data)
    lead_data["jobtread_sync"] = jobtread_sync

    # ------------------------
    # Event logging
    # ------------------------
    event = log_event("NEW_LEAD", {
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "priority": lead_data["qualification"]["priority"],
        "score": lead_data["qualification"]["score"],
        "action": route["action"]
    })

    # ------------------------
    # Save lead
    # ------------------------
    with open("leads.json", "a") as f:
        f.write(json.dumps(lead_data) + "\n")

    return {
        "status": "lead stored",
        "lead": lead_data,
        "event": event,
        "jobtread_sync": jobtread_sync
    }